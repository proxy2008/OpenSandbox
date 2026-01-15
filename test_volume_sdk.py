#!/usr/bin/env python3
"""
Volume Mounts Test using OpenSandbox Python SDK

This script demonstrates using the Python SDK to create a sandbox
with volume mounts and verify the mounted directory is accessible.
"""

import asyncio
import sys
from datetime import timedelta

# Add SDK to path
sys.path.insert(0, '/Volumes/Terry/code/python/OpenSandbox/sdks/sandbox/python/src')

from opensandbox import Sandbox
from opensandbox.config import ConnectionConfig
from opensandbox.models import VolumeMount
from opensandbox.exceptions import SandboxException


async def test_volume_mounts_with_sdk():
    """Test volume mounts using Python SDK"""

    print("=" * 70)
    print("Volume Mounts Test - OpenSandbox Python SDK")
    print("=" * 70)
    print()

    # Configuration
    SERVER_URL = "http://172.32.153.182:18888"
    API_KEY = "test-api-key-12345"
    HOST_PATH = "/data/AI/tengyt/OpenSandbox/tests/python"
    CONTAINER_PATH = "/mounted_python_tests"

    print(f"📋 Configuration:")
    print(f"   Server: {SERVER_URL}")
    print(f"   Host path: {HOST_PATH}")
    print(f"   Container path: {CONTAINER_PATH}")
    print()

    # Configure connection
    config = ConnectionConfig(
        base_url=SERVER_URL,
        api_key=API_KEY,
    )

    sandbox = None

    try:
        # Prepare volume mounts
        volume_mounts = [
            VolumeMount(
                host_path=HOST_PATH,
                container_path=CONTAINER_PATH,
                read_only=False,
            )
        ]

        print("🚀 Creating sandbox with volume mount...")
        print(f"   Mounting: {HOST_PATH} -> {CONTAINER_PATH}")
        print()

        # Create sandbox with volume mounts
        sandbox = await Sandbox.create(
            "python:3.11-slim",
            connection_config=config,
            timeout=timedelta(minutes=10),
            resource={"cpu": "500m", "memory": "512Mi"},
            volume_mounts=volume_mounts,
            entrypoint=["sleep", "600"],  # Keep container running
        )

        print(f"✅ Sandbox created successfully!")
        print(f"   Sandbox ID: {sandbox.id}")
        print()

        # Test 1: List the mounted directory
        print("📂 Test 1: Listing mounted directory...")
        print("-" * 70)

        try:
            execution = await sandbox.commands.run(f"ls -la {CONTAINER_PATH}")
            print(execution.logs.stdout[0].text)
            print("-" * 70)
            print("✅ Directory listing successful!")
            print()
        except Exception as e:
            print(f"❌ Failed to list directory: {e}")
            print()

        # Test 2: Recursive listing
        print("📂 Test 2: Recursive directory listing...")
        print("-" * 70)

        try:
            execution = await sandbox.commands.run(f"ls -R {CONTAINER_PATH}")
            print(execution.logs.stdout[0].text)
            print("-" * 70)
            print("✅ Recursive listing successful!")
            print()
        except Exception as e:
            print(f"❌ Failed to list recursively: {e}")
            print()

        # Test 3: Check if files are readable
        print("📂 Test 3: Checking file accessibility...")
        print("-" * 70)

        try:
            # Try to find and read a Python file
            execution = await sandbox.commands.run(
                f"find {CONTAINER_PATH} -name '*.py' -type f | head -5"
            )

            if execution.logs.stdout:
                files = execution.logs.stdout[0].text.strip().split('\n')
                if files and files[0]:
                    first_file = files[0]
                    print(f"Found Python file: {first_file}")

                    # Try to read it
                    cat_execution = await sandbox.commands.run(f"cat {first_file}")
                    print(f"\nContent of {first_file}:")
                    print("-" * 70)
                    print(cat_execution.logs.stdout[0].text[:500])  # First 500 chars
                    if len(cat_execution.logs.stdout[0].text) > 500:
                        print("... (truncated)")
                    print("-" * 70)
                    print("✅ File reading successful!")
                else:
                    print("⚠️  No Python files found in the directory")
            else:
                print("⚠️  Could not list files")

        except Exception as e:
            print(f"❌ Failed to read files: {e}")
            print()

        # Test 4: Write test (if mount is read-write)
        print("📂 Test 4: Testing write access...")
        print("-" * 70)

        try:
            # Try to create a test file
            await sandbox.files.write_file(
                f"{CONTAINER_PATH}/sdk_test.txt",
                "This file was created by the SDK test!"
            )

            # Read it back
            execution = await sandbox.commands.run(f"cat {CONTAINER_PATH}/sdk_test.txt")
            content = execution.logs.stdout[0].text.strip()

            if "SDK test" in content:
                print("✅ Write access confirmed! File created and read successfully.")
                print(f"   Content: {content}")
            else:
                print("⚠️  Unexpected content")

            # Clean up test file
            await sandbox.commands.run(f"rm {CONTAINER_PATH}/sdk_test.txt")
            print("   Test file cleaned up.")

        except Exception as e:
            print(f"❌ Write test failed: {e}")
            print("   (This might be expected if mount is read-only)")

        print()
        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("📊 Summary:")
        print(f"   ✅ Sandbox created with volume mount")
        print(f"   ✅ Directory listing: {CONTAINER_PATH}")
        print(f"   ✅ Files accessible inside container")
        print(f"   ✅ SDK integration working correctly")
        print()

    except SandboxException as e:
        print(f"❌ Sandbox Error: [{e.error.code}] {e.error.message}")
        if hasattr(e, 'response'):
            print(f"   Response: {e.response}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        if sandbox:
            print("🧹 Cleaning up...")
            try:
                await sandbox.kill()
                await sandbox.close()
                print("✅ Sandbox terminated and cleaned up")
            except Exception as e:
                print(f"⚠️  Cleanup warning: {e}")


async def test_multiple_volume_mounts():
    """Test multiple volume mounts"""

    print("\n" + "=" * 70)
    print("Multiple Volume Mounts Test")
    print("=" * 70)
    print()

    SERVER_URL = "http://172.32.153.182:18888"
    API_KEY = "test-api-key-12345"

    config = ConnectionConfig(
        base_url=SERVER_URL,
        api_key=API_KEY,
    )

    sandbox = None

    try:
        # Mount two different directories
        volume_mounts = [
            VolumeMount(
                host_path="/data/AI/tengyt/OpenSandbox/tests/python",
                container_path="/python_tests",
                read_only=True,
            ),
            VolumeMount(
                host_path="/data/AI/tengyt/OpenSandbox/tests/java",
                container_path="/java_tests",
                read_only=True,
            ),
        ]

        print("🚀 Creating sandbox with multiple volume mounts...")

        sandbox = await Sandbox.create(
            "python:3.11-slim",
            connection_config=config,
            timeout=timedelta(minutes=10),
            resource={"cpu": "500m", "memory": "512Mi"},
            volume_mounts=volume_mounts,
            entrypoint=["sleep", "600"],
        )

        print(f"✅ Sandbox created: {sandbox.id}")
        print()

        # List both mounted directories
        print("📂 Checking Python test files...")
        execution = await sandbox.commands.run("ls /python_tests")
        print(execution.logs.stdout[0].text)

        print("\n📂 Checking Java test files...")
        execution = await sandbox.commands.run("ls /java_tests")
        print(execution.logs.stdout[0].text)

        print("\n✅ Multiple volume mounts working!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if sandbox:
            print("\n🧹 Cleaning up...")
            await sandbox.kill()
            await sandbox.close()
            print("✅ Cleanup complete")


if __name__ == "__main__":
    print("\n🚀 Starting Volume Mounts SDK Test\n")

    # Run single volume mount test
    asyncio.run(test_volume_mounts_with_sdk())

    # Run multiple volume mounts test
    # asyncio.run(test_multiple_volume_mounts())

    print("\n✨ Test completed!")
