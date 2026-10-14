"""Single active tunnel session tests."""

import pytest

from local_gitlab_gateway.common.tunnel_session import TunnelSession


def test_initially_disconnected() -> None:
    session = TunnelSession()
    assert not session.connected


def test_attach_and_detach() -> None:
    session = TunnelSession()
    socket = object()
    assert session.attach(socket)
    assert session.connected
    assert session.socket is socket
    session.detach(socket)
    assert not session.connected


def test_second_connection_rejected() -> None:
    session = TunnelSession()
    assert session.attach(object())
    assert not session.attach(object())


def test_stale_detach_does_not_remove_active_connection() -> None:
    session = TunnelSession()
    socket = object()
    session.attach(socket)
    session.detach(object())
    assert session.socket is socket


def test_send_requires_connection() -> None:
    session = TunnelSession()
    with pytest.raises(RuntimeError):
        session.require_socket()
