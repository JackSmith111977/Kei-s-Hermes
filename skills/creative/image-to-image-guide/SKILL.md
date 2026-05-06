---
name: image-to-image-guide
description: "按已知信息生图的完整指南 — IP-Adapter + ControlNet 组合、17 种 ControlNet 模型分类、固定角色大法、风格迁移工作流。涵盖从参考图生成新图的全流程，解决 AI 绘图随机性太强的问题。"
version: 1.0.0
triggers:
  - 按已知信息生图
  - 图生图
  - ControlNet
  - IP-Adapter
  - 风格迁移
  - 固定角色
  - 参考图生图
  - 姿势控制
  - 线稿上色
  - 角色一致性
  - image-to-image
  - 参考图
  - 原图生新图
depends_on:
  - image-prompt-guide
allowed-tools:
  - terminal
  - read_file
  - write_file
  - browser_navigate
  - browser_snapshot
metadata:
  hermes:
    tags:
      - image-generation
      - controlnet
      - ip-adapter
      - style-transfer
      - character-consistency
    category: creative
    skill_type: workflow
    design_pattern: pipeline
---
# Image-to-Image Guide · 按已知信息生图完整指南

> **核心目标**：解决 AI 绘图"随机性太强"的问题，让生成的图与参考图保持一致性（风格、姿势、构图）。

---

## 一、技术范式转变

### 传统方法痛点

| 方法 | 痛点 | 处理时间 |
|------|------|----------|
| 神经风格迁移 | 每种风格需单独训练、8GB+显存 | 15-30 分钟/张 |
| GANs 方法 | 复杂训练、有限风格灵活性 | 数小时 |
| LoRA 训练 | 需要 100+张参考图、144MB+存储 | 2-8 小时训练 |

### 新范式：IP-Adapter + ControlNet 组合

| 特性 | 传统方法 | IP-Adapter + ControlNet |
|------|----------|-------------------------|
| 训练需求 | 需训练模型 | **零训练** |
| 参考图像 | 100+张 | **1 张足够** |
| 处理时间 | 15-30 分钟 | **10-30 秒** |
| 内容保留 | 70-80% | **99%+** |
| 风格准确度 | 70% | **96%** |
| 显存需求 | 16GB+ | **8GB** |

**技术分工**：
- **IP-Adapter Plus**：风格提取与迁移（图像 → Token → 注入扩散）
- **ControlNet**：结构约束与控制（预处理器 → 条件图 → 引导生成）

---

## 二、通用工作流程

### 基础流程（适用于任何 ControlNet）

```
上传参考图 → 选择预处理器 → 选择模型 → 设置权重 → 输入提示词 → 生成
```

### 详细步骤

| 步骤 | 操作 | 参数建议 |
|------|------|----------|
| 1. 基础设置 | 选择大模型（写实/二次元） | 迭代步数 35，采样方法 Euler |
| 2. 上传参考图 | 导入到 ControlNet 面板 | 点击向上按钮同步尺寸 |
| 3. 启用设置 | 勾选"启用"+"完美像素模式" | 低配电脑开启"低显存模式" |
| 4. 选择控制类型 | 根据需求选择预处理器和模型 | 预处理器和模型通常同名配套 |
| 5. 预览检查 | 点击爆炸按钮预览预处理效果 | 确认线条/姿势检测正确 |
| 6. 权重调整 | 根据场景调整 ControlNet 权重 | 真人转二次元 0.6，风格迁移拉满 |
| 7. 输入提示词 | 场景词 + 风格词 | 避免过多关键词堆砌 |
| 8. 生成图片 | 点击 Generate 按钮 | 等待生成结果 |

---

## 三、ControlNet 17 种模型分类

### 1. 姿势约束（OpenPose 系列）

| 预处理器 | 功能 | 适用场景 |
|----------|------|----------|
| `openpose` | 仅身体姿势 | 通用场景 |
| `openpose_hand` | 身体 + 手指 | 手指骨骼清晰时 |
| `openpose_faceonly` | 仅脸部表情 | 近景特写大头照 |
| `openpose_full` | 身体 + 手指 + 表情 | 全方位控制 |

**模型**：统一使用 `openpose`

**应用场景**：
- 角色三视图（配合 charturner 模型）
- 姿势复刻（上传姿势参考图）
- 多人姿势控制

**⚠️ 注意**：使用 LoRA 时用 ControlNet 控制表情可能导致生成人物与 LoRA 人物不太像。

---

### 2. 线条约束

| 模型 | 预处理器 | 特点 | 适用场景 |
|------|----------|------|----------|
| `lineart` | `lineart_anime` | 动漫线稿 | 动漫照片上色 |
| | `lineart_anime_denoise` | 动漫线稿（降噪） | 动漫照片上色 |
| | `lineart_coarse` | 粗线条 | 素描照片 |
| | `lineart_realistic` | 写实线稿 | 真人照片 |
| | `lineart_standard` | 标准线稿 | 黑白线稿 |
| `canny` | `canny` | 识别最多线条 | 最大程度还原（适合二次元） |
| `softedge` | `softedge_pidient` | 柔和轮廓 | 给 SD 更多发挥空间 |
| `mlsd` | `mlsd` | 仅识别直线 | 建筑设计/装修 |
| `scribble` | `invert` | 涂鸦识别 | 手绘草图生成 |

**选择建议**：
- **最大程度还原**：canny
- **只控制构图**：softedge、scribble
- **真人/素描照片**：lineart
- **建筑物装修**：mlsd

---

### 3. 空间深度约束（Depth）

| 预处理器 | 模型 | 特点 |
|----------|------|------|
| `depth_leres++` | `depth` | 复刻房子线条，保持物品前后距离关系 |

**应用场景**：
- 建筑装修（还原前后空间关系）
- 人物和背景分别控制（Depth 控制背景 + OpenPose 控制人物）

---

### 4. 物品种类约束（Seg）

| 预处理器 | 模型 | 功能 |
|----------|------|------|
| `seg_ofade20k` | `seg` | 语义分割，不同物品用不同颜色表示 |

**高级用法**：
1. 下载 seg 色块图
2. Photoshop 修改颜色（不同颜色代表不同物品）
3. SD 根据颜色生成特定物品

---

### 5. 风格约束

| 模型 | 预处理器 | 功能 | 备注 |
|------|----------|------|------|
| `shuffle` | `shuffle` | 融合参考图颜色生成新图 | 引导介入时机设 0.2~0.3 |
| `reference` | `reference` | 还原角色五官发型 | **无需模型** |
| `normal` | `normal_bae` | 参考明暗关系 + 还原姿势 | |
| `t2ia` | `t2ia_color_grid` | 模糊成马赛克再生成 | 不同预处理器用不同模型 |
| `IP-Adapter` | `ip-adapter_clip` | 参考原图全部内容 | 风格 + 人物形象都能还原 |

---

### 6. 重绘

#### Inpaint（局部重绘）

| 预处理器 | 模型 | 特点 |
|----------|------|------|
| `inpaint_global_harmonious` | `inpaint` | 整张图重绘，融合好但色调会变 |
| `inpaint_only` | `inpaint` | 只重绘涂黑区域 |

**用途**：
- 消除图片信息（关键词填背景描述）
- 给人物换衣服

> 💡 效果优于图生图的局部重绘功能

#### Recolor（重新上色）

| 预处理器 | 模型 | 用途 |
|----------|------|------|
| `recolor_luminance` | `ioclad_sd15_recolor` | 黑白照片上色/换颜色 |

**换色技巧**：深色换深色，浅色换浅色（如黑发 → 棕/绿，不宜 → 白色）

---

### 7. 特效（IP2P）

| 预处理器 | 模型 | 关键词格式 |
|----------|------|------------|
| 无 | `ip2p` | `make it [效果]` |

**示例**：
- `make it winter` → 房子变冬天
- `make it fire` → 房子着火
- `make it snow` → 加入下雪效果

---

### 8. 加照片细节（Tile）

| 预处理器 | 模型 |
|----------|------|
| `tile_resample` | `tile` |

**用途**：
1. 恢复画质（不太适合真人，可能改变样貌）
2. 生成赛博机车图
3. 真人变动漫
4. 动漫变真人
5. 光影艺术字

---

## 四、核心技巧详解

### 4.1 IP-Adapter 风格迁移

**单图风格迁移流程**：
1. 上传参考图到 ControlNet Unit 0
2. 启用 ControlNet，勾选完美像素模式
3. 控制类型选择 IP-Adapter
4. 模型选择 `ip_adapter_sd15_plus.pth`
5. 设置生成参数，尺寸与参考图保持一样
6. 点击生成，风格、色调迁移到新图

**风格 + 姿势双重控制**：
1. ControlNet Unit 0：IP-Adapter（风格参考）
2. ControlNet Unit 1：OpenPose（姿势参考）
3. 同时启用两个 ControlNet
4. 输入提示词，生成风格 + 姿势双重控制的图片

**参数建议**：

| 参数 | 推荐值 | 用途 |
|------|--------|------|
| Weight | 0.8-1.2 | 风格强度 |
| Style Scale | 0.5-0.6 | 最佳平衡 |
| Noise | 0.1-0.3 | 增强变化 |
| Weight Type | 渐入渐出 | 自然混合 |

---

### 4.2 固定角色大法（Reference）

**核心思想**：通过 Reference 功能固定角色形象，生成不同场景、不同动作的图片，角色风格保持不变。

**使用流程**：
1. 准备角色图片（用 SD 生成或找特色图片）
2. 启用 ControlNet，勾选"完美像素"
3. 导入角色图片到 Reference
4. 权重值调到 1
5. 输入场景词（仅描述场景，**不描述角色**）
6. 生成图片，角色风格保持不变

**示例**：
- **角色设定**："女孩，全身，波浪姜黄色头发，淡褐色眼睛，中式风格，蕾丝镶边，蓝色背景，POP MART 盲盒，IP 形象"
- **场景词**："坐在教室里" → 女孩坐在教室里
- **场景词**："打羽毛球，羽毛球场" → 女孩在羽毛球场打羽毛球

**应用场景**：
- 游戏开发：快速生成游戏角色不同动作、不同场景
- 广告设计：快速生成多个风格的广告海报
- 动画制作、插画创作

---

### 4.3 多 ControlNet 组合

**人物和背景分别控制**：
1. ControlNet 0：OpenPose（控制人物姿势）
2. ControlNet 1：Seg 或 Depth（控制背景构成）
3. 调整权重：OpenPose 权重高于 Depth
4. 提示词进行内容和风格控制

**精准图片风格化**：
1. 在 img2img 图生图中使用
2. ControlNet 0：Lineart（提取图像结构）
3. ControlNet 1：Depth（保持空间关系）
4. 配合提示词和风格模型重新生成

---

## 五、参数速查表

### 5.1 ControlNet 权重建议

| 场景 | 权重值 | 说明 |
|------|--------|------|
| 真人转二次元 | **0.6** | 降低权重避免过度还原 |
| 风格迁移 | **1.0**（拉满） | 最大程度迁移风格 |
| 姿势控制 | **0.8-1.0** | 确保姿势正确识别 |
| 线稿上色 | **0.8-1.0** | 最大程度还原线稿 |
| Shuffle 风格迁移 | **0.8-1.0** | 配合引导介入时机 0.2~0.3 |

### 5.2 引导介入时机

| 模型 | 建议值 | 说明 |
|------|--------|------|
| Shuffle | **0.2~0.3** | 先生成形状再改画风 |

### 5.3 SD 基础参数建议

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 迭代步数 | **35** | 平衡质量与速度 |
| 采样方法 | **Euler** | 通用推荐 |
| 完美像素模式 | **开启** | 确保生成质量 |
| 低显存模式 | **低配电脑开启** | 避免显存溢出 |

---

## 六、常见错误与避坑指南

### 6.1 ControlNet 常见错误

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 预处理器和模型不匹配 | 选错了配套组合 | 预处理器和模型通常同名配套使用 |
| 真人转二次元不像真人 | ControlNet 权重过高 | 将权重降至 **0.6** 左右 |
| 使用 LoRA 时人物不像 LoRA 人物 | ControlNet 控制表情导致 | 避免 openpose_faceonly 控制表情 |
| Shuffle 模型影响形状 | 引导介入时机不对 | 设置引导介入时机为 **0.2~0.3** |
| 低配电脑显存溢出 | 同时运行多个高精度模型 | 开启"低显存模式"，避免同时运行 3 个以上模型 |

### 6.2 平台差异注意事项

| 平台 | Prompt 特点 |
|------|--------------|
| Stable Diffusion | 适合逗号分隔，需负向提示 |
| Midjourney | 爱长句和细节，用 `--ar --v` 参数 |
| DALL-E | 喜欢简洁，需适度克制 |
| Gemini | 要简单短句 |

---

## 七、应用场景速查

| 场景 | 推荐模型 | 预处理器 | 权重 |
|------|----------|----------|------|
| 线稿上色 | canny, lineart | canny, lineart_anime | 0.8-1.0 |
| 风格迁移 | shuffle, IP-Adapter | shuffle, ip-adapter_clip | 0.8-1.2 |
| 角色三视图 | openpose | openpose_full | 1.0 |
| 建筑设计 | mlsd, depth | mlsd, depth_leres++ | 1.0 |
| 人物姿势控制 | openpose | openpose, openpose_hand | 0.8-1.0 |
| 局部重绘 | inpaint | inpaint_only | 拉满 |
| 黑白照片上色 | recolor | recolor_luminance | 1.0 |
| 照片增强 | tile | tile_resample | 0.8-1.0 |
| 真人转二次元 | lineart, canny | lineart_anime, canny | **0.6** |
| 固定角色 | reference | reference_only | **1.0** |

---

## 八、知识缺口

⚠️ **待补充内容**（建议后续学习）：
- ComfyUI 节点配置详解
- IP-Adapter Faceid（肖像特定风格迁移）
- ControlNet Union（统一架构）
- 视频风格迁移管道（AnimateDiff + IP-Adapter）

---

## 九、参考资料

- IP-Adapter + ControlNet 组合详解：https://apatero.com/zh/blog/ip-adapter-controlnet-combo-killed-style-transfer-2025
- ControlNet 终极教程：https://skycaiji.com/aigc/ai18568.html
- Stable Diffusion Prompt 语法：https://cloud.baidu.com/article/4229808
- 固定角色技巧：https://cloud.baidu.com/article/3361534