#!/bin/bash
# OpenSandbox Python SDK 部署脚本
# 用途: 构建和发布 SDK 到 PyPI 或私有仓库

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示使用帮助
show_help() {
    cat << EOF
OpenSandbox Python SDK 部署脚本

用法: $0 [命令] [选项]

命令:
  build              构建包（不发布）
  testpypi           发布到 TestPyPI
  pypi               发布到生产 PyPI
  install            从本地源码安装（开发模式）
  check              验证安装

选项:
  --no-test          跳过测试
  --version VERSION  指定版本号（覆盖 Git 标签）

示例:
  $0 build                          # 仅构建
  $0 testpypi                       # 发布到 TestPyPI
  $0 pypi                           # 发布到 PyPI
  $0 install                        # 本地安装
  $0 check                          # 验证安装

EOF
}

# 检查必要的工具
check_dependencies() {
    log_info "检查依赖工具..."

    if ! command -v python &> /dev/null; then
        log_error "Python 未安装"
        exit 1
    fi

    if ! command -v git &> /dev/null; then
        log_error "Git 未安装"
        exit 1
    fi

    log_info "✓ 依赖检查通过"
}

# 运行测试
run_tests() {
    log_info "运行测试套件..."

    if [ "$SKIP_TESTS" = "true" ]; then
        log_warn "跳过测试（--no-test）"
        return
    fi

    cd sdks/sandbox/python

    # 运行测试
    if command -v pytest &> /dev/null; then
        pytest tests/ -v || {
            log_error "测试失败"
            exit 1
        }
    else
        log_warn "pytest 未安装，跳过测试"
    fi

    cd ../../..
    log_info "✓ 测试通过"
}

# 代码检查
run_linting() {
    log_info "运行代码检查..."

    cd sdks/sandbox/python

    # 运行 ruff（如果安装）
    if command -v ruff &> /dev/null; then
        ruff check src/ || {
            log_error "代码检查失败"
            exit 1
        }
    else
        log_warn "ruff 未安装，跳过代码检查"
    fi

    cd ../../..
    log_info "✓ 代码检查通过"
}

# 创建版本标签
create_version_tag() {
    if [ -n "$OVERRIDE_VERSION" ]; then
        log_info "使用覆盖版本: $OVERRIDE_VERSION"
        VERSION=$OVERRIDE_VERSION
        TAG_NAME="python/sandbox/v$VERSION"
    else
        # 尝试从现有标签获取版本
        CURRENT_TAG=$(git describe --tags --abbrev=0 --match "python/sandbox/v*" 2>/dev/null || echo "")

        if [ -n "$CURRENT_TAG" ]; then
            log_info "检测到现有标签: $CURRENT_TAG"
            read -p "是否创建新版本? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                read -p "输入新版本号 (例如 1.0.1): " VERSION
                TAG_NAME="python/sandbox/v$VERSION"
            else
                TAG_NAME=$CURRENT_TAG
                VERSION=${TAG_NAME#python/sandbox/v}
            fi
        else
            log_warn "未找到版本标签"
            read -p "输入版本号 (例如 1.0.0): " VERSION
            TAG_NAME="python/sandbox/v$VERSION"
        fi
    fi

    # 创建标签（如果不存在）
    if ! git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
        log_info "创建标签: $TAG_NAME"
        git tag "$TAG_NAME"
        git push origin "$TAG_NAME"
    else
        log_info "标签已存在: $TAG_NAME"
    fi
}

# 构建包
build_package() {
    log_info "开始构建包..."

    cd sdks/sandbox/python

    # 清理旧的构建
    log_info "清理旧的构建文件..."
    rm -rf dist/ build/ *.egg-info

    # 安装构建工具
    log_info "安装构建工具..."
    pip install --quiet build twine

    # 构建
    log_info "构建包..."
    python -m build

    # 检查构建结果
    if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
        log_error "构建失败：dist 目录为空"
        exit 1
    fi

    log_info "构建完成，生成的文件："
    ls -lh dist/

    cd ../../..
}

# 检查包
check_package() {
    log_info "检查包..."
    cd sdks/sandbox/python

    twine check dist/*

    cd ../../..
}

# 发布到 TestPyPI
publish_testpypi() {
    log_info "发布到 TestPyPI..."

    cd sdks/sandbox/python

    twine upload --repository testpypi dist/*

    log_info "✓ 发布到 TestPyPI 成功"
    log_info "测试安装: pip install --index-url https://test.pypi.org/simple/ opensandbox"

    cd ../../..
}

# 发布到 PyPI
publish_pypi() {
    log_info "发布到 PyPI..."

    cd sdks/sandbox/python

    twine upload dist/*

    log_info "✓ 发布到 PyPI 成功"
    log_info "安装: pip install opensandbox"

    cd ../../..
}

# 本地安装
install_local() {
    log_info "本地安装 SDK（开发模式）..."

    cd sdks/sandbox/python

    pip install -e .

    log_info "✓ 安装完成"

    cd ../../..
}

# 验证安装
check_install() {
    log_info "验证安装..."

    python << EOF
import sys
try:
    import opensandbox
    print(f"✅ OpenSandbox SDK 已安装")
    print(f"   位置: {opensandbox.__file__}")

    from opensandbox import SandboxSync, Sandbox
    from opensandbox.models import VolumeMount
    print("✅ 所有核心模块导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)
EOF
}

# 主函数
main() {
    local COMMAND=$1
    shift

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-test)
                SKIP_TESTS=true
                shift
                ;;
            --version)
                OVERRIDE_VERSION=$2
                shift 2
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 切换到项目根目录
    cd "$(git rev-parse --show-toplevel)"

    case $COMMAND in
        build)
            check_dependencies
            run_linting
            run_tests
            create_version_tag
            build_package
            check_package
            log_info "✓ 构建完成！"
            ;;

        testpypi)
            check_dependencies
            run_linting
            run_tests
            create_version_tag
            build_package
            check_package
            publish_testpypi
            ;;

        pypi)
            check_dependencies
            run_linting
            run_tests
            create_version_tag
            build_package
            check_package
            publish_pypi
            ;;

        install)
            install_local
            check_install
            ;;

        check)
            check_install
            ;;

        *)
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
