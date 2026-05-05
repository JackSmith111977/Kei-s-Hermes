# 飞书图片发送流程验证报告

## 测试时间：2026-05-05

## 两种方法对比

### 方法1：图片 API（推荐用于内联图片）

```
POST /im/v1/images
Form: image_type=message, image=<binary>
→ 返回 image_key
→ 发送 msg_type=image, content={"image_key": "..."}
```

**效果**：图片直接嵌入聊天，点击可大图查看，支持预览
**适用场景**：截图、照片、图表等需要直接展示的图片

### 方法2：文件 API（用于图片附件）

```
POST /im/v1/files
Form: file_type=stream, file_name=xxx, file=<binary>
→ 返回 file_key
→ 发送 msg_type=file, content={"file_key": "..."}
```

**效果**：图片作为文件附件发送，显示为文件卡片，需要下载后查看
**适用场景**：需要保留原始文件名的图片、批量归档

## 结论

| 场景 | 推荐方法 | 原因 |
|------|---------|------|
| 聊天中直接展示图片 | 方法1 (image API) | 内联显示，支持预览 |
| 发送 PNG 截图/图表 | 方法1 (image API) | 用户体验最佳 |
| 发送原始图片文件 | 方法2 (file API) | 保留文件名和格式 |
| 批量发送混合内容 | 混用 | 图片用方法1，文档用方法2 |

## 注意事项

1. **图片大小限制**：≤ 10MB（图片 API）/ ≤ 50MB（文件 API）
2. **格式支持**：jpg, png, gif, webp, bmp（图片 API）
3. **file_type 不能乱填**：通用文件必须用 `stream`，不是 `file`！
4. **token 有效期**：2 小时，批量发送前检查
