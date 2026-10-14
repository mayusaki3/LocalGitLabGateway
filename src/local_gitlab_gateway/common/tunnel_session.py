"""Track the single currently attached reverse tunnel socket."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TunnelSession:
    """A single active connection; ownership is checked when detaching."""

    socket: Any | None = field(default=None, repr=False)

    @property
    def connected(self) -> bool:
        return self.socket is not None

    def attach(self, socket: Any) -> bool:
        if self.connected:
            return False
        self.socket = socket
        return True

    def detach(self, socket: Any) -> None:
        if self.socket is socket:
            self.socket = None

    def require_socket(self) -> Any:
        if self.socket is None:
            raise RuntimeError("Tunnel unavailable")
        return self.socket
