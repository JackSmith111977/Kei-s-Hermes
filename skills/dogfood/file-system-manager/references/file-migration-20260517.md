# 根目录文件安全迁移记录（2026-05-17）

> 将 `~/.hermes/` 根目录的 13 个文件迁移到标准目录（state/、data/、cache/）的完整实战记录。

## 迁移原则

| 文件类别 | 迁移方式 | 原因 |
|:---------|:---------|:-----|
| **STATE**（运行时状态） | `mv → ln -s` **软链接** | Hermes 源码可能硬编码根目录路径 |
| **DATA**（持久数据） | `cp → mv → ln -s` **复制+软链接** | 确保数据安全，核实一致性后替换 |
| **CACHE**（缓存） | `mv → ln -s` **直接移动+软链接** | 下次调用自动重建 |

## 通用迁移模板

```bash
# STATE 类（软链接安全）
cd ~/.hermes
for f in sdd_state.json installed_packs.json learning_state.json; do
  [ -f "$f" ] && [ ! -L "$f" ] && \
    mv "$f" "state/$f" && \
    ln -s "state/$f" "$f" && \
    echo "✅ $f → state/$f"
done

# DATA 类（复制+一致性验证）
for f in auth.json kanban.db; do
  cp "$f" "data/$f" && \
  mv "$f" "data/$f.orig" && \
  ln -s "../data/$f" "$f" && \
  if cmp -s "data/$f" "data/$f.orig"; then
    rm "data/$f.orig" && echo "✅ $f verified"
  else
    echo "❌ $f MISMATCH — 需要手动检查"
  fi
done
```

## 迁移清单

| # | 文件 | 目标 | 方式 | 状态 |
|:-:|:-----|:-----|:----:|:----:|
| 1 | sdd_state.json | `state/` | `mv + ln -s` | ✅ |
| 2 | installed_packs.json | `state/` | `mv + ln -s` | ✅ |
| 3 | installed_opencode_packs.json | `state/` | `mv + ln -s` | ✅ |
| 4 | learning_state.json | `state/` | `mv + ln -s` | ✅ |
| 5 | health-report-state.json | `state/` | `mv + ln -s` | ✅ |
| 6 | gateway_state.json | `state/` | `mv + ln -s` | ✅ |
| 7 | auth.lock | `state/` | `mv + ln -s` | ✅ |
| 8 | processes.json | `state/` | `mv + ln -s` | ✅ |
| 9 | auth.json | `data/` | `cp + verify + ln -s` | ✅ |
| 10 | feishu_seen_message_ids.json | `data/` | `cp + verify + ln -s` | ✅ |
| 11 | kanban.db | `data/` | `cp + verify + ln -s` | ✅ |
| 12 | channel_directory.json | `data/` | `cp + verify + ln -s` | ✅ |
| 13 | models_dev_cache.json | `cache/` | `mv + ln -s` | ✅ |

## 验证方法

```bash
# 检查软链接完整性
cd ~/.hermes
for f in sdd_state.json installed_packs.json auth.json kanban.db; do
  if [ -L "$f" ] && [ -f "$(readlink -f "$f")" ]; then
    echo "✅ $f → $(readlink "$f") ($(wc -c < "$f") bytes)"
  else
    echo "❌ $f broken"
  fi
done
```

## 注意事项

1. **不要直接 `rm` 原文件** — 先用 `mv` 移走并创建软链接，确保 Hermes 运行时路径仍然有效
2. **不要用 `cp` 覆盖** — 文件可能正被 Hermes 进程使用
3. **DATA 类必须验证** — `cmp -s` 确保复制内容无误后再删除原文件
4. **state.db 不动** — 硬编码在 Hermes 源码中，不迁移
5. **不要用 batch mv** — 某些文件可能被 Hermes 进程锁定，逐个处理更安全
