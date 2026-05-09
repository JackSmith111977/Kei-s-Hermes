# 飞书文档 API (docx/v1) 深度参考手册

> 基于飞书开放平台官方文档深度研究编写
> 更新日期: 2026-05-09
> 官方文档: https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/guide

---

## 一、核心概念

### 1.1 文档 (Document)

飞书新版文档 (docx) 是一棵 **Block 树**。每篇文档有唯一的 `document_id` 作为标识。

```text
Document = Block Tree
   └── Root: Page Block (document_id == block_id)
        ├── Text Block
        ├── Heading1 Block
        ├── Bullet Block
        │   └── Text Block (子块)
        └── Table Block
             ├── TableCell Block
             └── TableCell Block
```

**关键特性：**
- 新版文档 vs 旧版文档：新版基于 Block 树，旧版基于 Location
- 新版文档 URL: `https://{domain}/docx/{docx_token}`
- 旧版文档 URL: `https://{domain}/docs/{docs_token}`
- `document_id` 也是根 Page Block 的 `block_id`

### 1.2 块 (Block)

Block 是文档的最小构建单元。每个 Block 有：
- `block_id`: 唯一标识（创建时自动生成）
- `block_type`: 类型枚举（1~52）
- `parent_id`: 父块 ID（根节点 Page 无父块）
- `children`: 子块 ID 列表（树状结构）
- `comment_ids`: 评论 ID 列表
- BlockData: 根据 `block_type` 不同的数据结构（Text/Image/Table 等）

### 1.3 文本元素 (Text Element)

文本类 Block（Page/Text/Heading/Bullet/Ordered/Code/Quote/Todo）的内容由 Text Element 数组组成：

| Element 类型 | 用途 | 支持块类型 |
|-------------|------|-----------|
| `text_run` | 纯文本 | 所有文本类 Block |
| `mention_user` | @用户 | 文本类 |
| `mention_doc` | @文档 | 文本类 |
| `mention_page` | @页面 | 文本类 |
| `equation` | 公式 | 文本类 |
| `inline_block` | 内联块 | 文本类（仅移动/删除） |
| `inline_file` | 内联文件 | 文本类（仅移动/删除） |
| `reminder` | 日期提醒 | 文本类 |
| `button` | 按钮 | 文本类 |
| `intero_text` | 国际化文本 | 文本类 |

### 1.4 文档版本 (Revision)

- 创建时 revision_id = 1
- 每次编辑操作（创建/更新/删除 Block）递增
- 查询时 `document_revision_id=-1` 表示最新版本
- 查询历史版本需持有编辑权限

---

## 二、API 完整参考

### 2.1 文档管理 API

#### 2.1.1 创建文档
- **场景**: 创建一篇全新的空文档
- **端点**: `POST /open-apis/docx/v1/documents`
- **频率限制**: 3次/秒（特殊频控）
- **权限**: `docx:document` 或 `docx:document:create`
- **请求体**:
```json
{
  "title": "文档标题",          // 可选，≤800字符
  "folder_token": "fldbcxxx"   // 可选，指定文件夹
}
```
- **注意**: ⚠️ **不支持带内容创建！** 需后续创建 Block。基于模板创建需用 `copy` 接口。
- **响应**: `document_id`, `revision_id`, `title`, `display_setting`, `cover`

#### 2.1.2 获取文档基本信息
- **场景**: 获取文档标题、版本号、展示设置（不需要文档内容时使用）
- **端点**: `GET /open-apis/docx/v1/documents/{document_id}`
- **频率**: 5次/秒
- **权限**: `docx:document` 或 `docx:document:readonly`
- **响应**: 文档元信息 + `display_setting`（展示作者/创建时间/访问量等）

#### 2.1.3 获取文档纯文本内容
- **场景**: 只需文本内容，不需要富文本格式时使用（如全文搜索、摘要生成）
- **端点**: `GET /open-apis/docx/v1/documents/{document_id}/raw_content`
- **频率**: 5次/秒
- **权限**: `docx:document` 或 `docx:document:readonly`
- **参数**: `lang`（可选，指定 @用户 的语言：0=中文名/1=英文名）
- **响应**: 纯文本字符串（不包含格式信息）

#### 2.1.4 获取云文档内容 (Markdown 导出)
- **场景**: 需要导出文档为 Markdown 格式（用于迁移、备份）
- **端点**: `GET /open-apis/docs/v1/content?doc_token={token}&doc_type=docx&content_type=markdown`
- **频率**: 5次/秒
- **权限**: `docs:document.content:read`
- **注意**: 这是 `/docs/` v1 接口，不是 `/docx/` v1 接口

#### 2.1.5 复制文档（基于模板创建文档）
- **场景**: 基于已有文档创建副本（推荐方案，因创建文档不支持带内容）
- **端点**: `POST /open-apis/drive/v1/files/{file_token}/copy`
- **权限**: `drive:drive`
- **请求体**:
```json
{
  "name": "副本名称",
  "type": "docx",
  "folder_token": "fldbcxxx"
}
```

### 2.2 Block 读取 API

#### 2.2.1 获取文档所有 Block
- **场景**: 遍历整篇文档的结构（用于文档解析、内容迁移、结构分析）
- **端点**: `GET /open-apis/docx/v1/documents/{document_id}/blocks`
- **频率**: 5次/秒
- **权限**: `docx:document` 或 `docx:document:readonly`
- **参数**: `page_size` (默认500), `page_token` (分页), `document_revision_id` (版本)
- **响应**: Block 数组（每项含 block_type, parent_id, children, BlockData）
- **使用提示**: ⚠️ 分页返回，需处理 page_token 直到无更多数据

#### 2.2.2 获取单个 Block
- **场景**: 获取文档中某个特定 Block 的富文本内容（如查看某段落的内容）
- **端点**: `GET /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}`
- **频率**: 5次/秒
- **参数**: `document_revision_id`（默认 -1 表示最新版本）
- **响应**: 单个 Block 完整数据

#### 2.2.3 获取所有子块
- **场景**: 获取某个 Block 下的所有子块（如获取表格的所有单元格）
- **端点**: `GET /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children`
- **参数**: `page_size`, `page_token`, `document_revision_id`, `with_descendants`
- **`with_descendants`**: 
  - `false`（默认）: 仅返回直接子块
  - `true`: 先序遍历返回所有子孙块（含当前块）

### 2.3 Block 写入 API

#### 2.3.1 创建 Block（批量添加子块）
- **场景**: 在指定 Block 下批量插入新 Block 内容（仅同级，不支持嵌套）
- **端点**: `POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children?document_revision_id=-1`
- **频率**: 单文档 **3次/秒**（所有编辑操作共享此限制）
- **权限**: `docx:document` 或 `docx:document:write_only`
- **请求体**:
```json
{
  "index": 0,            // 插入位置，0=开头，-1=末尾
  "children": [
    {
      "block_type": 2,   // Text Block
      "text": {
        "elements": [{"text_run": {"content": "内容"}}],
        "style": {}
      }
    }
  ]
}
```
- **限制**: 此接口只创建**同级**子块，不支持嵌套；如需嵌套用 descendant 接口

#### 2.3.2 创建嵌套 Block（⭐ 核心接口）
- **场景**: 需要创建有父子关系的嵌套内容（如表格+单元格、分栏、高亮块、Markdown 导入）
- **端点**: `POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/descendant`
- **频率**: 单文档 3次/秒
- **权限**: `docx:document` 或 `docx:document:write_only`
- **请求体核心**: 需使用 `children_id` 临时 ID 机制
```json
{
  "index": -1,
  "children_id": ["cell1", "cell2"],
  "descendants": [
    {
      "block_id": "cell1",
      "block_type": 32,     // TableCell
      "table_cell": {},
      "children": ["cell1_text"]
    },
    {
      "block_id": "cell1_text",
      "block_type": 2,      // Text
      "text": {"elements": [{"text_run": {"content": "单元格内容"}}]},
      "children": []
    }
  ]
}
```
- **注意**: 
  - 只有第一级子块写在 `children_id` 里
  - 所有有父子关系的块（含嵌套子块的子块）都写在 `descendants` 里
  - 单次最多 **1000 个块**
  - GridColumn/TableCell/Callout **至少需要一个空的 Text Block** 作为子块
  - 响应中 `block_id_relations` 映射临时 ID 与实际 ID

#### 2.3.3 更新 Block
- **场景**: 更新单个 Block 的内容/样式（如替换图片、合并表格单元格）
- **端点**: `PATCH /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}`
- **频率**: 单文档 3次/秒
- **权限**: `docx:document` 或 `docx:document:write_only`
- **支持的操作类型**:

| 请求体字段 | 用途 | 支持类型 |
|-----------|------|---------|
| `update_text_elements` | 仅更新文本内容 | 文本类 Block |
| `update_text_style` | 仅更新文本样式 | 文本类 Block |
| `update_text` | 同时更新文本内容和样式 ⭐ | 文本类 Block |
| `replace_image` | 替换图片素材 | Image Block |
| `replace_file` | 替换文件素材 | File Block |
| `insert_table_rows` | 插入表格行 | Table Block |
| `insert_table_columns` | 插入表格列 | Table Block |
| `delete_table_rows` | 删除表格行 | Table Block |
| `delete_table_columns` | 删除表格列 | Table Block |
| `delete_grid_column` | 删除分栏列 | Grid Block |
| `merge_table_cells` | 合并表格单元格 | Table Block |
| `update_task` | 更新任务状态 | Task Block |

> 💡 **推荐**：使用 `update_text` 替代单独的 `update_text_elements` 或 `update_text_style`，一次操作搞定内容+样式。

#### 2.3.4 批量更新 Block
- **场景**: 一次请求更新多个 Block（如批量替换文本、批量合并表格单元格）
- **端点**: `PATCH /open-apis/docx/v1/documents/{document_id}/blocks/batch_update`
- **请求体**:
```json
{
  "requests": [
    {
      "block_id": "doxcnk0i44...",
      "merge_table_cells": {
        "row_start_index": 0, "row_end_index": 1,
        "column_start_index": 0, "column_end_index": 2
      }
    },
    {
      "block_id": "doxcn0K8iGS...",
      "update_text_elements": {
        "elements": [{"text_run": {"content": "Hello"}}]
      }
    }
  ]
}
```

#### 2.3.5 删除 Block
- **场景**: 删除文档中的一段内容（通过索引区间批量删除）
- **端点**: `DELETE /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children/batch_delete`
- **权限**: `docx:document`（只此权限—⚠️ write_only 不适用！）
- **参数+请求体**:
```json
DELETE ?document_revision_id=-1
{
  "start_index": 0,
  "end_index": 2    // 删除 0~1 两个子块（左闭右开）
}
```
- ⚠️ **限制**:
  - 不支持删除 Table 行列（需用 PATCH update）
  - 不支持删除 Grid 分栏列（需用 PATCH）
  - 不支持删除 TableCell/GridColumn/Callout 的全部子块

### 2.4 文档转换/导入 API

#### 2.4.1 Markdown/HTML 转换为文档块 ⭐
- **场景**: 将外部 Markdown/HTML 内容导入飞书文档
- **端点**: `POST /open-apis/docx/v1/documents/blocks/convert`
- **频率**: 1次/秒
- **权限**: `docx:document.block:convert`
- **请求体**:
```json
{
  "content_type": "markdown",  // 或 "html"
  "content": "# 标题\n\n内容..."
}
```
- **支持转换**: 文本、h1~h9、无序列表、有序列表、代码块、引用、待办事项、图片、表格
- **输出**: 带有父子关系的 Block 列表 + `first_level_block_ids`（临时 ID）
- **完整的导入流程**: `创建文档 → convert → (可选去 merge_info) → descendant 插入`
- ⚠️ **注意事项**:
  - 表格转换后需去除 `merge_info` 字段（只读属性，会报错 code=1770001）
  - 图片需额外调用 `medias/upload_all` + `replace_image`
  - 块过多时需分批插入（单次最多 1000 个）

> 🚨 **关键陷阱：表格树结构的正确构建方式**
>
> convert 输出的所有 block 的 `parent_id` **都为空**，层级关系通过 `children` 数组表达：
> - `Table` 的 `children` = TableCell ID 列表
> - `TableCell` 的 `children` = Text Block ID 列表（至少一个）
>
> **不要用 `parent_id` 重建树！** 正确做法是用 `children` 数组：
> ```python
> referenced = {c for b in blocks for c in b.get('children', [])}
> top_ids = [b['block_id'] for b in blocks if b['block_id'] not in referenced]
> ```
>
> 详见 `references/document-creation-best-practices.md`。

---

## 三、Block 类型完整对照表

### 文本类 Block

| block_type | 名称 | BlockData | 可创建子块 | 说明 |
|:----------:|------|-----------|:----------:|------|
| 1 | Page | Text | ✅ | 页面根 Block，block_id = document_id |
| 2 | Text | Text | ✅ | 普通文本段落 |
| 3~11 | Heading1~9 | Text | ✅ | 1~9 级标题 |
| 12 | Bullet | Text | ✅ | 无序列表 |
| 13 | Ordered | Text | ✅ | 有序列表 |
| 14 | Code | Text | ✅ | 代码块 |
| 15 | Quote | Text | ✅ | 引用 |
| 17 | Todo | Text | ✅ | 待办事项 |

### 容器类 Block（必须有子块）

| block_type | 名称 | BlockData | 可创建子块 | 说明 |
|:----------:|------|-----------|:----------:|------|
| 24 | Grid | Grid | ✅ | 分栏，需含 GridColumn 子块 |
| 25 | GridColumn | GridColumn | ✅ | 分栏列，至少1个空 Text |
| 31 | Table | Table | ✅ | 表格，需含 TableCell 子块 |
| 32 | TableCell | TableCell | ✅ | 表格单元格，至少1个空 Text |
| 19 | Callout | Callout | ✅ | 高亮块，至少1个空 Text |
| 34 | QuoteContainer | QuoteContainer | ✅ | 引用容器 |
| 33 | View | View | ✅ | 视图 |

### 媒体/数据类 Block（不可创建子块）

| block_type | 名称 | BlockData | 说明 |
|:----------:|------|-----------|------|
| 22 | Divider | Divider | 分割线，空结构体 `{}` |
| 27 | Image | Image | 图片，需 upload → replace_image |
| 23 | File | File | 文件 |
| 26 | Iframe | Iframe | 内嵌网页 |
| 18 | Bitable | Bitable | 多维表格（只读/跳转） |
| 30 | Sheet | Sheet | 电子表格 |
| 29 | Mindnote | Mindnote | 思维笔记 |
| 21 | Diagram | Diagram | 流程图 & UML |
| 20 | ChatCard | ChatCard | 会话卡片 |
| 35 | Task | Task | 任务 Block |

### 专项 Block

| block_type | 名称 | 说明 |
|:----------:|------|------|
| 36~39 | OKR 系列 | OKR，只读 |
| 40 | AddOns | 文档小组件 |
| 41 | JiraIssue | Jira 问题 |
| 42 | WikiCatalog | Wiki 子目录 |
| 43 | Board | 画板 |
| 44~47 | Agenda 系列 | 议程项/标题/内容 |
| 48 | LinkPreview | 链接预览 |
| 49 | SourceSynced | 源同步块，仅查询 |
| 50 | ReferenceSynced | 引用同步块，仅查询 |
| 51 | SubPageList | Wiki 新版子目录 |
| 52 | AITemplate | AI 模板，仅查询 |
| 999 | Undefined | 未支持 Block |

---

## 四、场景实战指引

### A: 从零创建完整文档
```text
1. POST /docx/v1/documents → 获取 document_id
2. POST blocks/{根}/children (block_type=3, heading1) → 创建标题
3. POST blocks/{根}/children (block_type=2, text) → 创建内容
4. POST blocks/{根}/children (block_type=12, bullet) → 创建列表
```
> 根 Page Block 的 block_id = document_id，向它添加子块即添加到文档末尾。

### B: 基于模板创建文档
```text
1. 获取模板 document_id
2. POST /drive/v1/files/{模板_id}/copy → 副本
3. PATCH /docx/v1/documents/{副本_id}/blocks/{根_id}
   → update_text_elements 更新占位内容
4. POST blocks/{根_id}/children → 追加新内容
```

### C: Markdown 导入飞书文档
```text
1. POST /docx/v1/documents → 创建空文档
2. POST /docx/v1/documents/blocks/convert → Markdown→Blocks
3. 处理表格：
   - 去除 Table 块的 merge_info（只读属性，会报错！）
   - 确保 TableCell 至少有一个子块（空 Text 也行）
4. 用 children 数组（而非 parent_id）确定层级关系：
   - convert 输出的表格块 children 数组已正确设置
   - parent_id 为空是正常现象！
5. POST blocks/{根}/descendant → 分批插入
   - 每批 ≤ 50 个顶级块
6. 如含图片 → medias/upload_all + replace_image
7. 数量 > 1000 → 分批插入
```

> ⚠️ **表格树结构关键**：convert 输出中 Table 的 `children` 数组引用了 TableCell ID，TableCell 的 `children` 引用了 Text Block ID。直接用这些 `children` 数组插入，不要尝试用 `parent_id` 重建树结构！详见 `references/document-creation-best-practices.md`。

### D: 读取文档内容
```text
纯文本:     GET /docx/v1/documents/{id}/raw_content
富文本:     GET /docx/v1/documents/{id}/blocks (分页遍历)
Markdown:   GET /docs/v1/content?doc_token={id}&doc_type=docx&content_type=markdown
局部读取:   GET /docx/v1/documents/{id}/blocks/{block_id}/children?with_descendants=true
```

### E: 插入图片
```text
1. convert 中包含图片引用 → 获得 Image Block
2. descendant 插入 Image Block
3. POST /drive/v1/medias/upload_all (以 Image BlockID 为 parent_node)
4. PATCH /docx/v1/documents/{id}/blocks/{image_id} → replace_image: {token: file_token}
```

### F: 表格操作
```text
创建:   POST descendant 创建 Table + TableCell + 空 Text Block
合并:   PATCH merge_table_cells {row/column_start_index, row/column_end_index}
加行:   PATCH insert_table_rows {row_index, row_size}
加列:   PATCH insert_table_columns {column_index, column_size}
删除行: PATCH delete_table_rows {row_index, row_count}
删除列: PATCH delete_table_columns {column_index, column_count}
```

### G: 更新文档标题
```text
PATCH /docx/v1/documents/{id}/blocks/{document_id} (根 Block)
→ update_text_elements → text_run 内容
```

### H: 高亮块 (Callout)
```text
POST descendant
→ block_type: 19, callout: {background_color, border_color, emoji_id}
→ 至少含一个空 Text Block 子块
```

### I: 分栏 (Grid)
```text
POST descendant → Grid → GridColumn → 内容
每个 GridColumn 至少有一个空 Text Block
```

---

## 五、权限与认证

| API | 所需权限 |
|-----|---------|
| 创建文档 | `docx:document` 或 `docx:document:create` |
| 读取文档 | `docx:document` 或 `docx:document:readonly` |
| 编辑 Block | `docx:document` 或 `docx:document:write_only` |
| Markdown 转换 | `docx:document.block:convert` |
| 复制文件 | `drive:drive` |
| Markdown 导出 | `docs:document.content:read` |

**访问凭证**: `tenant_access_token`（应用身份）/ `user_access_token`（用户身份）

### 常见错误码

| 错误码 | 含义 | 排查建议 |
|:------:|------|----------|
| 1770001 | invalid param | 确认参数合法性 |
| 1770002 | not found | 文档或 Block 不存在 |
| 1770003 | resource deleted | 资源已被删除 |
| 1770004 | too many blocks | 文档 Block 超上限 |
| 1770005 | too deep level | Block 层级超上限 |
| 1770006 | schema mismatch | 文档结构不合法 |
| 1770007 | too many children | 某 Block 子块超上限 |
| 1770031 | not support delete children | 该类型不支持删除子块 |
| 1770032 | forbidden | 无权限 |
| 1770040 | no folder permission | 无文件夹权限 |
| 1770041 | open schema mismatch | Block 父子关系不合法！最常见原因：TableCell 缺少子块
| 429 | rate limit | 频率限制，用退避重试 |

---

## 六、频率限制

| 维度 | 限制 |
|------|:----:|
| 创建文档 | 3次/秒 |
| 读取类 API | 5次/秒 |
| 编辑类 API (创建/更新/删除 Block) | 3次/秒/文档 |
| Markdown 转换 | 1次/秒 |
| Markdown 导出 | 5次/秒 |

---

## 七、新旧版文档差异

| 能力 | 新版 (docx) | 旧版 (doc) |
|------|-------------|------------|
| 数据结构 | Block 树 | Location + Element |
| 创建文档 | 不支持带内容 | 已废弃 |
| 编辑内容 | Block API | 旧版接口 |
| 内容定位 | block_id | startIndex + endIndex |
| URL 格式 | /docx/:token | /docs/:token |
| 文件类型 | docx | doc |

> ⚠️ **重要**：旧版接口已废弃，所有新开发应使用新版 docx API。
