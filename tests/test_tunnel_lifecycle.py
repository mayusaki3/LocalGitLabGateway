"""Unit tests for the opt-in reverse tunnel lifecycle."""

from local_gitlab_gateway.common.tunnel_lifecycle import TunnelLifecycle, TunnelState


def test_initially_disabled() -> None:
    tunnel = TunnelLifecycle()
    assert tunnel.state is TunnelState.DISABLED
    assert not tunnel.should_connect


def test_enable_connect_and_disable() -> None:
    tunnel = TunnelLifecycle()
    tunnel.enable()
    assert tunnel.state is TunnelState.CONNECTING
    assert tunnel.should_connect
    tunnel.connected()
    assert tunnel.state is TunnelState.CONNECTED
    tunnel.disable()
    assert tunnel.state is TunnelState.DISABLED
    assert not tunnel.should_connect


def test_disconnect_only_reconnects_when_enabled() -> None:
    tunnel = TunnelLifecycle()
    tunnel.enable()
    tunnel.connected()
    tunnel.disconnected()
    assert tunnel.state is TunnelState.RECONNECT_WAIT
    assert tunnel.should_connect
    tunnel.retry()
    assert tunnel.state is TunnelState.CONNECTING
    tunnel.disable()
    tunnel.disconnected()
    assert tunnel.state is TunnelState.DISABLED
    assert not tunnel.should_connect


def test_duplicate_enable_does_not_restart_connection() -> None:
    tunnel = TunnelLifecycle()
    tunnel.enable()
    tunnel.enable()
    assert tunnel.state is TunnelState.CONNECTING


def test_invalid_connected_transition_rejected() -> None:
    tunnel = TunnelLifecycle()
    try:
        tunnel.connected()
    except RuntimeError:
        pass
    else:
        raise AssertionError("connected() must reject a disabled tunnel")


def test_retry_only_allowed_while_waiting() -> None:
    tunnel = TunnelLifecycle()
    try:
        tunnel.retry()
    except RuntimeError:
        pass
    else:
        raise AssertionError("retry() must reject disabled tunnel")


def test_disconnect_during_connecting_waits_for_retry() -> None:
    tunnel = TunnelLifecycle()
    tunnel.enable()
    tunnel.disconnected()
    assert tunnel.state is TunnelState.RECONNECT_WAIT


def test_disable_is_idempotent() -> None:
    tunnel = TunnelLifecycle()
    tunnel.disable()
    assert tunnel.state is TunnelState.DISABLED
