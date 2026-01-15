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
Integration tests for volume mounts functionality.

These tests require Docker to be running and create actual containers.
They are marked as integration tests and can be skipped during normal test runs.
"""

import os
import tempfile
import time
import pytest
from pathlib import Path

from src.api.schema import (
    CreateSandboxRequest,
    ImageSpec,
    ResourceLimits,
    VolumeMount,
)


@pytest.mark.integration
class TestVolumeMountsIntegration:
    """Integration tests for volume mounts with actual Docker containers"""

    def test_create_sandbox_with_volume_mount_and_list_contents(
        self, docker_service
    ):
        """
        Test case: Create sandbox with volume mount and list directory contents

        Purpose: Verify that:
        1. A local directory can be mounted into a sandbox container
        2. The mounted directory is accessible inside the container
        3. Files in the mounted directory are visible via 'ls' command

        This is an integration test that requires actual Docker runtime.
        """
        # Create a temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files in the temporary directory
            test_file1 = Path(temp_dir) / "test_file_1.txt"
            test_file2 = Path(temp_dir) / "test_file_2.txt"
            test_subdir = Path(temp_dir) / "subdirectory"

            test_file1.write_text("Hello from file 1")
            test_file2.write_text("Hello from file 2")
            test_subdir.mkdir()

            # Create a file in the subdirectory
            (test_subdir / "nested_file.txt").write_text("Nested content")

            # Create sandbox request with volume mount
            request = CreateSandboxRequest(
                image=ImageSpec(uri="python:3.11-slim"),
                timeout=300,
                resourceLimits=ResourceLimits(root={}),
                env={},
                metadata={"test": "volume-mount-integration"},
                entrypoint=["sleep", "300"],  # Keep container running
                volumeMounts=[
                    VolumeMount(
                        host_path=temp_dir,
                        container_path="/mounted_data",
                        read_only=False,
                    ),
                ],
            )

            # Create the sandbox
            response = docker_service.create_sandbox(request)
            sandbox_id = response.id

            try:
                # Wait a moment for the container to be fully ready
                time.sleep(2)

                # Get the container
                from src.services.docker import DockerSandboxService
                container = docker_service._docker_client.containers.get(sandbox_id)

                # Execute ls command in the container to list mounted directory
                exit_code, output = container.exec_run(
                    "ls -la /mounted_data"
                )

                output_str = output.decode('utf-8')
                print(f"\n=== Directory listing of /mounted_data ===")
                print(output_str)
                print("=" * 50)

                # Verify the command succeeded
                assert exit_code == 0, f"ls command failed: {output_str}"

                # Verify test files are present
                assert "test_file_1.txt" in output_str, "test_file_1.txt not found in ls output"
                assert "test_file_2.txt" in output_str, "test_file_2.txt not found in ls output"
                assert "subdirectory" in output_str, "subdirectory not found in ls output"

                # Also verify using ls -R to show nested files
                exit_code_recursive, output_recursive = container.exec_run(
                    "ls -R /mounted_data"
                )
                output_recursive_str = output_recursive.decode('utf-8')
                print(f"\n=== Recursive directory listing ===")
                print(output_recursive_str)
                print("=" * 50)

                assert exit_code_recursive == 0
                assert "nested_file.txt" in output_recursive_str, "nested_file.txt not found"

                # Test reading a file from the mounted directory
                exit_code_cat, output_cat = container.exec_run(
                    "cat /mounted_data/test_file_1.txt"
                )
                file_content = output_cat.decode('utf-8').strip()
                print(f"\n=== Content of test_file_1.txt ===")
                print(file_content)
                print("=" * 50)

                assert exit_code_cat == 0
                assert file_content == "Hello from file 1", f"Unexpected file content: {file_content}"

                print("\n✅ Volume mount integration test passed!")

            finally:
                # Clean up: delete the sandbox
                try:
                    docker_service.delete_sandbox(sandbox_id)
                    print(f"\n✅ Cleaned up sandbox {sandbox_id}")
                except Exception as e:
                    print(f"\n⚠️  Failed to cleanup sandbox {sandbox_id}: {e}")

    def test_create_sandbox_with_read_only_volume_mount(self, docker_service):
        """
        Test case: Create sandbox with read-only volume mount

        Purpose: Verify that read-only mounts prevent write operations
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = Path(temp_dir) / "readonly.txt"
            test_file.write_text("This is read-only")

            request = CreateSandboxRequest(
                image=ImageSpec(uri="python:3.11-slim"),
                timeout=300,
                resourceLimits=ResourceLimits(root={}),
                env={},
                metadata={"test": "readonly-volume-mount"},
                entrypoint=["sleep", "300"],
                volumeMounts=[
                    VolumeMount(
                        host_path=temp_dir,
                        container_path="/readonly_data",
                        read_only=True,
                    ),
                ],
            )

            response = docker_service.create_sandbox(request)
            sandbox_id = response.id

            try:
                time.sleep(2)

                container = docker_service._docker_client.containers.get(sandbox_id)

                # Try to write to the read-only mount (should fail)
                exit_code, output = container.exec_run(
                    "echo 'test write' > /readonly_data/new_file.txt"
                )

                # The write should fail due to read-only mount
                assert exit_code != 0, "Write to read-only mount should have failed"

                print("\n✅ Read-only volume mount test passed!")

            finally:
                try:
                    docker_service.delete_sandbox(sandbox_id)
                except Exception as e:
                    print(f"\n⚠️  Failed to cleanup sandbox {sandbox_id}: {e}")

    def test_create_sandbox_with_multiple_volume_mounts(self, docker_service):
        """
        Test case: Create sandbox with multiple volume mounts

        Purpose: Verify that multiple directories can be mounted simultaneously
        """
        with tempfile.TemporaryDirectory() as temp_dir1, \
             tempfile.TemporaryDirectory() as temp_dir2:

            # Create files in both directories
            (Path(temp_dir1) / "dir1_file.txt").write_text("Content from dir1")
            (Path(temp_dir2) / "dir2_file.txt").write_text("Content from dir2")

            request = CreateSandboxRequest(
                image=ImageSpec(uri="python:3.11-slim"),
                timeout=300,
                resourceLimits=ResourceLimits(root={}),
                env={},
                metadata={"test": "multiple-volume-mounts"},
                entrypoint=["sleep", "300"],
                volumeMounts=[
                    VolumeMount(
                        host_path=temp_dir1,
                        container_path="/data1",
                        read_only=False,
                    ),
                    VolumeMount(
                        host_path=temp_dir2,
                        container_path="/data2",
                        read_only=False,
                    ),
                ],
            )

            response = docker_service.create_sandbox(request)
            sandbox_id = response.id

            try:
                time.sleep(2)

                container = docker_service._docker_client.containers.get(sandbox_id)

                # List both directories
                exit_code1, output1 = container.exec_run("ls /data1")
                exit_code2, output2 = container.exec_run("ls /data2")

                output1_str = output1.decode('utf-8')
                output2_str = output2.decode('utf-8')

                print(f"\n=== Contents of /data1 ===")
                print(output1_str)
                print(f"\n=== Contents of /data2 ===")
                print(output2_str)
                print("=" * 50)

                assert exit_code1 == 0
                assert exit_code2 == 0
                assert "dir1_file.txt" in output1_str
                assert "dir2_file.txt" in output2_str

                print("\n✅ Multiple volume mounts test passed!")

            finally:
                try:
                    docker_service.delete_sandbox(sandbox_id)
                except Exception as e:
                    print(f"\n⚠️  Failed to cleanup sandbox {sandbox_id}: {e}")


if __name__ == "__main__":
    """
    Run this test file directly with:
    cd server
    pytest tests/test_volume_mounts_integration.py -v -s
    """
    pytest.main([__file__, "-v", "-s", "-m", "integration"])
