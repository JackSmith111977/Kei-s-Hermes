---
name: image-prompt-guide
description: 编写高质量生图 Prompt 的最佳实践，涵盖光影、风格、情绪及技术参数（适配 FLUX/gpt-image-2）。包含角色一致性技巧、多模态策略决策树、按已知信息生图方法。
triggers:
- prompt
- 生图提示词
- art style
- character consistency
- 角色一致性
metadata:
  hermes:
    tags:
    - prompt-engineering
    - generative-ai
    - art
    - flux
    - gpt-image-2
    - character-consistency
    category: creative
    skill_type: reference
    design_pattern: tool_wrapper
depends_on: []

---
# AI 生图 Prompt 指南 v2.0

> 基于 2024-2025 年最新论文与实践更新，包含 IP-Adapter、gpt-image-2、FLUX 最佳实践

## 描述
AI 图片生成 prompt 编写最佳实践 — 涵盖 FLUX、gpt-image-2、DALL·E 等主流模型的风格描述、灯光关键词、构图技巧、角色一致性技巧和迭代策略。

---

## 模型特性速查表

| Feature | FLUX | gpt-image-2 | Stable Diffusion |
|---------|------|-------------|------------------|
| Prompt style | 自然语言 | 结构化/分段 | 关键词列表 |
| Negative prompts | ❌ **不支持** | ✓ 支持 | ✓ 支持 |
| Weight syntax | ❌ 完全忽略 | ✓ 支持 | ✓ `(word:1.5)` |
| Optimal length | 40-50 words | Variable | ~75 tokens |
| Token limit | 512 (dev), 256 (schnell) | Flexible | 75 (CLIP) |
| Reference image | ✓ Kontext | ✓ 多模态输入 | IP-Adapter |
| Camera specs | ✓ 解锁真实感 | ✓ 松散解释 | ✓ 有帮助 |

---

## FLUX Prompt 最佳实践（2026 更新）

### ⚠️ 关键规则：FLUX 不支持 Negative Prompts

**错误做法**：
```
negative_prompt: "blurry, low quality, bad hands, deformed"
```

**正确做法**：用正向描述替代
```
sharp focus, crisp detail, accurate hands, natural proportions
```

### Prompt 结构层级

**FLUX 对早期 token 权重更大，结构至关重要**：

```
1. Subject first（主体） — 图像是什么？
2. Action/pose（动作） — 主体在做什么？
3. Environment（环境） — 场景在哪里？
4. Lighting（光照） — 场景如何照明？
5. Style/technical specs（风格/技术规格） — 相机、外观、情绪
```

### Prompt 长度最佳实践

- **FLUX.1 [dev]**: 支持最多 512 tokens
- **FLUX.1 [schnell]**: 最多 256 tokens
- **最佳长度**: **40-50 words**

```
❌ 过短（< 10 words）：模型从训练数据填充细节，不可控
❌ 过长（> 200 words）：内部压缩，细节可能丢失
✅ 40-50 words：最佳平衡
```

### 文本渲染最佳实践

FLUX 在文本渲染方面表现卓越：

```
规则：
1. 用引号包裹精确文本：'"TODAY'S SPECIAL: LAVENDER LATTE"'
2. 单独指定字体：'Bold serif font in dark green'
3. 大小写敏感："HELLO" → HELLO; "hello" → hello
4. 短文本更准确：2-5 词高度可靠
5. 清洁背景有帮助：复杂背景上的文本更难渲染
6. 明确放置位置：'At the top of the poster, "SUMMER SALE"'
```

### 描述光的行为（而非类型）

```
❌ golden hour lighting
✅ warm golden sunset light streaming through the window, 
   casting long shadows across the hardwood floor, 
   with dust particles visible in the light beam

对比示例：
❌ bright sunlight
✅ Harsh noon sun creating deep contrast shadows under the awnings

❌ diffused lighting  
✅ Soft overcast light wrapping evenly around the subject's face

❌ neon lighting
✅ Neon signs reflecting off wet pavement at night, 
   blue and pink glow pooling in puddles
```

### Camera Specifications 解锁真实感

| Style | Camera Spec |
|-------|-------------|
| Professional portraits | Canon EOS R5, 85mm f/1.4, studio lighting |
| Street photography | Fujifilm X-T5, 23mm f/2, available light |
| Product shots | Phase One IQ4, 120mm macro, softbox lighting |
| Casual content | iPhone 16, natural light, candid angle |
| Editorial quality | Hasselblad X2D, medium format, natural light |

---

## gpt-image-2 Prompt 最佳实践

### 核心能力

| Capability | Description |
|------------|-------------|
| High-fidelity photorealism | 自然光照、准确材质、丰富色彩 |
| Robust facial/identity preservation | 编辑、角色一致性、多步工作流 |
| Reliable text rendering | 清晰字形、一致布局、强对比 |
| Precise style control/transfer | 最少提示词控制风格 |
| **多模态输入** | 可直接接收图片作为参考 |

### 分辨率约束

**必须满足所有条件**：
- 最大边长 < 3840px
- 两边必须是 16 的倍数
- 长短边比例 ≤ 3:1
- 总像素范围：655,360 – 8,294,400

> ⚠️ 超过 2560x1440 (2K/QHD) 视为实验性

### Prompt 基础结构

```
推荐顺序：背景/场景 → 主体 → 关键细节 → 约束条件
```

**关键原则**：
1. **结构 + 目标**：包含预期用途（广告、UI mock、信息图）
2. **分段清晰**：复杂请求用短标签分段或换行
3. **生产优先**：使用可扫描模板而非花哨语法

### Quality Settings 选择

| Setting | When to Use |
|---------|-------------|
| `low` | 延迟敏感、高批量用例，先测试 |
| `medium` | 平衡质量与速度 |
| `high` | 小/密集文本、详细信息图、身份敏感编辑 |

### Composition 要素

```
Framing/viewpoint: close-up, wide, top-down
Perspective/angle: eye-level, low-angle
Lighting/mood: soft diffuse, golden hour, high-contrast
Placement: "logo top-right", "subject centered with negative space"
```

### 编辑工作流关键技巧

```
使用 "change only X" + "keep everything else the same"
每次迭代重复 preserve list 以减少漂移

示例：
change only the background color to blue, 
preserve identity, geometry, layout, brand elements, 
saturation, contrast, camera angle
```

---

## 角色一致性技巧（2026 最佳实践）

### 理解核心问题

> 扩散模型是**无状态的**——它们没有之前生成的记忆。每次生成从头开始。

**Consistency vs Similarity**：
- **Similar**：角色看起来大致相同
- **Consistent**：每次生成出现相同的下颌线、嘴唇形状、眼睛距离

### Step 1: 构建 Character Block

**锁定 5 个物理锚点**：

| Anchor | Example Details |
|--------|-----------------|
| Face shape | oval, square, heart, round |
| Eye details | hazel almond-shaped eyes, close-set |
| Nose structure | narrow bridge, rounded tip |
| Skin tone | warm olive, deep ebony |
| Hair | chestnut brown, shoulder-length, slight wave |

**Character Block 编写规则**：
```
1. 单一密集段落（< 120 词）
2. 作为"选角简介"
3. 每次提示词中复制粘贴，绝不重写
4. 放在提示词最前面（模型对早期 token 权重更大）
```

**示例 Character Block**：
```
A young woman with oval face shape, hazel almond-shaped close-set eyes, 
narrow nose bridge with rounded tip, warm olive skin tone, 
shoulder-length chestnut brown hair with subtle highlights and slight wave, 
side part left, delicate features
```

### Step 2: Prompt Engineering 公式

```
[Character Block] + [Scene Setup] + [Action/Pose] + 
[Environment] + [Lighting] + [Camera/Technical]
```

> ⚠️ **Character Block 必须放在最前面**

### 常见错误表

| Mistake | What Goes Wrong | Fix |
|--------|-----------------|-----|
| Vague descriptors | "beautiful woman" 每次生成新人物 | Use 8+ specific physical descriptors |
| Character block at end | 模型对早期 token 权重更大 | Always put character block first |
| Changing any word | "dark hair" vs "dark wavy hair" 差异大 | Copy-paste the block, never retype |
| Overly stylized reference | 模型学习风格+光照而非角色 | Use neutral expression, clean lighting |

### 参考图像最佳实践

**好的参考图像条件**：
- **Neutral expression**（微笑会夸大特征）
- **Frontal or slight 3/4 angle**
- **Clean, diffused lighting**
- **Minimal background**
- **High resolution**

### 5-Scene Test

在承诺设计前，测试这5个场景：

| Scene | Purpose |
|-------|---------|
| Indoor neutral | 办公室/图书馆，平面光照 |
| Outdoor harsh light | 正午阳光从上方 |
| Night scene | 人工光照，高对比 |
| Close-up portrait | 填充 80% 画面 |
| Full body shot | 头到脚可见 |

---

## 按已知信息生图策略决策树

```
是否有参考图片？
├─ Yes → 模型是否多模态？
│   ├─ Yes (gpt-image-2) → 直接提供参考图片作为输入
│   │   API: /v1/images/edits (image + prompt)
│   │   最佳实践: 高 fidelity 自动处理
│   │
│   └─ No (FLUX/SD) → 选择参考方法：
│       ├─ 1 张参考 → InstantID/PuLID (2-3 min setup)
│       │   Consistency: 80-90%
│       │   Best for: Quick consistent faces
│       │
│       ├─ 多张参考 → IP-Adapter + ControlNet
│       │   IP-Adapter: 风格/身份控制 (scale 0.6-0.8)
│       │   ControlNet: 空间布局控制 (scale 0.7)
│       │   Consistency: 85-95%
│       │
│       ├─ Flux Redux Schnell → 从 master 图生成变体
│       │   保持视觉身份到新场景/姿势
│       │
│       └─ Flux Canny Pro → 提取结构边缘图
│       │   锁定骨结构和比例
│       │
│       └─ 需要完美一致性 → LoRA Training (1-2 hours)
│           15-30 张角色图像训练
│           Consistency: 95-99%
│
└─ No → 仅文本提示词
    ├─ FLUX → 
    │   自然语言 prompt
    │   40-50 words
    │   正向描述替代 negative
    │   Camera specs 解锁真实感
    │
    ├─ SD →
    │   关键词列表
    │   Negative prompts 支持
    │   Weight syntax `(word:1.5)`
    │
    └─ gpt-image-2 →
        结构化 prompt
        Quality settings 选择
        包含预期用途
```

---

## 一致性层级总结

| Level | Method | Consistency | Setup Time | Best For |
|-------|--------|-------------|------------|----------|
| L1 | Detailed Prompt (8+ descriptors) | 60-70% | 5 min | 简单场景 |
| L2 | Seed + Prompt Locking | 70-80% | 10 min | 姿势/服装变化 |
| L3 | InstantID/PuLID | 80-90% | 2-3 min | 快速面部一致性 |
| L4 | IP-Adapter + ControlNet | 85-95% | 10 min | 专业控制 |
| L5 | LoRA Training | 95-99% | 1-2 hours | 完美控制 |

---

## 灯光关键词（所有模型通用）

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

---

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

---

## 最佳实践总结

1. **主题和风格放在前面** — 这不是建议，是必须的
2. **使用 8+ 具体物理描述符** — 角色一致性关键
3. **Character Block 复制粘贴** — 绝不重写，放在最前
4. **FLUX 用正向描述替代 negative** — 不支持 negative prompts
5. **描述光的行为而非类型** — 更真实的光照效果
6. **Camera specs 解锁真实感** — 指定相机型号和镜头
7. **文本用引号包裹** — 精确控制文本渲染
8. **40-50 words 最佳长度** — FLUX 最佳平衡
9. **5-Scene Test** — 测试角色一致性后才承诺设计
10. **迭代而非一次性** — 逐步添加细节

---

## 参考文献

- IP-Adapter (arxiv 2308.06721) — Decoupled Cross-Attention
- gpt-image-2 Official Prompting Guide (OpenAI Cookbook)
- FLUX Prompt Guide (fal.ai)
- Character Consistency Comprehensive Guide (PicassoIA)
- InstantID/PuLID — Single-reference Face Consistency