# Copyright 2025 Alibaba Group Holding Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Pytest configuration and fixtures for sandbox server tests.

This module provides shared fixtures and configuration for all test modules.
"""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

TEST_CONFIG_PATH = Path(__file__).resolve().parent / "testdata" / "config.toml"
os.environ.setdefault("SANDBOX_CONFIG_PATH", str(TEST_CONFIG_PATH))

# Prevent real Docker connections during tests by mocking docker.from_env
import docker  # noqa: E402

_mock_docker_client = MagicMock()
_mock_docker_client.containers.list.return_value = []
docker.from_env = lambda: _mock_docker_client  # type: ignore

from src.main import app  # noqa: E402


def pytest_configure(config):
    """
    Configure pytest with custom markers.
    """
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require Docker)"
    )


@pytest.fixture(scope="session")
def test_api_key() -> str:
    """
    Fixture providing a test API key (matches test configuration file).
    """
    return "test-api-key-12345"


@pytest.fixture(scope="function")
def client() -> TestClient:
    """
    Fixture providing a FastAPI test client.
    """
    return TestClient(app)


@pytest.fixture(scope="function")
def auth_headers(test_api_key: str) -> dict:
    """
    Fixture providing authentication headers.
    """
    return {"OPEN-SANDBOX-API-KEY": test_api_key}


@pytest.fixture(scope="session")
def sample_sandbox_request() -> dict:
    """
    Fixture providing a sample sandbox creation request.
    """
    return {
        "image": {"uri": "python:3.11"},
        "timeout": 3600,
        "resourceLimits": {"cpu": "500m", "memory": "512Mi"},
        "env": {"DEBUG": "true", "LOG_LEVEL": "info"},
        "metadata": {"name": "Test Sandbox", "project": "test-project"},
        "entrypoint": ["python", "-c", "print('Hello from sandbox')"],
    }


@pytest.fixture(scope="session")
def docker_config():
    """
    Fixture providing Docker configuration for integration tests.

    This fixture loads a real Docker configuration for integration tests.
    """
    from src.config import AppConfig

    config_path = Path(__file__).resolve().parent / "testdata" / "config.toml"
    return AppConfig.from_file(str(config_path))


@pytest.fixture(scope="function")
def docker_service(docker_config):
    """
    Fixture providing a real DockerSandboxService for integration tests.

    This fixture creates an actual Docker connection and should only be used
    with tests marked as @pytest.mark.integration
    """
    # Undo the mock for integration tests
    import docker as real_docker
    real_docker.from_env = real_docker.from_env.__wrapped__ if hasattr(
        real_docker.from_env, '__wrapped__'
    ) else real_docker.from_env

    from src.services.docker import DockerSandboxService

    service = DockerSandboxService(config=docker_config)

    yield service

    # Cleanup: don't do anything here, tests should clean up their own sandboxes
