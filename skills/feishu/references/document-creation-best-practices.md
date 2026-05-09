# 飞书文档创作避坑指南

> **经验来源**: 2026-05-09 实际创作中的教训总结
> **关联经验**: `exp-20260509-005` (文档创作教训总结)

---

## 一、表格插入的正确做法 (convert + descendant)

### ⚠️ 最常踩的坑：错误使用 parent_id 建树

**错误做法**：假设 convert 输出中 `parent_id` 包含父子关系信息，用它来重建树结构。

```python
# ❌ 错误：用 parent_id 确定顶级块
all_ids = {b['block_id'] for b in blocks}
real_first = [b for b in blocks if b.get('parent_id') not in all_ids]
```

**为什么错**：convert API 输出的**所有 block 的 parent_id 都为空**！这不是 bug，是设计如此。表格的层级关系通过 `children` 数组来表达。

### ✅ 正确做法：用 children 数组建树

```python
# ✅ 正确：用 children 数组（convert 已正确设置）
# 1. 找出所有被引用为子块的 block_id
referenced_as_child = set()
for b in blocks:
    for c in b.get('children', []):
        referenced_as_child.add(c)

# 2. 顶级块 = 未被任何 children 引用的块
top_ids = [b['block_id'] for b in blocks 
           if b['block_id'] not in referenced_as_child]
```

### 表格处理三步曲

```python
# Step 1: 转换
resp = requests.post('/docx/v1/documents/blocks/convert',
    json={'content_type': 'markdown', 'content': md_text})

# Step 2: 处理表格（插入前必须做！）
for b in blocks:
    # 2a: 去除 merge_info（只读属性，会报错 1770001）
    if b.get('block_type') == 31 and 'table' in b:
        if 'property' in b['table'] and 'merge_info' in b['table']['property']:
            del b['table']['property']['merge_info']
    
    # 2b: TableCell 必须有子块（否则报错 1770041）
    if b.get('block_type') == 32 and (not b.get('children') or len(b['children']) == 0):
        dummy_id = 'dummy_' + b['block_id'][:12]
        b['children'] = [dummy_id]
        blocks.append({
            'block_id': dummy_id,
            'block_type': 2,
            'text': {'elements': [{'text_run': {'content': ''}}], 'style': {}},
            'children': []
        })

# Step 3: 用 children 数组建树 + 分批插入
top_ids = find_top_blocks_via_children(blocks)
for batch in chunks(top_ids, 50):
    descendants = collect_descendants(batch, blocks)
    r = requests.post('/docx/v1/documents/{id}/blocks/{id}/descendant',
        json={'index': -1, 'children_id': batch, 'descendants': descendants})
```

---

## 二、文档创作必须的 Review 流程

### 创作前检查清单

- [ ] 输出格式确定（HTML / Feishu / PDF）
- [ ] 如果是飞书文档：先做最小测试用例（1 个表格）
- [ ] 如果是 HTML：先加载 visual-aesthetics + web-ui-ux-design
- [ ] 数据是否完整？是否需要 delegate_task 调查系统状态？

### 创作中检查

- [ ] 每个 API 调用前先理解返回值结构
- [ ] 不跳过困难部分（表格、复杂嵌套）
- [ ] 分段处理，每段独立 convert + insert
- [ ] 分批插入（每批 ≤ 50 个顶级块）

### 创作后验证

- [ ] 章节完整性：所有预期章节都在 raw_content 中
- [ ] 表格完整性：raw_content 长度 >= 预期值
- [ ] 无报错：insert 请求全部返回 code=0
- [ ] 视觉验证：截图或 vision_analyze 评分
- [ ] 本地备份存在

---

## 三、飞书文档 vs HTML 文档的选型决策

| 场景 | 推荐格式 | 原因 |
|:----|:--------|:-----|
| 需要在线协作/评论 | 飞书文档 | 原生协作能力 |
| 复杂表格/样式要求 | HTML | 完全 CSS 控制 |
| 需要离线查看 | HTML | 单文件自包含 |
| 需要打印/PDF | HTML+WeasyPrint | 打印优化可控 |
| 大量数据展示 | HTML | 表格渲染完美 |
| 需要侧边栏导航 | HTML | JS 实现灵活 |
| 自动化发送到聊天 | HTML | 作为文件附件发送 |
| 简单文本/列表 | 飞书文档 | 最快发布 |

---

## 四、关键技术陷阱速查

| 陷阱 | 症状 | 解决 |
|:----|:-----|:------|
| `parent_id` 为空 | 所有 block 都变成"顶级块" | 用 `children` 数组建树 |
| `merge_info` 未删除 | code=1770001 invalid param | 插入前必须删除 |
| `TableCell` 无子块 | code=1770041 schema mismatch | 添加空 Text 子块 |
| 一次插入 > 1000 块 | code=1770007 too many children | 分批，每批 ≤ 50 顶级块 |
| `tenant_access_token` 转所有权 | Access denied | 需 `docs:permission.member:transfer` |
| 手动用 `type=docx` 创建 Table | cells 数组需对应 | 建议用 convert API，自动处理 |
