# systemd Drop-in 孤儿依赖诊断与修复

> 来自实际事故：2026-05-11 SRA 迁移后 Gateway 启动失败
> `Failed to start hermes-gateway.service: Unit srad.service not found`

## 事故症状

### 直接症状（系统管理视角）

```bash
$ systemctl --user start hermes-gateway
Failed to start hermes-gateway.service: Unit srad.service not found.
$ echo $?
5   # systemd 错误码：依赖的 unit 不存在
```

### Python CLI 视角（用户实际看到的）

当通过 `hermes gateway start` 触发时，用户看到的是完整的 Python 调用链 traceback：

```
Failed to start hermes-gateway.service: Unit srad.service not found.
Traceback (most recent call last):
  File "/home/ubuntu/.local/bin/hermes", line 8, in <module>
    sys.exit(main())
             ^^^^^^
  File "/home/ubuntu/.hermes/hermes-agent/hermes_cli/main.py", line 10870, in main
    args.func(args)
  File "/home/ubuntu/.hermes/hermes-agent/hermes_cli/main.py", line 1482, in cmd_gateway
    gateway_command(args)
  File "/home/ubuntu/.hermes/hermes-agent/hermes_cli/gateway.py", line 4461, in gateway_command
    return _gateway_command_inner(args)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ubuntu/.hermes/hermes-agent/hermes_cli/gateway.py", line 4578, in _gateway_command_inner
    systemd_start(system=system)
  File "/home/ubuntu/.hermes/hermes-agent/hermes_cli/gateway.py", line 2196, in systemd_start
    _run_systemctl(["start", get_service_name()], system=system, check=True, timeout=30)
  File "/home/ubuntu/.hermes/hermes-agent/hermes_cli/gateway.py", line 1263, in _run_systemctl
    return subprocess.run(_systemctl_cmd(system) + args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['systemctl', '--user', 'start', 'hermes-gateway']' returned non-zero exit status 5.
```

**诊断关键**：`hermes gateway start` 不会预先检查依赖链健康度。`systemd_start()` 中 `check=True` 导致非零退出直接抛异常。因此即使 systemd 的 `Requires=` 依赖缺失，错误也会表现为 CLI 崩溃而非清晰提示。

## 诊断流程

### 1. 查看单元依赖链

```bash
systemctl --user show hermes-gateway -p Requires,Wants,After,BindsTo
```

输出示例（问题状态）：
```
Requires=srad.service basic.target app.slice    # ← 有 srad.service！
Wants=network-online.target
After=srad.service network-online.target        # ← 有 srad.service！
```

### 2. 定位依赖来源

systemd 依赖可能来自三个地方：

| 来源 | 文件路径 | 检查方法 |
|:----|:--------|:---------|
| 主单元文件 | `~/.config/systemd/user/hermes-gateway.service` | `grep Requires \| Wants` |
| Drop-in 覆盖 | `~/.config/systemd/user/hermes-gateway.service.d/*.conf` | `ls` 查看所有文件 |
| 模板实例化 | — | `systemctl cat hermes-gateway` 看全部 |

**最常见原因**：某个 `.conf` 文件声明了 `Requires=xxx.service`，但 `xxx.service` 已被删除。

### 3. 确认缺失的单元

```bash
systemctl --user cat srad.service 2>&1
# → "No such file or directory" 或 "Unit srad.service not found"
systemctl --user list-unit-files | grep srad
# → 空（完全不存在）
```

## 修复步骤

### 短期修复：移除冲突的 drop-in 或改成 Wants=

```bash
# 找出声明了缺失依赖的 drop-in
cd ~/.config/systemd/user/hermes-gateway.service.d/
grep -l "Requires=srad" *.conf

# 方案 A：删除 drop-in（如果 SRA 不再需要）
rm sra-dep.conf

# 方案 B：改为 Wants=（如果 SRA 应该存在但暂时缺失）
# 编辑 sra-dep.conf
# Requires=srad.service → Wants=srad.service

# 重载并测试
systemctl --user daemon-reload
systemctl --user start hermes-gateway
```

### 长期预防：`Wants=` 替代 `Requires=`

```diff
  [Unit]
- Requires=srad.service    # 硬依赖 → 不存在就炸
+ Wants=srad.service       # 软依赖 → 不存在就忽略
  After=srad.service
```

### 彻底修复：恢复缺失的依赖单元

如果 `srad.service` 应该存在，创建它：

```ini
[Unit]
Description=My Service Daemon
After=network.target

[Service]
Type=simple
ExecStart=/path/to/binary
Restart=on-failure

[Install]
WantedBy=default.target
```

## Requires= vs Wants= 决策矩阵

| 服务关系 | 用 Requires= | 用 Wants= |
|:---------|:------------:|:---------:|
| B 是 A 的硬前置条件（A 无 B 就不能工作） | ✅ | ❌ |
| B 是 A 的可选增强（A 有降级策略） | ❌ | ✅ |
| B 是第三方微服务（可能被迁移/重命名） | ❌ | ✅ |
| 团队内约定「必须同时部署」 | ✅ | ❌ |
| 不确定未来 B 是否会被移除 | ❌ | ✅ |

## 配套清理：服务卸载三件套

卸载一个 systemd 服务时必须清理三样东西：

```bash
# 1. 停服并删除自身 unit
systemctl --user stop my-service
systemctl --user disable my-service
rm -f ~/.config/systemd/user/my-service.service

# 2. 删除自己创建的所有 drop-in（最重要！）
rm -f ~/.config/systemd/user/other-service.service.d/my-dep.conf

# 3. 重载
systemctl --user daemon-reload
```

## 验证闭环：完整恢复流程示例

以下是一个完整的「诊断 → 修复 → 验证」闭环，使用 SRA 作为示例：

```bash
# ── 诊断 ──
# 检查依赖链中是否有缺失的单元
sra dep-check
# 输出: sra-dep.conf 存在但 srad.service 不存在（孤儿配置）

systemctl --user show hermes-gateway -p Wants,After | grep srad
# Wants=srad.service network-online.target
# After=... srad.service ...

# ── 修复 ──
# 一键卸载（自动清理 sra-dep.conf）
sra uninstall --all
# 输出: ✅ 已删除 sra-dep.conf
#       ✅ systemd daemon-reload 完成
#       ✅ SRA 卸载完成！

# 验证 drop-in 已清除
ls ~/.config/systemd/user/hermes-gateway.service.d/sra-dep.conf
# → No such file or directory

# ── 重装 ──
cd ~/projects/sra
source venv/bin/activate
pip install --no-build-isolation -e .

# 重建 systemd 服务 + 依赖（用 Wants= 而非 Requires=）
systemctl --user daemon-reload
systemctl --user enable --now srad.service

# ── 验证 ──
sra dep-check
# 输出: ✅ 依赖链健康
#       📄 sra-dep.conf: 存在
#       🔗 依赖类型: Wants= (软依赖 ✅)
#       🏠 srad.service: 存在

systemctl --user status srad
# ● active (running)

curl --noproxy '*' http://127.0.0.1:8536/health
# {"status": "running", ...}
```

## 预防机制

1. **在 install.sh 的 `--uninstall` 分支**：自动清理自身 drop-in
2. **在 check-sra.py 等健康检查脚本**：检测 deprecated 的 `Requires=` 声明
3. **在部署文档中**：明确标注 drop-in 文件属主和清理方式
