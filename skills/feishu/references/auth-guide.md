# 飞书 API 认证指南

> 飞书开放平台鉴权体系详解，涵盖 token 获取、刷新、权限申请、安全最佳实践。

---

## 1. 鉴权体系概览

飞书开放平台支持两种身份凭证：

| 凭证类型 | 身份 | 权限范围 | 有效期 | 适用场景 |
|---------|------|---------|--------|---------|
| `tenant_access_token` | 应用身份 | 应用自身的数据权限范围 | 2 小时 | 机器人发消息、管理文档等 |
| `user_access_token` | 用户身份 | 用户个人的数据权限范围 | 2 小时（可刷新） | 以用户身份操作日历、任务等 |

**Hermes 飞书集成默认使用 `tenant_access_token`**（机器人身份）。

---

## 2. 获取 tenant_access_token

### 接口

```
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
Content-Type: application/json

{
  "app_id": "cli_xxxxxxxxxx",
  "app_secret": "xxxxxxxxxxxxxxxx"
}
```

### 响应

```json
{
  "code": 0,
  "msg": "success",
  "tenant_access_token": "t-g1044qeGEDXTB6NDJOGV4JQCYDGHRBARFTGT1234",
  "expire": 7200
}
```

### Hermes 配置

在 `~/.hermes/config.yaml` 或 `~/.hermes/.env` 中配置：

```yaml
# config.yaml
feishu:
  app_id: "cli_xxxxxxxxxx"
  app_secret: "xxxxxxxxxxxxxxxx"
```

或

```bash
# .env
FEISHU_APP_ID=cli_xxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx
```

### Token 管理最佳实践

1. **缓存 token**: 不要每次请求都获取新 token
2. **定时刷新**: 在过期前 5 分钟刷新（即每 115 分钟刷新一次）
3. **错误处理**: 收到 `code: 99991663` 时重新获取 token
4. **并发安全**: 多进程/多线程环境下需要加锁或使用集中式缓存

### Python 实现示例

```python
import time
import requests

class FeishuAuth:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._token = None
        self._expires_at = 0

    def get_tenant_access_token(self) -> str:
        now = time.time()
        if self._token and now < self._expires_at - 300:  # 提前5分钟刷新
            return self._token

        resp = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": self.app_id, "app_secret": self.app_secret}
        )
        data = resp.json()
        if data["code"] != 0:
            raise Exception(f"获取 token 失败: {data['msg']}")

        self._token = data["tenant_access_token"]
        self._expires_at = now + data["expire"]
        return self._token
```

---

## 3. 获取 user_access_token

以用户身份调用 API（如操作用户日历、任务等），需要 user_access_token。

### 流程

1. **获取 authorization_code**: 引导用户访问授权页面
2. **换取 user_access_token**: 用 authorization_code 换取

### 步骤 1: 引导用户授权

```
GET https://open.feishu.cn/open-apis/authen/v1/redirect
  ?app_id=cli_xxx
  &redirect_uri=https://your-domain.com/callback
  &state=可选
  &scope=可选
```

### 步骤 2: 用 code 换 token

```
POST https://open.feishu.cn/open-apis/authen/v1/access_token
{
  "grant_type": "authorization_code",
  "code": "authorization_code"
}
```

### 步骤 3: 刷新 user_access_token

```
POST https://open.feishu.cn/open-apis/authen/v1/refresh_access_token
{
  "grant_type": "refresh_token",
  "refresh_token": "xxx"
}
```

---

## 4. 权限申请

### 4.1 在开发者后台申请

1. 登录 [飞书开放平台](https://open.feishu.cn/)
2. 进入你的应用 → **添加应用能力** / **权限管理**
3. 搜索并申请所需权限
4. 自建应用：需企业管理员审核
5. 商店应用：需平台管理员审核

### 4.2 权限分类

**不需要审核的权限：**
- `im:message:send_as_bot` — 机器人发消息
- `im:chat` — 获取群组信息
- `contact:user.base:readonly` — 读取用户基本信息

**需要审核的权限：**
- `im:message` — 获取消息
- `drive:drive` — 云空间管理
- `docx:document` — 读写云文档
- `bitable:app` — 读写多维表格
- `calendar:calendar` — 读写日历
- `approval:approval` — 审批管理
- `wiki:wiki` — 知识库管理
- `task:task` — 任务管理

### 4.3 通讯录权限范围

通讯录相关接口受「通讯录权限范围」控制：

- **全部成员**: 应用可访问所有用户/部门
- **部分成员**: 仅可访问指定部门/用户

在开发者后台 → **权限管理** → **通讯录权限范围** 中设置。

---

## 5. 事件订阅鉴权

### 5.1 URL 验证

配置事件回调地址时，飞书会发送验证请求：

```json
POST /your-callback-url
{
  "challenge": "ajls384kdjx9843d",
  "token": "your_verification_token",
  "type": "url_verification"
}
```

需返回：

```json
{ "challenge": "ajls384kdjx9843d" }
```

### 5.2 事件回调签名验证（v2.0 schema）

飞书使用签名验证确保回调来自飞书服务器：

```python
import hashlib
import hmac

def verify_signature(encrypt_key, timestamp, nonce, body):
    """验证飞书事件回调签名"""
    # 飞书 v2.0 使用 Encrypt Key 解密
    # 具体实现参考飞书官方 SDK
    pass
```

---

## 6. 安全最佳实践

### 6.1 凭证安全

- ✅ 将 `app_id` 和 `app_secret` 存储在环境变量或配置文件中
- ✅ 配置文件设置适当权限（`chmod 600 ~/.hermes/.env`）
- ❌ 不要在代码中硬编码凭证
- ❌ 不要在日志中打印 token

### 6.2 Token 安全

- ✅ 使用 HTTPS 传输
- ✅ 定期轮换 app_secret（如怀疑泄露）
- ✅ 实现 token 缓存避免频繁请求
- ❌ 不要在 URL 中传递 token（使用 Header）

### 6.3 权限最小化

- ✅ 只申请业务必需的权限
- ✅ 自建应用使用「部分成员」通讯录范围
- ✅ 定期审查权限使用情况
- ❌ 不要申请「获取用户手机号」等敏感权限（除非必需）

### 6.4 频率控制

- ✅ 实现请求队列和退避重试
- ✅ 监控 429 错误码
- ✅ 批量操作使用 batch 接口
- ❌ 不要无视频率限制持续请求

---

## 7. Hermes 飞书集成配置

### 7.1 配置文件位置

- 主配置: `~/.hermes/config.yaml`
- 环境变量: `~/.hermes/.env`

### 7.2 最小配置

```yaml
# ~/.hermes/config.yaml
platforms:
  feishu:
    enabled: true
    app_id: "cli_xxxxxxxxxx"
    app_secret: "xxxxxxxxxxxxxxxx"
```

### 7.3 Hermes 内置的飞书能力

Hermes 通过 `send_message` 工具集成飞书消息发送：

```python
# 发送文本消息
send_message(target="feishu:oc_xxx", message="你好")

# 发送富文本（Markdown）
send_message(target="feishu:oc_xxx", message="**加粗** *斜体* `代码`")

# 回复消息
send_message(target="feishu:om_xxx", message="回复内容")
```

**注意**: Hermes `send_message` 仅支持文本/Markdown 消息。上传文件、创建文档等操作需直接调用飞书 REST API。

---

## 8. 常见问题

### Q: token 过期了怎么办？
A: tenant_access_token 有效期 2 小时。收到 `code: 99991663` 错误时重新获取即可。建议实现自动刷新机制。

### Q: 权限申请被拒绝了怎么办？
A: 检查权限描述是否清晰，补充业务场景说明后重新提交。自建应用需要企业管理员在管理后台审核。

### Q: 如何测试 API？
A: 使用飞书开放平台的 [API 调试台](https://open.feishu.cn/api-explorer/) 在线测试。

### Q: 自建应用和商店应用有什么区别？
A: 自建应用仅限本企业使用，权限由企业管理员审核。商店应用可发布到应用市场，权限由平台审核。

### Q: 如何获取用户的 open_id？
A: 通过消息事件回调中的 `sender.sender_id.open_id` 获取，或调用通讯录 API 查询。
