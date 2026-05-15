# SRA 安装脚本已知陷阱

> 来源: EPIC-004 安装验证 (2026-05-15)
> 环境: Ubuntu 24.04, Python 3.11, systemd

---

## 陷阱 1: Python 版本检查使用 `bc` 导致误判

**文件**: `scripts/install.sh:211`

**症状**: Python 3.11 被误判为「需要 Python >= 3.8」
```
[ERROR] 需要 Python >= 3.8，当前: 3.11
```

**根因**: `bc` 做十进制比较：`echo "3.11 < 3.8" | bc` → `1` (true)。  
`3.11` 作为十进制数确实小于 `3.8`，但作为版本号 `3.11 > 3.8`。

**修复**: 用 Python 元组比较替代 bc：
```bash
# 错误
if [[ $(echo "$PY_VERSION < 3.8" | bc) -eq 1 ]]; then

# 正确
if ! python3 -c "import sys; sys.exit(0 if (3,8) <= sys.version_info[:2] else 1)"; then
```

---

## 陷阱 2: PEP 668 — pip install --user 在 Ubuntu 23.04+ 上失败

**文件**: `scripts/install.sh:225`

**症状**: `pip install --user` 报错
```
error: externally-managed-environment
× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
```

**根因**: Ubuntu 23.04+ 的 PEP 668 阻止系统 Python 的 `pip install --user`。

**修复**: 添加 `--break-system-packages` 降级策略：
```bash
# 先试 --user，失败后加 --break-system-packages
pip install --user -e . 2>/dev/null || \
pip install --user --break-system-packages -e . 2>/dev/null || \
pip install -e . 2>/dev/null || \
pip install --break-system-packages -e .
```

**更好的长期方案**: 让 install.sh 自动创建 venv 后安装，而非直接使用系统 pip。

---

## 验证方法

每次修改 install.sh 后，在两种环境下测试：

```bash
# 测试 1: 源码目录内安装
cd ~/projects/sra
bash scripts/install.sh 2>&1 | tail -10
sra version
sra start
sra status
sra stop

# 测试 2: 卸载后重新安装（验证 clean install）
bash scripts/install.sh --uninstall
bash scripts/install.sh 2>&1 | tail -10
```

**核心 API 功能验证清单**（安装后逐一确认）：

```bash
sra version          # CLI 可用
sra start            # 守护进程启动
sra status           # 运行中 + 技能数
sra recommend "测试"  # 推荐功能
curl localhost:8536/health      # HTTP API 健康
curl -X POST localhost:8536/recommend -d '{"message":"test"}'  # POST 推荐
curl -X POST localhost:8536/validate -d '{"tool":"write_file","args":{"path":"test.py"}}'  # 校验
sra stop             # 正常停止
```
