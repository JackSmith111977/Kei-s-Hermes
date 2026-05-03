#!/bin/bash
# 安装 Chrome 浏览器（用于 web-access skill）
set -e

echo "→ 检测系统..."
case "$(uname -s)" in
    Linux*)
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO="$ID"
        fi
        case "$DISTRO" in
            ubuntu|debian)
                echo "→ 安装 Chrome (Debian/Ubuntu)..."
                wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb
                sudo dpkg -i /tmp/chrome.deb || sudo apt install -f -y
                rm -f /tmp/chrome.deb
                ;;
            fedora)
                echo "→ 安装 Chrome (Fedora)..."
                sudo dnf install -y google-chrome-stable
                ;;
            arch)
                echo "→ 安装 Chrome (Arch)..."
                sudo pacman -S --noconfirm chromium
                ;;
            *)
                echo "⚠️ 请手动安装 Chrome: https://www.google.com/chrome/"
                ;;
        esac
        ;;
    Darwin*)
        echo "→ 安装 Chrome (macOS)..."
        brew install --cask google-chrome
        ;;
esac

echo "✅ Chrome 安装完成"
google-chrome --version 2>/dev/null || chromium --version 2>/dev/null || echo "请验证安装"
