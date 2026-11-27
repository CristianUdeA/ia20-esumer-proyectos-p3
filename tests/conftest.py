"""Aislamiento global: las pruebas no deben crear clientes cloud ni usar red."""

import socket

import pytest


_socket_connect = socket.socket.connect


def _forbid_external_client(*args, **kwargs):
    raise AssertionError("A local test attempted to create an external client")


def _forbid_non_local_socket_connect(sock, address):
    host = address[0] if isinstance(address, tuple) else address
    if host in {"127.0.0.1", "::1", "localhost"}:
        return _socket_connect(sock, address)
    raise AssertionError("A local test attempted an external network connection")


@pytest.fixture(autouse=True)
def forbid_cloud_clients_and_network(monkeypatch):
    """Reemplaza clientes de Google y conexiones de red por centinelas."""
    monkeypatch.setattr(socket, "create_connection", _forbid_external_client)
    monkeypatch.setattr(socket.socket, "connect", _forbid_non_local_socket_connect)

    import google.genai
    from google.cloud import secretmanager, storage

    monkeypatch.setattr(google.genai, "Client", _forbid_external_client)
    monkeypatch.setattr(storage, "Client", _forbid_external_client)
    monkeypatch.setattr(
        secretmanager.SecretManagerServiceClient,
        "__init__",
        _forbid_external_client,
    )
