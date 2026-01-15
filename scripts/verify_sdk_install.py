#!/usr/bin/env python3
"""
OpenSandbox SDK 安装验证脚本

用法:
    python verify_sdk_install.py
"""

import sys


def print_header(text: str) -> None:
    """打印标题"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}")


def print_success(text: str) -> None:
    """打印成功信息"""
    print(f"✅ {text}")


def print_error(text: str) -> None:
    """打印错误信息"""
    print(f"❌ {text}")


def print_info(text: str) -> None:
    """打印信息"""
    print(f"ℹ️  {text}")


def check_python_version() -> bool:
    """检查 Python 版本"""
    print_header("检查 Python 版本")

    version = sys.version_info
    print_info(f"Python 版本: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error("需要 Python 3.10 或更高版本")
        return False

    print_success("Python 版本符合要求")
    return True


def check_sdk_install() -> bool:
    """检查 SDK 安装"""
    print_header("检查 SDK 安装")

    try:
        import opensandbox

        print_success("OpenSandbox SDK 已安装")
        print_info(f"安装位置: {opensandbox.__file__}")

        if hasattr(opensandbox, "__version__"):
            print_info(f"SDK 版本: {opensandbox.__version__}")
        else:
            print_info("SDK 版本: 未知 (开发模式)")

        return True

    except ImportError as e:
        print_error(f"SDK 未安装或导入失败: {e}")
        print_info("\n安装 SDK:")
        print_info("  pip install opensandbox")
        print_info("或:")
        print_info("  cd sdks/sandbox/python && pip install -e .")
        return False


def check_core_modules() -> bool:
    """检查核心模块"""
    print_header("检查核心模块")

    modules = [
        ("opensandbox", "主模块"),
        ("opensandbox.sandbox", "异步沙箱"),
        ("opensandbox.sync", "同步沙箱"),
        ("opensandbox.config", "配置模块"),
        ("opensandbox.models", "数据模型"),
        ("opensandbox.models.volume_mount", "卷挂载模型"),
        ("opensandbox.exceptions", "异常处理"),
    ]

    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print_success(f"{description:20} ({module_name})")
        except ImportError as e:
            print_error(f"{description:20} ({module_name}): {e}")
            all_ok = False

    return all_ok


def check_sdk_imports() -> bool:
    """检查 SDK 常用导入"""
    print_header("检查常用导入")

    try:
        from opensandbox import SandboxSync, Sandbox
        print_success("SandboxSync, Sandbox 导入成功")

        from opensandbox.config import ConnectionConfigSync, ConnectionConfig
        print_success("ConnectionConfig 导入成功")

        from opensandbox.models import VolumeMount
        print_success("VolumeMount 导入成功")

        from opensandbox.exceptions import SandboxException
        print_success("SandboxException 导入成功")

        return True

    except ImportError as e:
        print_error(f"导入失败: {e}")
        return False


def check_dependencies() -> bool:
    """检查依赖包"""
    print_header("检查依赖包")

    dependencies = [
        ("pydantic", "Pydantic 数据验证"),
        ("httpx", "HTTP 客户端"),
        ("python_dateutil", "日期时间处理"),
        ("attr", "Attrs 类库"),
    ]

    all_ok = True
    for package, description in dependencies:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{description:30} ({package})")
        except ImportError:
            print_error(f"{description:30} ({package}) 未安装")
            all_ok = False

    return all_ok


def show_usage_example() -> None:
    """显示使用示例"""
    print_header("SDK 使用示例")

    example = '''
# 示例 1: 创建同步沙箱
from datetime import timedelta
from opensandbox import SandboxSync
from opensandbox.config import ConnectionConfigSync
from opensandbox.models import VolumeMount

config = ConnectionConfigSync(
    base_url="http://your-server:18888",
    api_key="your-api-key",
)

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

try:
    execution = sandbox.commands.run("ls -la /app_data")
    print(execution.logs.stdout[0].text)
finally:
    sandbox.kill()
    sandbox.close()
'''

    print(example)


def main() -> int:
    """主函数"""
    print("\n🚀 OpenSandbox SDK 安装验证\n")

    results = {
        "Python 版本": check_python_version(),
        "SDK 安装": check_sdk_install(),
        "核心模块": check_core_modules(),
        "常用导入": check_sdk_imports(),
        "依赖包": check_dependencies(),
    }

    # 显示结果总结
    print_header("验证结果")

    all_passed = True
    for check, passed in results.items():
        if passed:
            print_success(f"{check:15} - 通过")
        else:
            print_error(f"{check:15} - 失败")
            all_passed = False

    if all_passed:
        print_header("✅ 所有检查通过！SDK 安装正确。")
        show_usage_example()
        return 0
    else:
        print_header("❌ 部分检查失败，请修复上述问题。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
