# Bilibili 视频字幕提取指南

## 概述

Bilibili 视频字幕提取的挑战与解决方案。B 站的大部分视频（尤其是 AI 自动生成字幕）需要登录态才能获取，且反爬机制较强。

## 已知限制

1. **大部分视频需要登录**：B 站 API (`x/player/v2`) 返回 `need_login_subtitle: true` 时，字幕仅在提供 SESSDATA 等 Cookie 时可用。
2. **AI 字幕 API 需要 WBI 签名**：新版 API 使用 `x/player/wbi/v2` 端点，可能需要签名。
3. **空字幕列表**：视频可能根本没有上传/生成字幕（`subtitles: []`）。

## 尝试过的获取方式

### 方式 1：直接 API 调用（无需登录）
```
GET https://api.bilibili.com/x/player/v2?bvid=BVxxx&cid=xxx
```
- ✅ 可获取视频基本信息（CID、标题等）
- ❌ `subtitles` 字段在未登录时返回空数组

### 方式 2：WBI 签名 API
```
GET https://api.bilibili.com/x/player/wbi/v2?bvid=BVxxx&cid=xxx
```
- 部分情况下可能返回字幕，但通常也需要登录

### 方式 3：yt-dlp
```bash
yt-dlp --list-subs "https://www.bilibili.com/video/BVxxx"
```
- ✅ 可提取视频格式信息
- ⚠️ 字幕需要 `--cookies-from-browser` 或 `--cookies`
- 注意：国内服务器可能需要代理

### 方式 4：bilibili-api-python
```python
from bilibili_api import video, Credential
v = video.Video(bvid='BVxxx', credential=Credential(sessdata='xxx'))
sub = await v.get_subtitle(cid)
```
- ✅ 功能最完整
- ❌ 需要 SESSDATA、BILI_JCT、BUVID3 等凭证
- ⚠️ 依赖 Pillow，需注意系统 Python 版本兼容性

### 方式 5：bilibili-cli
```bash
bili video BVxxx --subtitle
```
- ✅ 支持 QR 扫码登录
- ⚠️ 首次使用需 `bili login` 扫码授权

### 方式 6：bilibili-subtitle-fetch（MCP 服务）
```bash
bilibili-subtitle-fetch fetch --asr BVxxx
```
- ✅ 支持 ASR（语音识别）回退
- ❌ 需要登录凭证才能获取官方字幕

## Pillow 兼容性问题

`bilibili-api-python` 依赖 PIL/ Pillow。在此环境中：

### 问题
```
ImportError: cannot import name '_imaging' from 'PIL'
```
原因：pip 安装的 Pillow 缺少 C 扩展 `_imaging`，而系统 Python 的 Pillow 来自 apt。

### 解决方案
```bash
# 移除 pip 安装的 PIL，使用系统 PIL
pip uninstall -y Pillow pillow
rm -rf /home/ubuntu/.local/lib/python3.12/site-packages/PIL/
# 用系统 Python 运行
PYTHONPATH=/home/ubuntu/.local/lib/python3.12/site-packages /usr/bin/python3 script.py
```

## 没有字幕时的替代方案

1. **参考视频描述和 GitHub 仓库**：很多技术视频作者会开源相关的代码和文档
2. **使用 ASR 语音识别**：下载视频音频后用 Whisper/faster-whisper 转写
3. **搜索视频中提到的论文和资料**：基于关键词做独立调研
4. **查看视频评论和弹幕**：有时包含有价值的信息摘要

## 快速检查字幕是否可用

```bash
# 1. 获取视频信息
curl -s 'https://api.bilibili.com/x/web-interface/view?bvid=BVxxx' | python3 -c "
import json,sys
d=json.load(sys.stdin)['data']
print('CID:', d['cid'])
print('Title:', d['title'])
"
# 2. 检查字幕
curl -s 'https://api.bilibili.com/x/player/v2?bvid=BVxxx&cid=CID' | python3 -c "
import json,sys
d=json.load(sys.stdin)
sub=d['data']['subtitle']
print('Need login:', d['data'].get('need_login_subtitle'))
print('Subtitles:', len(sub.get('subtitles',[])))
"
```

## 相关工具

| 工具 | 安装方式 | 字幕支持 | 是否需要登录 |
|------|---------|---------|------------|
| yt-dlp | `pip install yt-dlp` | ⚠️ 需要 cookies | ✅ |
| bilibili-api-python | `pip install bilibili-api-python` | ✅ 完整 | ✅ |
| bilibili-cli | `pip install bilibili-cli` | ✅ 完整 | ✅ (QR 扫码) |
| bilibili-subtitle-fetch | `pip install bilibili-subtitle-fetch` | ✅ 含 ASR | ⚠️ 可选 |
