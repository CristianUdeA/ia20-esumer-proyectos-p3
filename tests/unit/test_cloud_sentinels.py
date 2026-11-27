import google.genai
from google.cloud import secretmanager, storage
import pytest


def test_local_suite_replaces_all_google_client_constructors():
    with pytest.raises(AssertionError):
        google.genai.Client()
    with pytest.raises(AssertionError):
        storage.Client()
    with pytest.raises(AssertionError):
        secretmanager.SecretManagerServiceClient()


def test_local_suite_blocks_non_loopback_network_connections():
    sock = __import__("socket").socket()
    try:
        with pytest.raises(AssertionError):
            sock.connect(("203.0.113.1", 443))
    finally:
        sock.close()
