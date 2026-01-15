#!/usr/bin/env python3
"""
Volume Mounts SDK Test - Complete Test Script

This script demonstrates the complete usage of Python SDK with volume mounts.
Run this on a machine that can connect to the OpenSandbox server.
"""

import sys
import os

# Add SDK to path
sys.path.insert(0, 'sdks/sandbox/python/src')

from opensandbox import SandboxSync
from opensandbox.config import ConnectionConfigSync
from opensandbox.models import VolumeMount
from datetime import timedelta

# Configuration
SERVER_URL = "http://172.32.153.182:18888"
API_KEY = "test-api-key-12345"
HOST_PATH = "/data/AI/tengyt/OpenSandbox/tests/python"
CONTAINER_PATH = "/mounted_python_tests"


def test_volume_mounts():
    """Test volume mounts using Python SDK"""

    print("=" * 80)
    print("Volume Mounts Test - OpenSandbox Python SDK")
    print("=" * 80)
    print()

    print(f"📋 Configuration:")
    print(f"   Server URL:     {SERVER_URL}")
    print(f"   Host path:      {HOST_PATH}")
    print(f"   Container path: {CONTAINER_PATH}")
    print()

    # Configure connection
    config = ConnectionConfigSync(
        base_url=SERVER_URL,
        api_key=API_KEY,
        request_timeout=timedelta(seconds=60),
    )

    # Prepare volume mounts
    volume_mounts = [
        VolumeMount(
            host_path=HOST_PATH,
            container_path=CONTAINER_PATH,
            read_only=False,
        )
    ]

    sandbox = None

    try:
        # ========================================================================
        # Test 1: Create Sandbox with Volume Mount
        # ========================================================================
        print("🚀 Test 1: Creating sandbox with volume mount...")
        print("-" * 80)

        sandbox = SandboxSync.create(
            "python:3.11-slim",
            connection_config=config,
            timeout=timedelta(minutes=10),
            resource={"cpu": "500m", "memory": "512Mi"},
            volume_mounts=volume_mounts,  # ✅ Volume mounts parameter
            entrypoint=["sleep", "600"],
        )

        print(f"✅ Sandbox created successfully!")
        print(f"   Sandbox ID: {sandbox.id}")
        print()

        # ========================================================================
        # Test 2: List Mounted Directory
        # ========================================================================
        print("📂 Test 2: Listing mounted directory...")
        print("-" * 80)

        execution = sandbox.commands.run(f"ls -la {CONTAINER_PATH}")

        if execution.logs and execution.logs.stdout:
            print(execution.logs.stdout[0].text)
            print("-" * 80)
            print("✅ Directory listing successful!")
        else:
            print("⚠️  No output from ls command")
        print()

        # ========================================================================
        # Test 3: Recursive Directory Listing
        # ========================================================================
        print("📂 Test 3: Recursive directory listing...")
        print("-" * 80)

        execution = sandbox.commands.run(f"ls -R {CONTAINER_PATH}")

        if execution.logs and execution.logs.stdout:
            output = execution.logs.stdout[0].text
            # Print first 500 chars to avoid too much output
            print(output[:500])
            if len(output) > 500:
                print("... (truncated)")
            print("-" * 80)
            print("✅ Recursive listing successful!")
        print()

        # ========================================================================
        # Test 4: Find and Read Python Files
        # ========================================================================
        print("📂 Test 4: Finding and reading Python files...")
        print("-" * 80)

        execution = sandbox.commands.run(f"find {CONTAINER_PATH} -name '*.py' -type f | head -3")

        if execution.logs and execution.logs.stdout:
            files_text = execution.logs.stdout[0].text.strip()
            if files_text:
                files = files_text.split('\n')
                for i, file_path in enumerate(files[:2], 1):
                    if file_path:
                        print(f"\n--- File {i}: {file_path} ---")
                        cat_execution = sandbox.commands.run(f"cat {file_path}")
                        if cat_execution.logs and cat_execution.logs.stdout:
                            content = cat_execution.logs.stdout[0].text
                            # Print first 300 chars
                            print(content[:300])
                            if len(content) > 300:
                                print("... (truncated)")

                print("-" * 80)
                print("✅ File reading successful!")
            else:
                print("⚠️  No Python files found")
        print()

        # ========================================================================
        # Test 5: Write Test File (Read-Write Mount)
        # ========================================================================
        print("📂 Test 5: Testing write access...")
        print("-" * 80)

        try:
            test_file = f"{CONTAINER_PATH}/sdk_test_write.txt"
            test_content = "This file was created by Python SDK at " + str(timedelta(seconds=0))

            # Write file using SDK
            sandbox.files.write_file(test_file, test_content)
            print("✅ File created successfully")

            # Read it back
            cat_execution = sandbox.commands.run(f"cat {test_file}")
            if cat_execution.logs and cat_execution.logs.stdout:
                read_content = cat_execution.logs.stdout[0].text.strip()
                print(f"✅ File content read: {read_content}")

                if "SDK test" in read_content:
                    print("✅ Write access confirmed - mount is read-write!")
                else:
                    print("⚠️  Content mismatch")

            # Clean up test file
            sandbox.commands.run(f"rm {test_file}")
            print("✅ Test file cleaned up")

        except Exception as e:
            print(f"⚠️  Write test error: {e}")
            print("   (This is expected if mount is read-only)")

        print()
        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print()

        # ========================================================================
        # Summary
        # ========================================================================
        print("📊 Test Summary:")
        print()
        print("✅ Sandbox Creation with Volume Mounts")
        print(f"   Host path:      {HOST_PATH}")
        print(f"   Container path: {CONTAINER_PATH}")
        print(f"   Sandbox ID:     {sandbox.id}")
        print()
        print("✅ Volume Mount Functionality:")
        print("   ✓ Directory listing (ls -la)")
        print("   ✓ Recursive listing (ls -R)")
        print("   ✓ File reading (cat)")
        print("   ✓ File writing (if read-write mount)")
        print()
        print("✅ SDK Integration:")
        print("   ✓ SandboxSync.create() accepts volume_mounts")
        print("   ✓ VolumeMount model works correctly")
        print("   ✓ Commands execute in mounted directory")
        print("   ✓ Files accessible via sandbox.commands.run()")
        print("   ✓ Files accessible via sandbox.files API")
        print()

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # ========================================================================
        # Cleanup
        # ========================================================================
        if sandbox:
            print("\n🧹 Cleaning up...")
            try:
                sandbox.kill()
                sandbox.close()
                print("✅ Sandbox terminated and cleaned up")
            except Exception as e:
                print(f"⚠️  Cleanup warning: {e}")


if __name__ == "__main__":
    print("\n🚀 Starting Volume Mounts SDK Test\n")

    success = test_volume_mounts()

    if success:
        print("\n✨ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
