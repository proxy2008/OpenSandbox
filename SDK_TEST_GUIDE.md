# Volume Mounts SDK 测试指南

## 情况说明

从本地 macOS 机器无法直接建立 TCP 连接到 `172.32.153.182:18888`（连接被拒绝，错误代码 61），但服务器的健康检查端点可以访问。

这可能是因为：
1. 服务器只监听特定的网络接口
2. 防火墙规则阻止了某些类型的连接
3. 网络配置限制

## 解决方案

测试脚本已准备好，需要在**能够连接到服务器**的机器上运行。

### 方案 1: 在服务器上直接运行（推荐）

SSH 到服务器并运行测试：

```bash
# 1. SSH 到服务器
ssh user@172.32.153.182

# 2. 创建测试脚本
cat > /tmp/test_sdk_volume_mounts.py << 'TEST_SCRIPT'
import sys
sys.path.insert(0, '/data/AI/tengyt/OpenSandbox/sdks/sandbox/python/src')

from opensandbox import SandboxSync
from opensandbox.config import ConnectionConfigSync
from opensandbox.models import VolumeMount
from datetime import timedelta

config = ConnectionConfigSync(
    base_url="http://172.32.153.182:18888",
    api_key="test-api-key-12345",
    request_timeout=timedelta(seconds=60),
)

volume_mounts = [
    VolumeMount(
        host_path="/data/AI/tengyt/OpenSandbox/tests/python",
        container_path="/mounted_python_tests",
        read_only=False,
    )
]

print("Creating sandbox with volume mount...")
sandbox = SandboxSync.create(
    "python:3.11-slim",
    connection_config=config,
    timeout=timedelta(minutes=10),
    resource={"cpu": "500m", "memory": "512Mi"},
    volume_mounts=volume_mounts,
    entrypoint=["sleep", "600"],
)

print(f"Sandbox created: {sandbox.id}")

# Test directory listing
print("\n=== Listing /mounted_python_tests ===")
execution = sandbox.commands.run("ls -la /mounted_python_tests")
print(execution.logs.stdout[0].text)

# Test file reading
print("\n=== Finding Python files ===")
execution = sandbox.commands.run("find /mounted_python_tests -name '*.py' | head -1")
files = execution.logs.stdout[0].text.strip()
if files:
    print(f"Reading: {files}")
    cat_exec = sandbox.commands.run(f"cat {files}")
    print(cat_exec.logs.stdout[0].text[:500])

sandbox.kill()
sandbox.close()
print("\n✅ Test completed!")
TEST_SCRIPT

# 3. 运行测试
cd /data/AI/tengyt/OpenSandbox
python3 /tmp/test_sdk_volume_mounts.py
```

### 方案 2: 使用 Docker 容器测试

```bash
# 在服务器上运行
docker run -it --rm \
  -v /data/AI/tengyt/OpenSandbox:/workspace \
  -w /workspace \
  python:3.11-slim \
  bash -c "
    pip install httpx pydantic python-dateutil attrs -q && \
    pip install -e sdks/sandbox/python -q && \
    python3 /tmp/test_sdk_volume_mounts.py
  "
```

### 方案 3: 使用项目已有的虚拟环境

如果服务器上已有虚拟环境：

```bash
cd /data/AI/tengyt/OpenSandbox

# 激活虚拟环境（如果存在）
source venv/bin/activate  # 或其他虚拟环境路径

# 安装 SDK
pip install -e sdks/sandbox/python

# 运行测试
python3 test_sdk_volume_mounts.py
```

## 已创建的测试文件

1. **`test_sdk_volume_mounts.py`** - 完整的 SDK 测试脚本
   - 5 个测试用例
   - 覆盖创建、列出、读写等操作
   - 包含详细的输出和错误处理

2. **`test_volume_sdk_sync.py`** - 简化版本的测试

3. **`test_volume_sdk.py`** - 异步版本的测试

## SDK API 完整示例

```python
from opensandbox import SandboxSync
from opensandbox.config import ConnectionConfigSync
from opensandbox.models import VolumeMount
from datetime import timedelta

# 1. 配置连接
config = ConnectionConfigSync(
    base_url="http://172.32.153.182:18888",
    api_key="test-api-key-12345",
    request_timeout=timedelta(seconds=60),
)

# 2. 准备 volume mounts
volume_mounts = [
    VolumeMount(
        host_path="/data/AI/tengyt/OpenSandbox/tests/python",
        container_path="/mounted_python_tests",
        read_only=False,  # 设为 True 则只读
    )
]

# 3. 创建沙箱
sandbox = SandboxSync.create(
    "python:3.11-slim",
    connection_config=config,
    timeout=timedelta(minutes=10),
    resource={"cpu": "500m", "memory": "512Mi"},
    volume_mounts=volume_mounts,  # ✅ 支持 volume mounts
    entrypoint=["sleep", "600"],
)

try:
    # 4. 在挂载的目录中执行命令
    execution = sandbox.commands.run("ls -la /mounted_python_tests")
    print(execution.logs.stdout[0].text)

    # 5. 读取文件
    execution = sandbox.commands.run("cat /mounted_python_tests/file.py")
    print(execution.logs.stdout[0].text)

    # 6. 写入文件（如果挂载是读写模式）
    sandbox.files.write_file(
        "/mounted_python_tests/test.txt",
        "Hello from SDK!"
    )

finally:
    # 7. 清理
    sandbox.kill()
    sandbox.close()
```

## SDK 更新内容总结

### 更新的文件

#### 同步版本 (Sync)
1. ✅ `sdks/sandbox/python/src/opensandbox/sync/sandbox.py`
   - `SandboxSync.create()` 添加 `volume_mounts` 参数

2. ✅ `sdks/sandbox/python/src/opensandbox/sync/adapters/sandboxes_adapter.py`
   - `create_sandbox()` 添加 `volume_mounts` 参数

3. ✅ `sdks/sandbox/python/src/opensandbox/sync/services/sandbox.py`
   - `SandboxesSync` 协议接口更新

#### 异步版本 (Async)
1. ✅ `sdks/sandbox/python/src/opensandbox/sandbox.py`
2. ✅ `sdks/sandbox/python/src/opensandbox/adapters/sandboxes_adapter.py`
3. ✅ `sdks/sandbox/python/src/opensandbox/services/sandbox.py`

#### 模型层
1. ✅ `sdks/sandbox/python/src/opensandbox/models/volume_mount.py` (新建)
2. ✅ `sdks/sandbox/python/src/opensandbox/models/__init__.py`

## 测试检查清单

- [x] SDK 异步版本支持 volume_mounts
- [x] SDK 同步版本支持 volume_mounts
- [x] VolumeMount 模型实现
- [x] API 适配器传递 volume_mounts
- [x] 文档和示例代码

## 下一步

请在能够连接到服务器的机器上运行测试脚本以验证功能：

```bash
python3 test_sdk_volume_mounts.py
```

或在服务器上运行简化版本。

测试完成后请分享结果！🎉
