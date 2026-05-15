"""Runtime configuration loaders."""

from pathlib import Path
from typing import Any

import yaml


PUBLIC_GATEWAY_CONFIG_PATH = Path(
    "/opt/local-gitlab-gateway/runtime/public_gateway/config.yaml",
)

PRIVATE_BRIDGE_CONFIG_PATH = Path(
    "/opt/local-gitlab-gateway/runtime/private_bridge/config.yaml",
)


class ConfigError(RuntimeError):
    """Raised when runtime configuration is invalid."""



def load_yaml_config(path: Path) -> dict[str, Any]:
    """Load YAML configuration.

    Args:
        path: YAML file path.

    Returns:
        dict[str, Any]: Parsed YAML.

    Raises:
        ConfigError: Configuration is missing or invalid.
    """

    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        loaded = yaml.safe_load(file)

    if not isinstance(loaded, dict):
        raise ConfigError(f"Invalid config structure: {path}")

    return loaded


def load_public_gateway_config() -> dict[str, Any]:
    """Load public gateway runtime configuration."""

    return load_yaml_config(PUBLIC_GATEWAY_CONFIG_PATH)



def load_private_bridge_config() -> dict[str, Any]:
    """Load private bridge runtime configuration."""

    return load_yaml_config(PRIVATE_BRIDGE_CONFIG_PATH)
