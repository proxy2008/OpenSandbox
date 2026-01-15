#!/usr/bin/env python3
"""
Manual integration test for volume mounts functionality.

This script tests creating a sandbox with a volume mount and listing
the mounted directory contents inside the container.
"""

import requests
import json
import time

# Server configuration
SERVER_URL = "http://172.32.153.182:18888"
API_KEY = "test-api-key-12345"  # From test config

# Directory to mount (local path)
HOST_PATH = "/Volumes/Terry/code/python/OpenSandbox/tests/python"

# Container path where it will be mounted
CONTAINER_PATH = "/mounted_tests"


def create_sandbox_with_volume_mount():
    """Create a sandbox with volume mount"""
    url = f"{SERVER_URL}/v1/sandboxes"

    headers = {
        "OPEN-SANDBOX-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    request_data = {
        "image": {
            "uri": "python:3.11-slim"
        },
        "timeout": 600,
        "resourceLimits": {
            "cpu": "500m",
            "memory": "512Mi"
        },
        "env": {},
        "metadata": {
            "test": "volume-mount-manual-test"
        },
        "entrypoint": ["sleep", "600"],
        "volumeMounts": [
            {
                "hostPath": HOST_PATH,
                "containerPath": CONTAINER_PATH,
                "readOnly": False
            }
        ]
    }

    print(f"🚀 Creating sandbox with volume mount...")
    print(f"   Host path: {HOST_PATH}")
    print(f"   Container path: {CONTAINER_PATH}")

    response = requests.post(url, headers=headers, json=request_data)

    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        sandbox_id = data.get("id")
        print(f"✅ Sandbox created successfully!")
        print(f"   Sandbox ID: {sandbox_id}")
        return sandbox_id
    else:
        print(f"❌ Failed to create sandbox")
        print(f"   Status code: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def test_volume_mount_in_container(sandbox_id):
    """Test that volume mount is accessible inside container"""
    import docker

    print(f"\n⏳ Waiting for container to be ready...")
    time.sleep(3)

    try:
        # Get Docker client
        client = docker.from_env()

        # Get the container
        container_name = f"sandbox-{sandbox_id}"
        print(f"🔍 Looking for container: {container_name}")

        # Try to find the container
        containers = client.containers.list(all=True)
        sandbox_container = None

        for container in containers:
            if sandbox_id in container.name:
                sandbox_container = container
                print(f"✅ Found container: {container.name}")
                break

        if not sandbox_container:
            print(f"❌ Container not found. Listing all containers:")
            for container in containers:
                print(f"   - {container.name}")
            return False

        # Execute ls command in the container
        print(f"\n📂 Listing directory {CONTAINER_PATH} in container...")
        exit_code, output = sandbox_container.exec_run(f"ls -la {CONTAINER_PATH}")

        output_str = output.decode('utf-8')
        print(f"\n{'='*60}")
        print(f"Directory listing of {CONTAINER_PATH}:")
        print(f"{'='*60}")
        print(output_str)
        print(f"{'='*60}")

        if exit_code == 0:
            print(f"✅ Volume mount is working! Directory is accessible.")

            # Try to list files recursively
            print(f"\n📂 Recursive directory listing...")
            exit_code_recursive, output_recursive = sandbox_container.exec_run(f"ls -R {CONTAINER_PATH}")
            output_recursive_str = output_recursive.decode('utf-8')
            print(f"\n{'='*60}")
            print("Recursive listing:")
            print(f"{'='*60}")
            print(output_recursive_str)
            print(f"{'='*60}")

            return True
        else:
            print(f"❌ Failed to list directory")
            print(f"   Exit code: {exit_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def delete_sandbox(sandbox_id):
    """Delete the sandbox"""
    url = f"{SERVER_URL}/v1/sandboxes/{sandbox_id}"
    headers = {
        "OPEN-SANDBOX-API-KEY": API_KEY
    }

    print(f"\n🧹 Cleaning up sandbox {sandbox_id}...")
    response = requests.delete(url, headers=headers)

    if response.status_code == 200 or response.status_code == 204:
        print(f"✅ Sandbox deleted successfully")
    else:
        print(f"⚠️  Failed to delete sandbox: {response.status_code}")


def main():
    """Main test flow"""
    print("="*60)
    print("Volume Mounts Integration Test")
    print("="*60)
    print(f"Server: {SERVER_URL}")
    print(f"Mounting: {HOST_PATH} -> {CONTAINER_PATH}")
    print("="*60)

    sandbox_id = None
    try:
        # Step 1: Create sandbox with volume mount
        sandbox_id = create_sandbox_with_volume_mount()

        if not sandbox_id:
            print("\n❌ Test failed: Could not create sandbox")
            return

        # Step 2: Test volume mount in container
        success = test_volume_mount_in_container(sandbox_id)

        if success:
            print(f"\n{'='*60}")
            print("✅ TEST PASSED!")
            print(f"{'='*60}")
            print(f"Volume mount is working correctly.")
            print(f"The directory {HOST_PATH} was successfully mounted")
            print(f"to {CONTAINER_PATH} inside the container.")
        else:
            print(f"\n{'='*60}")
            print("❌ TEST FAILED!")
            print(f"{'='*60}")

    finally:
        # Cleanup
        if sandbox_id:
            delete_sandbox(sandbox_id)


if __name__ == "__main__":
    main()
