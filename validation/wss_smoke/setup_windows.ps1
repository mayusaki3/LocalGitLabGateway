# Windows local WSS smoke test (PowerShell 7 or Windows PowerShell 5.1)
# Requires mkcert installed and its local CA trusted (mkcert -install).
# Run from the repository root. Never use production credentials.
$ErrorActionPreference = "Stop"
$root = (Get-Location).Path
$python = Join-Path $root ".venv\Scripts\python.exe"
if (!(Test-Path $python)) { throw "Run this script from the repository root after installing .venv" }
if (!(Get-Command mkcert -ErrorAction SilentlyContinue)) {
    throw "mkcert is required. Install it and run 'mkcert -install' before retrying."
}
$work = Join-Path $env:TEMP "lgg-wss-smoke"
New-Item -ItemType Directory -Path $work -Force | Out-Null
$cert = Join-Path $work "localhost.pem"
$key = Join-Path $work "localhost-key.pem"
& mkcert -cert-file $cert -key-file $key localhost 127.0.0.1
if ($LASTEXITCODE -ne 0) { throw "mkcert failed" }

$public = Join-Path $work "public.yaml"
$private = Join-Path $work "private.yaml"
@"
security:
  api_key: local-public-key
private_bridge:
  base_url: http://127.0.0.1:8081
  internal_api_key: local-internal-key
tunnel:
  token: local-tunnel-token
"@ | Set-Content -Encoding UTF8 $public
@"
security:
  internal_api_key: local-internal-key
gitlab:
  base_url: http://127.0.0.1:8090
  personal_access_token: local-mock-pat
"@ | Set-Content -Encoding UTF8 $private

# Explicitly pass the trusted local CA to the Python WSS client.
$caRoot = (& mkcert -CAROOT).Trim()
$ca = Join-Path $caRoot "rootCA.pem"
if (!(Test-Path $ca)) { throw "mkcert rootCA.pem not found" }

Write-Host "Start each command in its own PowerShell window, from repo root:"
Write-Host ""
Write-Host "1. Mock GitLab:"
Write-Host "   & '$python' -m uvicorn validation.wss_smoke.mock_gitlab:app --host 127.0.0.1 --port 8090"
Write-Host ""
Write-Host "2. Private Bridge:"
Write-Host "   `$env:LGG_PRIVATE_CONFIG = '$private'"
Write-Host "   & '$python' -m uvicorn local_gitlab_gateway.private_bridge.main:app --host 127.0.0.1 --port 8081"
Write-Host ""
Write-Host "3. TLS Public Gateway:"
Write-Host "   `$env:LGG_PUBLIC_CONFIG = '$public'"
Write-Host "   & '$python' -m uvicorn local_gitlab_gateway.public_gateway.main:app --host 127.0.0.1 --port 8443 --ssl-certfile '$cert' --ssl-keyfile '$key'"
Write-Host ""
Write-Host "4. On-demand tunnel worker (start AFTER verifying disconnected response):"
Write-Host "   `$env:LGG_TUNNEL_WSS_URL = 'wss://localhost:8443/internal/tunnel/v1'"
Write-Host "   `$env:LGG_TUNNEL_TOKEN = 'local-tunnel-token'"
Write-Host "   `$env:LGG_PRIVATE_BRIDGE_URL = 'http://127.0.0.1:8081'"
Write-Host "   `$env:LGG_INTERNAL_API_KEY = 'local-internal-key'"
Write-Host "   `$env:SSL_CERT_FILE = '$ca'"
Write-Host "   & '$python' -m local_gitlab_gateway.private_bridge.tunnel_worker"
Write-Host ""
Write-Host "5. Verify from another PowerShell window:"
Write-Host "   `$headers = @{ Authorization = 'Bearer local-public-key' }"
Write-Host "   Invoke-RestMethod 'https://localhost:8443/api/v1/projects?page=2&per_page=5' -Headers `$headers"
Write-Host ""
Write-Host "Expected before worker: HTTP 503. With worker: projects[0].id=42 and page=2."
Write-Host "Stop worker with Ctrl+C, then repeat request to confirm HTTP 503."
Write-Host "Do not commit the files in $work."
