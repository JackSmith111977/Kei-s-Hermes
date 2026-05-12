# SDD 工作流已知缺口与改进路线图

> 来源: SDD 工作流深度审计 (2026-05-12)
> 研究范围: 飞书卡片交互能力 + 文档质量检查框架 + 学习工作流集成
> 关联 SKILL.md: sdd-workflow §六、§八

---

## 一、当前流程审计

### 1.1 v1.0 状态机

```
CREATE ──→ REVIEW ──→ APPROVED ──→ IN PROGRESS ──→ COMPLETED ──→ ARCHIVED
```

### 1.2 识别到的三个缺口

| 编号 | 缺口 | 位置 | 具体问题 |
|:----:|:-----|:-----|:---------|
| **Gap A** | 需求澄清缺失 | CREATE 之前 | 主人提出任务后，boku 直接按理解写 Spec，没有确认需求理解的准确性。可能导致返工。 |
| **Gap B** | 技术调研缺失 | CREATE 之前 | 对于不确定的领域，boku 没有系统化的调研机制就写文档。可能导致文档质量依赖已有知识储备。 |
| **Gap C** | 质量检查缺失 | CREATE 之后 | 文档写完后直接提交 REVIEW，缺少系统化的自检和质量门禁。主人需要花更多时间审阅。 |

---

## 二、飞书卡片交互能力研究

### 2.1 能力矩阵

| 组件 | tag | 交互类型 | 回调数据 | 是否适用需求澄清 |
|:----|:----|:---------|:---------|:---------------:|
| 按钮 | `button` | `callback` / `open_url` | `action.value` (自定义 object) + `tag: "button"` | ✅ 选择选项 |
| 列表选择器 | `selectMenu` | `callback` | `action.option` (选中项) + `tag: "select_static"` | ✅ 多项选择 |
| 输入框 | `input` | `callback` | `action.input_value` (文本) + `tag: "input"` | ✅ 自由输入 |
| 表单容器 | `form` | `callback` (提交时统一触发) | `action.form_value` (所有组件数据) | ✅ 组合方案 |
| 日期选择器 | `datePicker` | `callback` | `action.option` (日期) | ❌ |
| 折叠按钮组 | `overflow` | `callback` / `open_url` | `action.option` (选中项) | ❌ |

### 2.2 回调机制详解

**配置方式**：在组件 JSON 中添加 `behaviors` 字段：
```json
{
  "behaviors": [
    {
      "type": "callback",
      "value": {"action": "my_custom_action"}
    }
  ]
}
```

**回调数据示例**：
```json
{
  "schema": "2.0",
  "event_type": "card.action.trigger",
  "operator": {
    "open_id": "ou_xxx",
    "user_id": "xxx",
    "union_id": "on_xxx"
  },
  "action": {
    "value": {"action": "my_custom_action"},
    "tag": "button",
    "form_value": {"notes_input": "自定义输入"},
    "name": "Button_xxx"
  },
  "context": {
    "open_message_id": "om_xxx",
    "open_chat_id": "oc_xxx"
  },
  "token": "c-xxx"
}
```

**响应要求**：服务端必须在 **3 秒内** 返回 HTTP 200，否则客户端显示错误。

### 2.3 当前网关限制

- Hermes 飞书网关 (`gateway/platforms/feishu.py`) 只输出**静态卡片**（markdown + header）
- 要实现交互卡片，需要：
  1. 修改 `_build_markdown_card_payload()` 生成带交互组件的卡片 JSON
  2. 在飞书开发者后台配置**消息卡片请求网址**（卡片回调 webhook）
  3. 在网关中新增 `card.action.trigger` 回调处理路由
  4. 注意：**仅通过应用发送的卡片支持回调**，自定义机器人发送的卡片不支持

### 2.4 实施路径

| Phase | 内容 | 成本 | 前置条件 |
|:------|:-----|:----:|:---------|
| **P3** | 改造 `feishu.py` 生成交互卡片 | ~4h | 熟悉 feishu.py 架构 |
| **P4** | 网关回调路由 + webhook 配置 | ~4h | 飞书开发者后台配置权限 |

---

## 三、文档质量检查框架

### 3.1 检查维度

改编自 9×1 校验模型（三维度 × 三层次）：

| 维度\层次 | 结构层 | 内容层 | 体系层 |
|:---------|:-------|:-------|:-------|
| **一致性** | 格式统一（命名/元数据/模板） | 术语一致（前后不矛盾） | 定位一致（与 Epic 不冲突） |
| **逻辑性** | 结构合理（层级/顺序） | 内容自洽（无矛盾） | 关联逻辑合理（引用链完整） |
| **完整性** | 要素齐全（必需字段） | 信息充分（无遗漏） | 价值闭环（AC 可验证） |

### 3.2 自动化程度

| 层次 | AI 优势 | 人类优势 | 协作方式 |
|:-----|:--------|:---------|:---------|
| **结构层** | 规则检查、格式验证 | 标准制定、异常判断 | AI 执行，人类审核 |
| **内容层** | 一致性检查、错误发现 | 准确性判断、价值评估 | AI 辅助，人类主导 |
| **体系层** | 关联分析、趋势识别 | 战略判断、价值决策 | 人类决策，AI 支持 |

### 3.3 质量门禁流程

```text
文档/CREATE 完成
    ↓
🟢 P0 结构检查（自动）
  ├── story_id 格式正确？
  ├── title 非空？
  ├── acceptance_criteria 每个可验证？
  ├── out_of_scope 已定义？
  └── spec_references 完整？
    ↓ 通过 → 进入 P1
    ↓ 失败 → 打回修改

🟡 P1 内容检查（AI 自查）
  ├── 技术描述无事实错误？
  ├── 术语使用一致？
  └── 信息覆盖完整？
    ↓ 通过 → 进入 P2
    ↓ 失败 → 打回修改

🔵 P2 体系检查（doc-alignment + 人工）
  ├── doc-alignment --verify 通过？
  └── 主人确认价值合理？
    ↓ 全部通过
✅ 质量门禁通过 → 提交 REVIEW
```

---

## 四、改进后 SDD v2.0 状态机设计

### 4.1 9 状态状态机

```text
CLARIFY ──→ RESEARCH ──→ CREATE ──→ QA_GATE ──→ REVIEW ──→ APPROVED ──→ IN PROGRESS ──→ COMPLETED ──→ ARCHIVED
 需求澄清    技术调研      写文档      质量检查     主人审阅    批准开发      实现中           已完成        归档
```

### 4.2 新增状态操作

| 状态 | 操作 | 前置条件 | 产出物 | 回退目标 |
|:-----|:-----|:---------|:-------|:--------|
| CLARIFY | boku 输出需求理解 → 主人确认 | 任务提出 | `~/.hermes/docs/req_clarification/{task_id}.md` | 任务起点 |
| RESEARCH | 执行 learning-workflow STEP 1-3 | CLARIFY 通过 | `~/.hermes/learning/` 下的调研笔记 | CLARIFY |
| QA_GATE | P0→P1→P2 三检 | CREATE 完成 | 质量检查报告 | CREATE |

### 4.3 回退机制

```text
CLARIFY 不通过 → 回到任务起点，重新理解需求
  RESEARCH 发现新方向 → 回到 CLARIFY 重新确认
    QA_GATE P0 失败 → 回到 CREATE 修改
    QA_GATE P1 失败 → 回到 CREATE 修改
    QA_GATE P2 失败 → 回到 CREATE 修改
      REVIEW 不通过 → 回到 RESEARCH 或 CLARIFY（根据拒绝原因）
```

---

## 五、需求澄清交互设计

### 5.1 Phase 1（使用 clarify 工具）

```text
boku 输出需求理解摘要
    ↓
使用 clarify 工具呈现选择题：
  ├── ✅ "需求理解正确，开始吧"
  ├── 🔄 "需要调整方向"
  └── 💬 "我有补充说明"（自由输入）
    ↓
主人确认 → 进入 RESEARCH 或直接 CREATE
```

### 5.2 Phase 3（使用飞书交互卡片）

卡片 JSON 设计方案（JSON 2.0 格式）：

```json
{
  "config": {"wide_screen_mode": true},
  "header": {
    "title": {"tag": "plain_text", "content": "📋 需求确认"},
    "template": "blue"
  },
  "elements": [
    {
      "tag": "markdown",
      "content": "主人，boku 对您的需求理解如下：\n\n**任务**: {task_title}\n\nboku 的理解：\n{understanding_summary}\n\n您觉得这个方向对吗？"
    },
    {"tag": "hr"},
    {
      "tag": "action",
      "actions": [
        {
          "tag": "button",
          "text": {"tag": "plain_text", "content": "✅ 方向正确"},
          "type": "primary",
          "value": {"action": "clarify_confirm"}
        },
        {
          "tag": "button",
          "text": {"tag": "plain_text", "content": "🔄 需要调整"},
          "type": "default",
          "value": {"action": "clarify_adjust"}
        }
      ]
    },
    {
      "tag": "input",
      "name": "user_feedback",
      "label": {"tag": "plain_text", "content": "补充说明（可选）"},
      "placeholder": {"tag": "plain_text", "content": "输入您的补充需求..."}
    }
  ]
}
```

---

## 六、参考来源

| 主题 | 来源 | URL |
|:-----|:-----|:----|
| 飞书卡片交互配置 | 飞书开放平台 | https://open.feishu.cn/document/feishu-cards/configuring-card-interactions |
| 按钮组件 | 飞书开放平台 | https://open.feishu.cn/document/feishu-cards/card-components/interactive-components/button |
| 输入框组件 | 飞书开放平台 | https://open.feishu.cn/document/feishu-cards/card-components/interactive-components/input |
| 列表选择器 | 飞书开放平台 | https://open.feishu.cn/document/ukTMukTMukTM/uIzNwUjLycDM14iM3ATN |
| 卡片回调通信 | 飞书开放平台 | https://open.feishu.cn/document/feishu-cards/card-callback-communication |
| 处理卡片回调 | 飞书开放平台 | https://open.feishu.cn/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/handle-card-callbacks |
| 文档校验规范 | Deepractice | https://docs.deepractice.ai/zh/practice/content-system/document-validation-standard |
| AI 技术文档审校 | Intelliparadigm | https://intelliparadigm.com/article/weixin_28713299/2019962 |
| 文档生命周期管理 | AppFox/Confluence | https://docs.appfox.io/confluence-workflows/document-lifecycle-management-in-confluence |
| Review Workflow | SmartWeb | https://www.smartweb.jp/en/glossary/review-workflow/ |
| Semcheck 工具 | 开源 | https://www.xugj520.cn/archives/ai-code-document-sync.html |
