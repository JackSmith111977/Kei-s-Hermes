# 🔬 验证 PR 声称 vs 实际行为

> 从 SRA PR #17 的实战中总结的模式——commit message 声称 jieba 能把「公众号」完整分词，
> 但实际运行发现 jieba 默认词典把它拆成了「公众」+「号」。

## 为什么这很重要

PR 的描述和 commit message 可能包含**不准确的行为、性能或正确性声明**。
不要轻信——必须通过运行实际代码路径来验证。

尤其是在以下场景最容易出现声称不符实：
- **新依赖的引入**（作者可能没在干净环境测试）
- **示例/测试数据**（手写的示例可能过于理想化）
- **性能改进**（可能只在作者特定的硬件/环境上成立）
- **兼容性声明**（声称「兼容 Python 3.9」但用了 PEP 604 语法）

## 验证步骤

### Step 1：提取 PR 中的行为声明

```bash
# 查看 commit message 和 PR body 中的示例
gh pr view <NUMBER> --json title,body,commits | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('=== PR Body ===')
print(d['body'])
print('\\n=== Commits ===')
for c in d['commits']:
    print(f'{c[\"messageHeadline\"]}')
    print(f'  {c[\"messageBody\"][:200]}')
"
```

标记所有**可验证的声明**：
- ❌ 主观判断（「更好」「更清晰」）→ 不可验证
- ✅ 具体示例（「输入 X 产生 Y」）→ **必须验证**
- ✅ 性能数字（「快 50%」）→ **必须验证**
- ✅ 兼容性（「支持 Python 3.9」）→ **必须验证**

### Step 2：安装新依赖

```bash
# 检查新增依赖
grep -A5 "dependencies\|optional-dependencies" pyproject.toml

# 安装所有新增依赖（含可选依赖）
pip install -e ".[chinese,dev,test]" 2>&1 | tail -5
pip install <PR特有的新包>
```

### Step 3：重现声称的行为

```python
# Python 验证脚本模板
import sys

# 对应 PR 的输入
input_data = "PR commit message 中的示例输入"

# 执行实际代码路径
# （从 PR diff 中复制函数，或用 read_file 读取变更文件）
from skill_advisor.indexer import SkillIndexer
import tempfile

with tempfile.TemporaryDirectory() as td:
    idx = SkillIndexer("/dev/null", td)
    result = idx.extract_keywords(input_data)
    
    # 检查声称的输出
    expected_words = ["公众号"]  # PR 声称的词
    for w in expected_words:
        if w in result:
            print(f"✅ PR 声称正确: {w} 在结果中")
        else:
            print(f"❌ PR 声称不准确: {w} 不在结果中")
            print(f"   实际结果: {sorted(result)}")
```

### Step 4：文档不一致

```
| 位置 | PR 声称 | 实际行为 | 严重度 |
|:-----|:--------|:---------|:------:|
| commit message 示例 | jieba 产生 '公众号' | jieba 产生 '公众' + '号' | 🔴 不准确 |
| PR body 声称 | CI 自动测试 jieba 路径 | CI 不装 [chinese] 依赖 | 🔴 遗漏 |
```

### Step 5：在审查报告中引用

将发现的偏差写入审查报告的 Critical 或 Warning 部分，要求作者修正：

```markdown
### 🔴 Critical: Commit message 示例不准确

Commit message 声称 jieba 对「帮我写一篇公众号文章」的输出为 `['公众号']`，
但实际 jieba 0.42.1 默认词典输出为 `['公众', '号']`。

**建议**：
- 修正 commit message 中的示例
- 或添加 `jieba.add_word("公众号")` 自定义词典
```

## 实际案例：SRA PR #17

| 检查项 | 发现 | 
|:-------|:-----|
| 声称 | jieba 分词精度「显著提升」，示例「公众号」被正确分词 |
| 验证 | jieba 默认词典把「公众号」切成了「公众」+「号」|
| 根因 | 「公众号」不在 jieba 默认词典中 |
| 修复 | 需 `jieba.add_word('公众号')` 或自定义词典 |
| 附带发现 | SRA 领域词「飞书」也被切成单字，「架构图」正常 |
