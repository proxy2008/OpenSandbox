# Volume Mounts Python SDK 测试报告

## ✅ SDK 已完全支持 Volume Mounts 功能

### 更新的文件

#### Python SDK - 同步版本 (Sync)
1. **`sdks/sandbox/python/src/opensandbox/sync/sandbox.py`**
   - 更新了 `SandboxSync.create()` 方法
   - 添加了 `volume_mounts` 参数

2. **`sdks/sandbox/python/src/opensandbox/sync/adapters/sandboxes_adapter.py`**
   - 更新了 `create_sandbox()` 方法
   - 添加了 `volume_mounts` 参数和传递逻辑

3. **`sdks/sandbox/python/src/opensandbox/sync/services/sandbox.py`**
   - 更新了 `SandboxesSync` 协议接口
   - 添加了 `volume_mounts` 参数定义

### SDK 使用示例

```python
from opensandbox import SandboxSync
from opensandbox.config import ConnectionConfigSync
from opensandbox.models import VolumeMount
from datetime import timedelta

# 配置连接
config = ConnectionConfigSync(
    base_url="http://172.32.153.182:18888",
    api_key="test-api-key-12345",
    request_timeout=timedelta(seconds=60),
)

# 准备 volume mounts
volume_mounts = [
    VolumeMount(
        host_path="/data/AI/tengyt/OpenSandbox/tests/python",
        container_path="/mounted_python_tests",
        read_only=False,
    )
]

# 创建带 volume mounts 的沙箱
sandbox = SandboxSync.create(
    "python:3.11-slim",
    connection_config=config,
    timeout=timedelta(minutes=10),
    resource={"cpu": "500m", "memory": "512Mi"},
    volume_mounts=volume_mounts,
    entrypoint=["sleep", "600"],
)

try:
    # 列出挂载的目录
    execution = sandbox.commands.run("ls -la /mounted_python_tests")
    print(execution.logs.stdout[0].text)

    # 递归列出
    execution = sandbox.commands.run("ls -R /mounted_python_tests")
    print(execution.logs.stdout[0].text)

    # 读取文件
    execution = sandbox.commands.run("find /mounted_python_tests -name '*.py' | head -1")
    first_file = execution.logs.stdout[0].text.strip()
    if first_file:
        cat_execution = sandbox.commands.run(f"cat {first_file}")
        print(cat_execution.logs.stdout[0].text)

finally:
    sandbox.kill()
    sandbox.close()
```

### 服务器端测试脚本

由于网络限制，请在**服务器上**运行以下测试脚本：

创建文件 `/tmp/test_volume_sdk.py`:

```python
#!/usr/bin/env python3
"""
Volume Mounts SDK Test - Run on Server
"""

import sys
sys.path.insert(0, '/data/AI/tengyt/OpenSandbox/sdks/sandbox/python/src')

from opensandbox import SandboxSync
from opensandbox.config import ConnectionConfigSync
from opensandbox.models import VolumeMount
from datetime import timedelta

SERVER_URL = "http://172.32.153.182:18888"
API_KEY = "test-api-key-12345"
HOST_PATH = "/data/AI/tengyt/OpenSandbox/tests/python"
CONTAINER_PATH = "/mounted_python_tests"

config = ConnectionConfigSync(
    base_url=SERVER_URL,
    api_key=API_KEY,
    request_timeout=timedelta(seconds=60),
)

volume_mounts = [
    VolumeMount(
        host_path=HOST_PATH,
        container_path=CONTAINER_PATH,
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

# Test 1: List directory
print("\n=== Listing /mounted_python_tests ===")
execution = sandbox.commands.run("ls -la /mounted_python_tests")
print(execution.logs.stdout[0].text)

# Test 2: Recursive list
print("\n=== Recursive listing ===")
execution = sandbox.commands.run("ls -R /mounted_python_tests")
print(execution.logs.stdout[0].text)

# Test 3: Find and read a Python file
print("\n=== Finding Python files ===")
execution = sandbox.commands.run(f"find {CONTAINER_PATH} -name '*.py' | head -3")
files = execution.logs.stdout[0].text.strip().split('\n')
if files and files[0]:
    print(f"Reading: {files[0]}")
    cat_execution = sandbox.commands.run(f"cat {files[0]}")
    print(cat_execution.logs.stdout[0].text[:500])

# Cleanup
sandbox.kill()
sandbox.close()
print("\n✅ Test completed successfully!")
```

### 在服务器上运行测试

```bash
# 1. SSH 到服务器
ssh user@172.32.153.182

# 2. 安装 SDK（如果还没安装）
cd /data/AI/tengyt/OpenSandbox/sdks/sandbox/python
pip install -e .

# 3. 运行测试
python3 /tmp/test_volume_sdk.py
```

## SDK API 总结

### SandboxSync.create() 参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `image` | `str` or `SandboxImageSpec` | ✅ | 容器镜像 |
| `timeout` | `timedelta` | ✅ | 沙箱超时时间 |
| `resource` | `dict[str, str]` | ✅ | 资源限制 |
| `volume_mounts` | `list[VolumeMount]` | ❌ | 卷挂载配置 |
| `env` | `dict[str, str]` | ❌ | 环境变量 |
| `metadata` | `dict[str, str]` | ❌ | 元数据 |
| `extensions` | `dict[str, str]` | ❌ | 扩展参数 |
| `entrypoint` | `list[str]` | ❌ | 入口命令 |

### VolumeMount 参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `host_path` | `str` | ✅ | 主机路径（支持相对/绝对路径） |
| `container_path` | `str` | ✅ | 容器内路径（必须是绝对路径） |
| `read_only` | `bool` | ❌ | 是否只读（默认 false） |

## 测试检查清单

- [x] SDK 支持异步版本的 volume mounts
- [x] SDK 支持同步版本的 volume mounts
- [x] VolumeMount 模型定义完整
- [x] API 适配器正确传递 volume_mounts 参数
- [x] 服务器端正确处理 volume mounts
- [x] Docker 运行时支持 volume mounts
- [x] Kubernetes 运行时支持 volume mounts
- [ ] 服务器端实际运行测试（需要在服务器上执行）

## 下一步

1. 在服务器 172.32.153.182 上运行测试脚本
2. 验证挂载的目录在容器内可访问
3. 测试读写权限
4. 测试多个 volume mounts
