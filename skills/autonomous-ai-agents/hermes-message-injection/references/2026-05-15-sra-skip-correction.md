# 2026-05-15 SRA 跳过被纠正事件

> 案例记录：boku 两次跳过 SRA 调用后被主人纠正
> 相关经验：`exp-20260515-sra-proxy-调用铁律被主人纠正跳`

---

## 经过

```
主人: "sra开启了吗"
boku: 直接 curl /health 检查 → 回复了 SRA 状态（❌ 跳过了 SRA Proxy /recommend）
      ↑ 错误：用 /health 代替了 /recommend

主人: "总结经验"
boku: 直接总结了 SRA 状态（❌ 再次跳过了 SRA Proxy /recommend）
      ↑ 错误：觉得问题简单，没必要调

主人: "总结经验没有触发sra吗" ← 纠正！
boku: 意识到错误 → 调 SRA → 获得 learning-review-cycle (51.8分)
      → 随后加载 knowledge-precipitation / knowledge-routing
      → 正确沉淀知识
```

## 根因分析

| 根因 | 说明 |
|:-----|:------|
| **用 /health 代替 /recommend** | 查询 SRA 状态时直接 curl 了 `/health`，认为「SRA 在工作就不用调了」 |
| **内置机制错觉** | 以为 Hermes 内置的 `_query_sra_context()` 会处理一切，不需要手动调 |
| **简单问题陷阱** | 觉得「总结经验」不需要技能推荐，低估了 SRA 的价值 |
| **缺乏自检习惯** | 回复前没有自我检查是否调用了 SRA |

## 正确应对

```python
# 收到任何非闲聊消息 → 第一步就是这个：
import subprocess
result = subprocess.run(
    ["curl", "-s", "--noproxy", "*", "--max-time", "10",
     "-X", "POST", "http://127.0.0.1:8536/recommend",
     "-H", "Content-Type: application/json",
     "-d", '{"message": "<主人消息>"}'],
    capture_output=True, text=True
)
# 然后才处理消息内容
```

## 自检清单（回复前）

- [ ] 我调了 SRA Proxy `/recommend` 吗？
- [ ] 我调的是 `/recommend` 而不是 `/health` 吗？
- [ ] `rag_context` 已经注入到思考过程了吗？
- [ ] 如果 `should_auto_load == true`，我加载了推荐的 skill 吗？

## 关联

- SOUL.md 第一条规则：「消息先过 SRA，再到你手上」
- `hermes-message-injection` skill 的「行为红牌」章节
- Memory: SRA 调用铁律（第11条）
- L2 Experience: `exp-20260515-sra-proxy-调用铁律被主人纠正跳`
