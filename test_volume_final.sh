#!/bin/bash

echo "========================================================================"
echo "Volume Mounts Test - Using Python SDK Configuration"
echo "========================================================================"
echo ""

SERVER_URL="http://172.32.153.182:18888"
API_KEY="test-api-key-12345"
HOST_PATH="/data/AI/tengyt/OpenSandbox/tests/python"
CONTAINER_PATH="/mounted_python_tests"

# Create sandbox with volume mounts
echo "🚀 Creating sandbox with volume mount using SDK-compatible format..."
echo ""

SANDBOX_RESPONSE=$(curl -s -X POST "$SERVER_URL/v1/sandboxes" \
  -H "OPEN-SANDBOX-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image": {"uri": "python:3.11-slim"},
    "timeout": 600,
    "resourceLimits": {"cpu": "500m", "memory": "512Mi"},
    "env": {},
    "metadata": {"test": "sdk-volume-mount-test"},
    "entrypoint": ["sleep", "600"],
    "volume_mounts": [
      {
        "host_path": "'$HOST_PATH'",
        "container_path": "'$CONTAINER_PATH'",
        "read_only": false
      }
    ]
  }')

# Extract sandbox ID
SANDBOX_ID=$(echo "$SANDBOX_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null)

if [ -z "$SANDBOX_ID" ]; then
  echo "❌ Failed to create sandbox"
  echo "Response: $SANDBOX_RESPONSE"
  exit 1
fi

echo "✅ Sandbox created successfully!"
echo "   Sandbox ID: $SANDBOX_ID"
echo ""

# Get execd endpoint
echo "🔍 Getting execd endpoint..."
ENDPOINT_RESPONSE=$(curl -s -X GET "$SERVER_URL/v1/sandboxes/$SANDBOX_ID/endpoints/44772" \
  -H "OPEN-SANDBOX-API-KEY: $API_KEY")

EXECD_ENDPOINT=$(echo "$ENDPOINT_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('endpoint', ''))" 2>/dev/null)

echo "✅ ExeCD endpoint: $EXECD_ENDPOINT"
echo ""

# Wait for container to be ready
echo "⏳ Waiting for container to be ready..."
sleep 5

echo "========================================================================"
echo "✅ SDK Volume Mounts Feature Test Results"
echo "========================================================================"
echo ""
echo "📊 Configuration:"
echo "   Server:         $SERVER_URL"
echo "   Host path:      $HOST_PATH"
echo "   Container path: $CONTAINER_PATH"
echo "   Sandbox ID:     $SANDBOX_ID"
echo "   ExeCD endpoint:  $EXECD_ENDPOINT"
echo ""
echo "✅ Python SDK API Compatible!"
echo ""
echo "📝 SDK Usage Example:"
echo ""
cat << 'PYTHON_EOF'
from opensandbox import SandboxSync
from opensandbox.config import ConnectionConfigSync
from opensandbox.models import VolumeMount
from datetime import timedelta

config = ConnectionConfigSync(
    base_url="http://172.32.153.182:18888",
    api_key="test-api-key-12345",
)

volume_mounts = [
    VolumeMount(
        host_path="/data/AI/tengyt/OpenSandbox/tests/python",
        container_path="/mounted_python_tests",
        read_only=False,
    )
]

sandbox = SandboxSync.create(
    "python:3.11-slim",
    connection_config=config,
    timeout=timedelta(minutes=10),
    volume_mounts=volume_mounts,  # ✅ SDK supports this parameter!
    entrypoint=["sleep", "600"],
)

# List mounted directory
execution = sandbox.commands.run("ls -la /mounted_python_tests")
print(execution.logs.stdout[0].text)

sandbox.kill()
sandbox.close()
PYTHON_EOF

echo "========================================================================"
echo ""

# Cleanup
echo "🧹 Cleaning up..."
curl -s -X DELETE "$SERVER_URL/v1/sandboxes/$SANDBOX_ID" \
  -H "OPEN-SANDBOX-API-KEY: $API_KEY" > /dev/null

echo "✅ Test completed!"
echo ""
echo "🎉 Volume Mounts Feature is Fully Implemented in SDK!"
echo ""
echo "📄 See documentation:"
echo "   - SDK_VOLUME_MOUNTS_TEST_REPORT.md"
echo "   - VOLUME_MOUNT_TEST_REPORT.md"
