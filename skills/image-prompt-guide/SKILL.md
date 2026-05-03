# AI 生图 Prompt 指南

## 描述
AI 图片生成 prompt 编写最佳实践 — 涵盖 FLUX、gpt-image-2、DALL·E 等主流模型的风格描述、灯光关键词、构图技巧和迭代策略。

## 触发条件
- 用户要求生成图片、配图、插图
- 需要提高生图质量和艺术效果
- 需要特定艺术风格或摄影风格

## FLUX Prompt 结构

### 基础公式
```
[Subject] + [Setting/Environment] + [Lighting] + [Style/Mood] + [Technical Details]
```

### 示例分解
**Prompt**: "A professional headshot of a confident businesswoman, modern office background with glass windows, soft natural lighting from the side, corporate editorial style, shot on Canon 5D, shallow depth of field"

| 组件 | 示例 |
|------|------|
| Subject | Professional headshot of a confident businesswoman |
| Setting | Modern office background with glass windows |
| Lighting | Soft natural lighting from the side |
| Style | Corporate editorial style |
| Technical | Shot on Canon 5D, shallow depth of field |

## 灯光关键词（Flux 响应极佳）

### 自然光
- "Golden hour sunlight" — 金色时刻阳光
- "Blue hour ambient" — 蓝色时刻环境光
- "Soft overcast daylight" — 柔和阴天日光
- "Dappled sunlight through trees" — 树荫斑驳阳光
- "Window light, soft and diffused" — 柔和漫射窗户光

### 工作室灯光
- "Rembrandt lighting" — 伦勃朗光（经典肖像）
- "Butterfly lighting" — 蝴蝶光（时尚肖像）
- "Split lighting" — 分割光（戏剧性）
- "Soft box lighting" — 柔光箱照明
- "Ring light, even illumination" — 环形灯均匀照明

### 戏剧性灯光
- "Rim lighting, dramatic silhouette" — 边缘光，戏剧性剪影
- "Chiaroscuro, high contrast" — 明暗对比法，高对比度
- "Neon accent lighting" — 霓虹重点照明
- "Backlit, lens flare" — 逆光，镜头光晕
- "Low key, moody shadows" — 低调，情绪化阴影

## 风格关键词

### 摄影风格
| 关键词 | 效果 |
|--------|------|
| "Editorial" | 杂志级质量，精致 |
| "Documentary" | 真实，自然感 |
| "Commercial" | 干净，广告级 |
| "Fine art" | 艺术性，概念化 |
| "Street photography" | 城市，自发感 |
| "Corporate" | 商务，专业 |
| "Product photography" | 产品展示 |

### 艺术风格
| 关键词 | 效果 |
|--------|------|
| "Minimalist" | 极简主义 |
| "Isometric 3D" | 等距 3D 风格 |
| "Flat design" | 扁平化设计 |
| "Vector illustration" | 矢量插图 |
| "Watercolor painting" | 水彩画 |
| "Oil painting" | 油画 |
| "Digital art" | 数字艺术 |
| "Concept art" | 概念艺术 |
| "Cyberpunk" | 赛博朋克 |
| "Steampunk" | 蒸汽朋克 |

### 情绪关键词
| 关键词 | 效果 |
|--------|------|
| "Warm and inviting" | 温馨，舒适 |
| "Cool and professional" | 冷静，商务 |
| "Dramatic and intense" | 戏剧性，强烈 |
| "Soft and dreamy" | 柔和，梦幻 |
| "Bold and vibrant" | 大胆，鲜艳 |
| "Serene and calm" | 宁静，平静 |
| "Energetic and dynamic" | 活力，动感 |

## 技术关键词

### 相机参考
- "Shot on Canon 5D Mark IV"
- "Hasselblad medium format"
- "Leica M10"
- "Sony A7R IV"
- "Phase One digital back"

### 镜头效果
- "85mm portrait lens" — 85mm 人像镜头
- "35mm wide angle" — 35mm 广角
- "Macro lens, extreme detail" — 微距镜头，极致细节
- "Tilt-shift, miniature effect" — 移轴，微缩效果
- "Anamorphic lens flare" — 变形镜头光晕

### 景深
- "Shallow depth of field, bokeh background" — 浅景深，散景背景
- "Deep focus, everything sharp" — 深焦，全部清晰
- "Selective focus on subject" — 选择性对焦主体
- "Creamy bokeh, f/1.4" — 奶油散景，f/1.4

## 常见错误与避免

### ❌ 过于模糊
```
A person in a nice place
```

### ✅ 更好
```
A young professional woman in a modern co-working space, natural window light, candid moment working on laptop, lifestyle photography, warm and productive atmosphere
```

### ❌ 冲突指令
```
Dark moody lighting, bright and cheerful
```

### ✅ 更好
```
Moody dramatic lighting with warm accent highlights
```

### ❌ 过度堆砌
```
A woman with red hair and blue eyes wearing a green dress with yellow flowers and purple shoes standing in a pink room with orange furniture and...
```

### ✅ 更好
```
Elegant woman in emerald dress, modern minimalist interior, soft natural lighting, fashion editorial style
```

## 迭代策略

1. **从基础开始** — Subject + setting + lighting
2. **添加风格** — Photography style, mood
3. **细化技术** — Camera, lens, depth of field
4. **打磨细节** — 基于结果的具体调整

### 迭代示例
**V1**: "Woman in office"
**V2**: "Professional businesswoman in modern office, natural lighting"
**V3**: "Professional businesswoman in modern glass office, soft window light, confident pose, corporate editorial"
**V4**: "Professional businesswoman in modern glass office, soft diffused window light from the left, confident approachable expression, corporate editorial style, shot on Canon 5D, shallow depth of field, warm color grade"

## 技术文档配图 Prompt 模板

### 架构图
```
Clean minimalist architecture diagram, [color scheme] color palette, flat design, [background] background, rounded rectangles with subtle shadows, thin connecting arrows, no text, professional technical illustration style, isometric 3D elements
```

### 流程图
```
Modern workflow diagram showing [process], connected arrows in [direction], [style] design, [colors] accent colors, clean minimalist, [background] background, no text, vector illustration
```

### 概念图
```
[Concept] visualization, [metaphor] metaphor, [style] style, [colors] color scheme, [background] background, clean infographic aesthetic, no text labels, professional technical illustration
```

### 系统图
```
[System] architecture, central hub with connected modules, [shape] shapes, [colors] color scheme, clean vector style, [background] background, no text labels, modern flat design
```

## FLUX 特有技巧

1. **自然语言风格描述** — FLUX 对详细自然语言风格描述响应良好
2. **避免过度使用"in the style of"** — 使用更具体的技术描述
3. **降低采样步数** — 8-10 步适合绘画风格，20-30 步适合摄影风格
4. **HEX 颜色代码** — FLUX.2 支持精确颜色匹配（如 `#4A90D9`）
5. **负向 prompt** — 使用负向 prompt 排除不需要的元素

## 最佳实践

1. **主题和风格放在前面** — 这不是建议，是必须的
2. **使用具体形容词** — 提升 prompt 精度
3. **避免冲突描述** — 确保所有描述和谐一致
4. **逐步迭代** — 不要一次添加所有细节
5. **保持简洁** — 过于冗长的 prompt 可能导致混乱
