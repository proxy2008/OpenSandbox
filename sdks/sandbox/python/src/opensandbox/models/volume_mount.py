#
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
Volume mount model for OpenSandbox SDK.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class VolumeMount(BaseModel):
    """
    Volume mount specification for binding host paths into the sandbox.

    Allows mounting files or directories from the host into the sandbox container.
    Similar to Docker's --volume or -v flag.

    Security Note: Volume mounts bypass container isolation. Only mount trusted directories.

    Attributes:
        host_path: Absolute path on the host filesystem to mount from.
            Relative paths will be resolved against the server's current working directory.
        container_path: Absolute path inside the container where the volume will be mounted.
        read_only: Mount the volume as read-only (write access is prohibited).

    Example:
        ```python
        # Mount host directory as read-write
        mount = VolumeMount(
            host_path="/host/workspace",
            container_path="/workspace",
            read_only=False
        )

        # Mount config directory as read-only
        config_mount = VolumeMount(
            host_path="./config",
            container_path="/app/config",
            read_only=True
        )
        ```
    """

    host_path: str = Field(
        ...,
        description="Absolute path on the host filesystem to mount from",
        examples=["/host/data", "./local-dir", "/tmp/workspace"],
        json_schema_extra={"alias": "hostPath"},
    )
    container_path: str = Field(
        ...,
        description="Absolute path inside the container where the volume will be mounted",
        examples=["/data", "/workspace", "/app/config"],
        json_schema_extra={"alias": "containerPath"},
    )
    read_only: bool = Field(
        False,
        description="Mount the volume as read-only (write access is prohibited)",
        json_schema_extra={"alias": "readOnly"},
    )

    @field_validator('host_path')
    @classmethod
    def validate_host_path(cls, v: str) -> str:
        """Validate that host_path is not empty."""
        if not v or not v.strip():
            raise ValueError("host_path cannot be empty")
        return v

    @field_validator('container_path')
    @classmethod
    def validate_container_path(cls, v: str) -> str:
        """Validate that container_path is absolute and not empty."""
        if not v or not v.strip():
            raise ValueError("container_path cannot be empty")
        if not v.startswith('/'):
            raise ValueError("container_path must be an absolute path starting with '/'")
        return v

    model_config = {"populate_by_name": True}

    def to_api_format(self) -> dict[str, Any]:
        """Convert to API request format."""
        return {
            "hostPath": self.host_path,
            "containerPath": self.container_path,
            "readOnly": self.read_only,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VolumeMount":
        """Create from API response format."""
        return cls(
            host_path=data.get("hostPath", data.get("host_path", "")),
            container_path=data.get("containerPath", data.get("container_path", "")),
            read_only=data.get("readOnly", data.get("read_only", False)),
        )
