"""Operator-controlled lifecycle for an outbound WebSocket tunnel."""

from dataclasses import dataclass
from enum import Enum


class TunnelState(str, Enum):
    DISABLED = "disabled"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECT_WAIT = "reconnect_wait"


@dataclass
class TunnelLifecycle:
    state: TunnelState = TunnelState.DISABLED

    @property
    def should_connect(self) -> bool:
        return self.state is not TunnelState.DISABLED

    def enable(self) -> None:
        if self.state is TunnelState.DISABLED:
            self.state = TunnelState.CONNECTING

    def connected(self) -> None:
        if self.state is not TunnelState.CONNECTING:
            raise RuntimeError("Tunnel connection was not requested")
        self.state = TunnelState.CONNECTED

    def disconnected(self) -> None:
        if self.should_connect:
            self.state = TunnelState.RECONNECT_WAIT

    def retry(self) -> None:
        if self.state is not TunnelState.RECONNECT_WAIT:
            raise RuntimeError("Tunnel is not waiting for reconnect")
        self.state = TunnelState.CONNECTING

    def disable(self) -> None:
        self.state = TunnelState.DISABLED
