# OpenSandbox Python SDK 部署指南

本指南介绍如何将 OpenSandbox Python SDK 部署为系统包，供应用程序使用。

---

## 📦 部署方式概览

OpenSandbox Python SDK 支持多种部署方式：

| 方式 | 适用场景 | 复杂度 | 访问性 |
|------|---------|--------|--------|
| **PyPI 公共发布** | 开源项目，公开使用 | ⭐⭐ | 全球访问 |
| **私有 PyPI** | 企业内部使用 | ⭐⭐⭐ | 内网访问 |
| **直接源码安装** | 开发测试环境 | ⭐ | 需要 Git 访问 |
| **本地 Wheel 包** | 离线环境/CI/CD | ⭐⭐ | 文件传输 |

---

## 方式 1: 发布到 PyPI（公共包仓库）

### 1.1 准备工作

```bash
# 1. 安装构建工具
pip install build twine

# 2. 检查项目配置
cd sdks/sandbox/python
cat pyproject.toml  # 确认包名、版本等信息
```

### 1.2 创建版本标签

SDK 使用 Git 标签自动生成版本号（配置在 pyproject.toml 中）：

```bash
# 格式: python/sandbox/v{version}
git tag python/sandbox/v1.0.0
git push origin python/sandbox/v1.0.0
```

### 1.3 构建包

```bash
cd sdks/sandbox/python

# 清理旧的构建
rm -rf dist/

# 构建源码包和 Wheel 包
python -m build

# 检查生成的包
ls -lh dist/
# 输出示例:
# opensandbox-1.0.0.tar.gz  (源码包)
# opensandbox-1.0.0-py3-none-any.whl  (Wheel 包)
```

### 1.4 测试包（先发布到 TestPyPI）

```bash
# 1. 注册 TestPyPI 账号: https://test.pypi.org/account/register/

# 2. 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 3. 测试安装
pip install --index-url https://test.pypi.org/simple/ opensandbox

# 4. 验证
python -c "import opensandbox; print(opensandbox.__version__)"
```

### 1.5 发布到生产 PyPI

```bash
# 1. 注册 PyPI 账号: https://pypi.org/account/register/

# 2. 上传到 PyPI
twine upload dist/*

# 3. 验证发布
# 访问: https://pypi.org/project/opensandbox/

# 4. 测试安装
pip install opensandbox
```

### 1.6 用户使用

```bash
# 安装
pip install opensandbox

# 或使用 uv
uv add opensandbox

# 使用
from opensandbox import SandboxSync
from opensandbox.models import VolumeMount
```

---

## 方式 2: 部署到私有 PyPI（企业内部）

### 2.1 使用阿里云 Package Manager

```bash
# 1. 安装阿里云 CLI 工具
pip install aliyun-pypi

# 2. 配置认证
aliyun-pypi configure --host-id your-host-id --region-id your-region

# 3. 构建包
cd sdks/sandbox/python
python -m build

# 4. 上传
aliyun-pypi upload dist/*

# 5. 配置用户使用
pip config set global.index-url https://your-aliyun-pypi.repo.aliyun.com/simple
pip config set global.trusted-host your-aliyun-pypi.repo.aliyun.com
```

### 2.2 使用 JFrog Artifactory

```bash
# 1. 构建包
cd sdks/sandbox/python
python -m build

# 2. 使用 twine 上传到 Artifactory
twine upload --repository-url https://your-artifactory/artifactory/api/pypi/your-pypi dist/*

# 3. 配置用户使用
pip install opensandbox --index-url https://your-artifactory/artifactory/api/pypi/your-pypi/simple
```

### 2.3 使用 devpi（私有 PyPI 服务器）

```bash
# 1. 安装 devpi
pip install devpi-server devpi-web

# 2. 启动 devpi 服务器
devpi-init
devpi-server --host 0.0.0.0 --port 3141 --start

# 3. 创建用户和索引
devpi use http://localhost:3141
devpi user -c user1 email@example.com
devpi login user1
devpi index -c bases=root/pypi

# 4. 上传包
cd sdks/sandbox/python
python -m build
devpi upload dist/*

# 5. 用户配置使用
pip install --index-url http://your-devpi:3141/user1/+simple/ opensandbox
```

---

## 方式 3: 直接从源码安装（开发/测试）

### 3.1 从 Git 仓库安装

```bash
# 从 GitHub 安装（推荐）
pip install git+https://github.com/proxy2008/OpenSandbox.git@main#subdirectory=sdks/sandbox/python

# 指定分支或标签
pip install git+https://github.com/proxy2008/OpenSandbox.git@feature/volume-mounts-implementation#subdirectory=sdks/sandbox/python

# 或使用 SSH
pip install git+ssh://git@github.com/proxy2008/OpenSandbox.git@main#subdirectory=sdks/sandbox/python
```

### 3.2 从本地目录安装

```bash
# 开发模式（可编辑安装）
cd sdks/sandbox/python
pip install -e .

# 正常安装
pip install .

# 使用 pip 的本地路径
pip install /path/to/OpenSandbox/sdks/sandbox/python
```

### 3.3 从压缩包安装

```bash
# 1. 打包
tar -czf opensandbox-sdk.tar.gz sdks/sandbox/python/

# 2. 传输到目标机器
scp opensandbox-sdk.tar.gz user@server:/tmp/

# 3. 安装
pip install /tmp/opensandbox-sdk.tar.gz
```

---

## 方式 4: 构建 Wheel 包（离线环境/CI/CD）

### 4.1 构建多平台 Wheel 包

```bash
cd sdks/sandbox/python

# 安装构建工具
pip install build cibuildwheel

# 构建当前平台的 Wheel
python -m build

# 或使用 cibuildwheel 构建多平台包
cibuildwheel --platform linux
cibuildwheel --platform macos
cibuildwheel --platform windows
```

### 4.2 离线部署流程

```bash
# 1. 在联网机器上构建包
cd sdks/sandbox/python
python -m build

# 2. 收集所有依赖
pip download -d ./deps opensandbox

# 3. 打包
tar -czf opensandbox-offline.tar.gz dist/ deps/

# 4. 传输到目标机器
scp opensandbox-offline.tar.gz user@offline-server:/tmp/

# 5. 在目标机器上安装
cd /tmp
tar -xzf opensandbox-offline.tar.gz
pip install --no-index --find-links=deps dist/opensandbox-*.whl
```

### 4.3 Docker 镜像中包含 SDK

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 复制 SDK 源码
COPY sdks/sandbox/python /tmp/sdk
RUN pip install /tmp/sdk

# 或直接从安装
# RUN pip install git+https://github.com/proxy2008/OpenSandbox.git@main#subdirectory=sdks/sandbox/python

# 复制应用代码
COPY . .

CMD ["python", "app.py"]
```

---

## 🔧 配置和验证

### 验证安装

```python
# 验证脚本 check_install.py
import sys

def check_install():
    try:
        import opensandbox
        print(f"✅ OpenSandbox SDK installed successfully!")
        print(f"   Version: {opensandbox.__version__ if hasattr(opensandbox, '__version__') else 'unknown'}")
        print(f"   Location: {opensandbox.__file__}")

        # Test imports
        from opensandbox import SandboxSync, Sandbox
        from opensandbox.models import VolumeMount
        from opensandbox.config import ConnectionConfigSync

        print("✅ All core modules imported successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = check_install()
    sys.exit(0 if success else 1)
```

运行验证：
```bash
python check_install.py
```

### 查看 SDK 信息

```bash
# 查看 SDK 信息
pip show opensandbox

# 列出安装的文件
pip show -f opensandbox

# 检查依赖
pip list | grep opensandbox
pip check opensandbox
```

---

## 📋 CI/CD 集成示例

### GitHub Actions 自动发布

```yaml
# .github/workflows/publish-sdk.yml
name: Publish Python SDK

on:
  push:
    tags:
      - 'python/sandbox/v*'

jobs:
  build-and-publish:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0  # 获取完整历史用于版本计算

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install build tools
      run: |
        pip install build twine

    - name: Build package
      run: |
        cd sdks/sandbox/python
        python -m build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        cd sdks/sandbox/python
        twine upload dist/*
```

### GitLab CI 自动发布

```yaml
# .gitlab-ci.yml
publish-sdk:
  stage: deploy
  image: python:3.11
  script:
    - pip install build twine
    - cd sdks/sandbox/python
    - python -m build
    - twine upload --repository-url ${PYPI_REPO_URL} dist/*
  only:
    - tags
  variables:
    PYPI_REPO_URL: "https://your-pypi-repo/simple"
```

---

## 🚀 最佳实践

### 1. 版本管理

```bash
# 遵循语义化版本
# 格式: python/sandbox/v{major}.{minor}.{patch}
git tag python/sandbox/v1.0.0
git tag python/sandbox/v1.1.0
git tag python/sandbox/v1.1.1

# 推送标签
git push origin --tags
```

### 2. 发布前检查清单

- [ ] 更新版本号（通过 Git 标签）
- [ ] 运行测试套件: `pytest`
- [ ] 代码检查: `ruff check`
- [ ] 类型检查: `pyright`
- [ ] 更新 CHANGELOG.md
- [ ] 测试安装: `pip install .`
- [ ] 验证导入: `python -c "import opensandbox"`

### 3. 文档和元数据

确保 `pyproject.toml` 中的信息完整：

```toml
[project]
name = "opensandbox"
description = "..."  # 清晰的描述
authors = [...]
license = {...}
readme = "README.md"
requires-python = ">=3.10"
keywords = [...]
classifiers = [...]

[project.urls]
Homepage = "..."
Repository = "..."
Documentation = "..."
Issues = "..."
```

---

## 📚 使用示例

### 在应用中使用

```python
# app.py
from opensandbox import SandboxSync
from opensandbox.config import ConnectionConfigSync
from opensandbox.models import VolumeMount
from datetime import timedelta

# 配置连接
config = ConnectionConfigSync(
    base_url="http://your-server:18888",
    api_key="your-api-key",
)

# 创建带卷挂载的沙箱
volume_mounts = [
    VolumeMount(
        host_path="/data/app",
        container_path="/app_data",
        read_only=False
    )
]

sandbox = SandboxSync.create(
    "python:3.11-slim",
    connection_config=config,
    timeout=timedelta(minutes=10),
    volume_mounts=volume_mounts,
)

# 使用沙箱...
try:
    execution = sandbox.commands.run("python /app_data/script.py")
    print(execution.logs.stdout[0].text)
finally:
    sandbox.kill()
    sandbox.close()
```

### requirements.txt

```txt
opensandbox>=1.0.0
```

### pyproject.toml（如果您的项目也使用 pyproject.toml）

```toml
[project]
dependencies = [
    "opensandbox>=1.0.0",
]
```

---

## 🔍 故障排除

### 常见问题

**Q: 构建失败 "error: invalid version"**

```bash
# 解决方案: 创建 Git 标签
git tag python/sandbox/v1.0.0
git push origin python/sandbox/v1.0.0
```

**Q: 找不到版本信息**

```bash
# 检查 Git 标签
git tag -l "python/sandbox/v*"

# 或设置 fallback 版本
# 编辑 pyproject.toml:
# [tool.hatch.version.raw-options]
# fallback_version = "1.0.0"
```

**Q: 安装后无法导入**

```bash
# 检查安装位置
pip show opensandbox

# 确认在正确的 Python 环境中
which python
python -m pip install opensandbox
```

---

## 📞 支持

- GitHub: https://github.com/proxy2008/OpenSandbox
- Issues: https://github.com/proxy2008/OpenSandbox/issues
- 文档: https://docs.opensandbox.io

---

**最后更新**: 2025-01-15
