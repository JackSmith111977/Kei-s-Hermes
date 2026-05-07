# Hermes 手动升级检查清单

> 基于 2026-05-07 v0.10.0 → v0.12.0 升级实战记录

## 1. 升级前准备

### 1.1 检查当前状态
```bash
hermes --version
cd ~/.hermes/hermes-agent && git log --oneline -3
```

### 1.2 备份自定义修改
```bash
mkdir -p ~/hermes_custom_backup
cd ~/.hermes/hermes-agent

# 备份 git diff（适用于已在 git 中管理的修改）
git diff > ~/hermes_custom_backup/modified_files.patch

# 备份新增文件（不在 git 中）
mkdir -p ~/hermes_custom_backup/new_files_originals/
for f in gateway/statusline.py tools/pollinations_image_tool.py tools/web_cache.py; do
  [ -f "$f" ] && cp "$f" ~/hermes_custom_backup/new_files_originals/
done

# 备份完整 patch（包含新增文件）
git stash push -m "custom-backup-before-upgrade"
```

## 2. 下载与解压

```bash
# 检查代理是否在运行
systemctl --user status mihomo | head -5

# 下载指定版本 tarball（替换 v0.12.0 为目标版本）
wget https://github.com/nousresearch/hermes-agent/archive/refs/tags/v0.12.0.tar.gz \
  -O /tmp/hermes_latest.tar.gz

# 解压
mkdir -p /tmp/hermes_new
cd /tmp/hermes_new
tar xzf /tmp/hermes_latest.tar.gz
# -> 解压到 hermes-agent-main/ 目录
```

## 3. 执行升级

```bash
cd ~/.hermes/hermes-agent

# 先 stash 当前修改（避免 rsync 混合新旧文件）
git stash push -m "backup-$(date +%Y%m%d_%H%M%S)"

# rsync 替换（关键：排除 .git, venv, __pycache__）
rsync -av --exclude='.git' --exclude='venv' --exclude='__pycache__' \
  /tmp/hermes_new/hermes-agent-main/ ./

# 重新安装依赖
source venv/bin/activate
pip install -e ".[all]" --break-system-packages

# 验证
hermes --version
```

## 4. 恢复自定义功能

### 4.1 检查自定义功能是否真正集成

升级后不能只看文件是否存在——有些功能即使文件保留了，**集成链路可能已断裂**。

```bash
# 检查状态栏脚注是否真正集成（文件存在是错觉！）
ls -la gateway/statusline.py                                # ✅ 文件存在
grep -n "from gateway.statusline" gateway/run.py             # ❌ 可能没有 → 未集成
grep -n "build_statusline" gateway/run.py                    # ❌ 可能没有 → 未集成

# 检查 Pollinations 生图是否已内置
ls -la tools/pollinations_image_tool.py
grep -n "pollinations_image_tool" tools/registry.py          # 检查是否注册

# 检查 Web 缓存是否已内置
ls -la tools/web_cache.py
grep -n "web_cache" tools/registry.py                        # 检查是否注册

# 检查 GPT Image 2
ls -la tools/image_generation_tool.py
grep -n "image_generation_tool" tools/registry.py

# 检查微信修复
grep -n "_is_stale_session_ret" gateway/platforms/weixin.py
```

**判断标准**：文件存在 + 被其他代码 import/注册 = 功能正常。只文件存在 = 死代码，需要手动恢复集成。

> 恢复网关钩子的详细步骤见 `references/reintegrating-gateway-hooks.md`

### 4.2 恢复飞书卡片 🐱小玛
修改文件：`gateway/platforms/feishu.py`

**需要添加/修改的内容：**

1. 添加正则常量（在 `_POST_CONTENT_INVALID_RE` 后面）：
   ```python
   _INTERACTIVE_CONTENT_INVALID_RE = re.compile(
       r"parse card json err|element exceeds the limit|template is not visible to app",
       re.IGNORECASE
   )
   ```

2. 添加 `_build_markdown_card_payload()` 和 `_build_text_card_payload()` 函数（在 `_build_markdown_post_rows` 函数之后）

3. 修改 `_build_outbound_payload()` 方法——返回 interactive card 替代 post/text

4. 在 `_send_message_inner` 方法中添加卡片发送失败的降级逻辑（interactive → post → text）

5. 在 `edit_message` 方法中添加卡片编辑失败的降级逻辑

**卡片结构**：
```json
{
  "config": {"wide_screen_mode": true},
  "header": {"title": {"tag": "plain_text", "content": "🐱 小玛"}, "template": "blue|red|orange"},
  "elements": [{"tag": "markdown", "content": "..."}]
}
```

### 4.3 恢复 SRA 技能推荐
修改文件：`run_agent.py` + `agent/prompt_builder.py`

- **prompt_builder.py**：在文件末尾添加 `build_sra_context_prompt()` 函数
- **run_agent.py**：
  - 在 `class AIAgent:` 之前添加 `_SRA_CACHE` 和 `_query_sra_context()` 函数
  - 在 `run_conversation` 方法中，用户消息构建前注入 SRA 上下文

### 4.4 从 Git Stash 恢复（替代方案）
如果升级后想直接应用旧 patch：
```bash
cd ~/.hermes/hermes-agent
git stash pop   # 可能有冲突
# 或者从备份 apply
git apply ~/hermes_custom_backup/modified_files.patch  # 可能报错（代码变化）
```

## 5. 升级后验证

```bash
# 5.1 版本确认
hermes --version

# 5.2 系统健康检查 + 自动修复
hermes doctor
hermes doctor --fix
# 自动修复的内容：
# - Config 版本迁移（v21 → v23）：添加缺失配置项，seed curator 默认值
# - WAL 文件 checkpoint（清理 WAL）
# - 添加 Skills Hub curator 配置

# 5.3 语法检查
cd ~/.hermes/hermes-agent
python3 -c "import py_compile; py_compile.compile('gateway/platforms/feishu.py', doraise=True); print('✅ feishu.py')"
python3 -c "import py_compile; py_compile.compile('run_agent.py', doraise=True); print('✅ run_agent.py')"
python3 -c "import py_compile; py_compile.compile('agent/prompt_builder.py', doraise=True); print('✅ prompt_builder.py')"

# 5.4 重启网关
systemctl --user restart hermes-gateway
journalctl --user -u hermes-gateway --since "30 sec ago" --no-pager | grep -E "Lark|weixin|platform|error" | head -10
```

## 6. 临时文件清理

```bash
# 升级完成后释放空间
rm -rf /tmp/hermes_latest.tar.gz
rm -rf /tmp/hermes_new/
rm -f /tmp/hermes-snap-*.sh
```

## 7. 已知注意事项

| 问题 | 对策 |
|------|------|
| Git TLS 错误（国内服务器） | 直接下载 GitHub tarball，用 rsync 替代 git pull |
| Config 版本过时 | `hermes doctor --fix` 自动迁移 |
| WAL 文件过大 | `hermes doctor --fix` 自动 checkpoint |
| 自定义修改被覆盖 | 升级前必须备份 patch，升级后手动恢复 |
| 辅助 LLM 无 Fallback | `config.yaml` 中 auxiliary 显式指定 provider: deepseek |
| 飞书卡片 API 兼容性 | 卡片失败自动降级为 post → 纯文本 |
