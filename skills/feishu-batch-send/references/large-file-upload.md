# 大文件（>10MB）上传方案测试报告

## 测试时间：2026-05-05

## 测试结果

### ✅ 方案1：消息文件 API（im/v1/files）—— 可用

```bash
curl -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=stream" \
  -F "file_name=large_file.bin" \
  -F "file=@/path/to/large_file"
```

**测试结果**：
- 12MB 文件上传成功 ✅
- 耗时：~26 秒
- file_key 正常返回 ✅
- 可以正常发送为文件消息 ✅

**限制**：
- 文件大小上限：**50MB**（普通应用）/ **200MB**（大型应用）
- 无需额外权限，im:message 权限即可

### ❌ 方案2：云空间分片上传（drive/v1）—— 不可用

需要 `drive:drive` 权限，当前飞书应用未开通此权限。
分片上传 API 流程（upload_prepare → upload_part → upload_finish）需要：
- parent_type 和 parent_node 参数
- 需要云空间读写权限

## 结论

| 文件大小 | 推荐方案 | 说明 |
|---------|---------|------|
| < 50MB | im/v1/files（直接上传） | 简单可靠，无需额外权限 |
| > 50MB | 需要申请 drive 权限 + 分片上传 | 当前不可用 |
| > 200MB | 需要飞书企业版 + 大文件权限 | 普通应用不支持 |

## 实际测试数据

| 文件大小 | 上传方式 | 耗时 | 结果 |
|---------|---------|------|------|
| 12MB | im/v1/files | 26s | ✅ 成功 |
| 12MB | drive/v1 分片 | - | ❌ 权限不足 |

## 建议

对于当前环境，**50MB 以下的文件直接用 im/v1/files 上传即可**，
不需要分片上传。如果未来有超过 50MB 的文件需求，需要：
1. 在飞书开发者后台申请 `drive:drive` 权限
2. 实现分片上传逻辑（每片建议 10MB）
3. 使用 upload_prepare → upload_part → upload_finish 三步流程
