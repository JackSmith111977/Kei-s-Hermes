#!/bin/bash
# ============================================================================
# Hermes Catgirl Deploy - 一键部署脚本
# ============================================================================
# 使用方法：chmod +x deploy.sh && ./deploy.sh
# ============================================================================

set -e

# ── 颜色 ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# ── 配置 ──
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
INSTALL_DIR="${HERMES_INSTALL_DIR:-$HERMES_HOME/hermes-agent}"
REPO_URL="https://github.com/NousResearch/hermes-agent.git"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── 工具函数 ──
print_banner() {
    echo ""
    echo -e "${MAGENTA}${BOLD}"
    echo "┌─────────────────────────────────────────────────────────┐"
    echo "│        🐱 Hermes Catgirl Deploy - 一键部署               │"
    echo "│        猫娘女仆 AI Agent 部署脚本                        │"
    echo "└─────────────────────────────────────────────────────────┘"
    echo -e "${NC}"
}

log_info()    { echo -e "${CYAN}→${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warn()    { echo -e "${YELLOW}⚠${NC} $1"; }
log_error()   { echo -e "${RED}✗${NC} $1"; }
log_step()    { echo -e "\n${BOLD}${BLUE}═══ $1 ═══${NC}\n"; }

prompt_yes_no() {
    local question="$1"
    local default="${2:-yes}"
    local prompt_suffix
    case "$default" in
        [yY]*) prompt_suffix="[Y/n]" ;;
        *)     prompt_suffix="[y/N]" ;;
    esac
    if [ -t 0 ]; then
        read -r -p "$question $prompt_suffix " answer || answer=""
    else
        answer=""
    fi
    answer="${answer#\"${answer%%[![:space:]]*}\"}"
    answer="${answer%\"${answer##*[![:space:]]}\"}"
    if [ -z "$answer" ]; then
        case "$default" in [yY]*) return 0 ;; *) return 1 ;; esac
    fi
    case "$answer" in [yY]*) return 0 ;; *) return 1 ;; esac
}

# ── 系统检测 ──
detect_os() {
    case "$(uname -s)" in
        Linux*)
            OS="linux"
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                DISTRO="$ID"
            else
                DISTRO="unknown"
            fi
            ;;
        Darwin*)
            OS="macos"
            DISTRO="macos"
            ;;
        *)
            OS="unknown"
            DISTRO="unknown"
            log_error "不支持的操作系统: $(uname -s)"
            exit 1
            ;;
    esac
    log_success "检测到系统: $OS ($DISTRO)"
}

# ── 安装 uv ──
install_uv() {
    if command -v uv &>/dev/null; then
        log_success "uv 已安装 ($(uv --version 2>/dev/null))"
        return 0
    fi
    if [ -x "$HOME/.local/bin/uv" ]; then
        export PATH="$HOME/.local/bin:$PATH"
        log_success "uv 已安装 ($($HOME/.local/bin/uv --version 2>/dev/null))"
        return 0
    fi
    log_info "安装 uv..."
    if curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null; then
        export PATH="$HOME/.local/bin:$PATH"
        log_success "uv 安装成功"
    else
        log_error "uv 安装失败"
        exit 1
    fi
}

# ── 检查依赖 ──
check_dependencies() {
    log_step "1/6 检查依赖"

    # Git
    if command -v git &>/dev/null; then
        log_success "Git: $(git --version | awk '{print $3}')"
    else
        log_error "Git 未安装"
        case "$DISTRO" in
            ubuntu|debian) log_info "  sudo apt update && sudo apt install git" ;;
            fedora)        log_info "  sudo dnf install git" ;;
            arch)          log_info "  sudo pacman -S git" ;;
            macos)         log_info "  brew install git" ;;
        esac
        exit 1
    fi

    # Python
    install_uv
    if "$HOME/.local/bin/uv" python find 3.11 &>/dev/null 2>&1; then
        log_success "Python 3.11+ 可用"
    else
        log_info "Python 3.11 未找到，uv 将自动下载..."
        "$HOME/.local/bin/uv" python install 3.11
    fi

    # Node.js
    if command -v node &>/dev/null; then
        log_success "Node.js: $(node --version)"
    else
        log_warn "Node.js 未安装（浏览器工具需要）"
        log_info "安装 Node.js: https://nodejs.org/en/download/"
    fi
}

# ── 克隆核心代码 ──
clone_hermes() {
    log_step "2/6 获取 Hermes 核心代码"

    if [ -d "$INSTALL_DIR/.git" ]; then
        log_info "核心代码已存在，更新中..."
        cd "$INSTALL_DIR"
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || log_warn "更新失败，使用现有版本"
    else
        log_info "克隆核心代码到 $INSTALL_DIR ..."
        mkdir -p "$(dirname "$INSTALL_DIR")"
        if git clone "$REPO_URL" "$INSTALL_DIR"; then
            log_success "核心代码克隆成功"
        else
            log_error "克隆失败！请检查网络或手动克隆："
            log_info "  git clone $REPO_URL $INSTALL_DIR"
            exit 1
        fi
    fi
}

# ── 安装 Python 依赖 ──
install_deps() {
    log_step "3/6 安装 Python 依赖"

    cd "$INSTALL_DIR"

    if [ -f "pyproject.toml" ]; then
        log_info "使用 uv 安装依赖..."
        "$HOME/.local/bin/uv" sync 2>&1 | tail -5
        log_success "Python 依赖安装完成"
    elif [ -f "requirements.txt" ]; then
        log_info "使用 pip 安装依赖..."
        "$HOME/.local/bin/uv" pip install -r requirements.txt 2>&1 | tail -5
        log_success "Python 依赖安装完成"
    else
        log_warn "未找到 pyproject.toml 或 requirements.txt"
    fi
}

# ── 配置 ──
setup_config() {
    log_step "4/6 配置"

    # 创建 .hermes 目录
    mkdir -p "$HERMES_HOME"

    # 复制配置模板
    if [ ! -f "$HERMES_HOME/config.yaml" ]; then
        if [ -f "$SCRIPT_DIR/config/config.yaml.example" ]; then
            cp "$SCRIPT_DIR/config/config.yaml.example" "$HERMES_HOME/config.yaml"
            log_success "config.yaml 已创建（模板）"
        fi
    else
        log_info "config.yaml 已存在，跳过"
    fi

    if [ ! -f "$HERMES_HOME/.env" ]; then
        if [ -f "$SCRIPT_DIR/config/.env.example" ]; then
            cp "$SCRIPT_DIR/config/.env.example" "$HERMES_HOME/.env"
            log_success ".env 已创建（模板）"
        fi
    else
        log_info ".env 已存在，跳过"
    fi

    echo ""
    log_warn "⚠️  请编辑以下文件填入你的 API Key："
    echo "   $HERMES_HOME/.env"
    echo "   $HERMES_HOME/config.yaml"
    echo ""

    if prompt_yes_no "是否现在编辑配置？" "no"; then
        ${EDITOR:-nano} "$HERMES_HOME/.env"
        ${EDITOR:-nano} "$HERMES_HOME/config.yaml"
    fi
}

# ── 安装自定义 Skills ──
install_skills() {
    log_step "5/6 安装自定义 Skills"

    # 复制到 hermes-agent 内置 skills 目录
    local target_dir="$INSTALL_DIR/skills"

    if [ -d "$SCRIPT_DIR/skills" ]; then
        for skill_dir in "$SCRIPT_DIR/skills"/*/; do
            skill_name=$(basename "$skill_dir")
            if [ -d "$skill_dir" ]; then
                cp -r "$skill_dir" "$target_dir/$skill_name" 2>/dev/null && \
                    log_success "Skill '$skill_name' 已安装" || \
                    log_warn "Skill '$skill_name' 安装失败"
            fi
        done
    fi

    # 也复制到外部 skills 目录
    mkdir -p "$HERMES_HOME/skills"
    if [ -d "$SCRIPT_DIR/skills" ]; then
        cp -r "$SCRIPT_DIR/skills"/* "$HERMES_HOME/skills/" 2>/dev/null
        log_success "Skills 已复制到 $HERMES_HOME/skills/"
    fi
}

# ── 安装中文字体 ──
install_fonts() {
    log_step "6/6 安装中文字体（可选）"

    if prompt_yes_no "是否安装中文字体（用于 PPT/PDF 生成）？" "yes"; then
        case "$DISTRO" in
            ubuntu|debian)
                sudo apt update -qq && sudo apt install -y -qq fonts-wqy-microhei fonts-noto-cjk 2>/dev/null && \
                    log_success "中文字体安装完成" || \
                    log_warn "字体安装失败（可能需要 sudo）"
                ;;
            fedora)
                sudo dnf install -y wqy-microhei-fonts google-noto-cjk-fonts 2>/dev/null && \
                    log_success "中文字体安装完成" || \
                    log_warn "字体安装失败"
                ;;
            arch)
                sudo pacman -S --noconfirm wqy-microhei noto-fonts-cjk 2>/dev/null && \
                    log_success "中文字体安装完成" || \
                    log_warn "字体安装失败"
                ;;
            macos)
                log_info "macOS 已内置中文字体"
                ;;
            *)
                log_warn "未知系统，请手动安装中文字体"
                ;;
        esac
    fi
}

# ── 验证安装 ──
verify_install() {
    echo ""
    log_step "部署完成！验证安装"

    echo ""
    echo -e "${BOLD}安装信息：${NC}"
    echo "  Hermes Home:   $HERMES_HOME"
    echo "  Install Dir:   $INSTALL_DIR"
    echo "  Python:        $($HOME/.local/bin/uv python find 3.11 2>/dev/null || echo 'N/A')"
    echo "  Node.js:       $(node --version 2>/dev/null || echo '未安装')"
    echo ""

    echo -e "${BOLD}已安装的 Skills：${NC}"
    for skill_dir in "$SCRIPT_DIR/skills"/*/; do
        skill_name=$(basename "$skill_dir")
        if [ -f "$skill_dir/SKILL.md" ]; then
            echo "  ✅ $skill_name"
        fi
    done

    echo ""
    echo -e "${BOLD}下一步：${NC}"
    echo "  1. 编辑配置：nano $HERMES_HOME/.env"
    echo "  2. 启动 Agent：cd $INSTALL_DIR && uv run hermes setup"
    echo "  3. 开始使用：uv run hermes"
    echo ""
    echo -e "${GREEN}${BOLD}🐱 部署完成！喵~${NC}"
    echo ""
}

# ── 主流程 ──
main() {
    print_banner
    detect_os
    check_dependencies
    clone_hermes
    install_deps
    setup_config
    install_skills
    install_fonts
    verify_install
}

main "$@"
