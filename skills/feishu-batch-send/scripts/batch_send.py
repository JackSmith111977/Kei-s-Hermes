#!/usr/bin/env python3
"""飞书批量发送文件/图片脚本"""
import os, sys, json, time, argparse, requests

def get_token():
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={
            "app_id": os.environ["FEISHU_APP_ID"],
            "app_secret": os.environ["FEISHU_APP_SECRET"]
        }
    )
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"获取 token 失败: {data}")
    return data["tenant_access_token"], data.get("expire", 7200)

def upload_file(token, filepath, file_type="stream"):
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        if file_type == "image":
            resp = requests.post(
                "https://open.feishu.cn/open-apis/im/v1/images",
                headers={"Authorization": f"Bearer {token}"},
                files={"image": (filename, f, "image/jpeg")},
                data={"image_type": "message"}
            )
            key_field = "image_key"
        else:
            resp = requests.post(
                "https://open.feishu.cn/open-apis/im/v1/files",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": (filename, f, "application/octet-stream")},
                data={"file_type": file_type, "file_name": filename}
            )
            key_field = "file_key"

    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"上传失败 {filename}: {data}")
    return data["data"][key_field]

def send_file_msg(token, chat_id, key, msg_type="file", id_type="chat_id"):
    key_field = f"{msg_type}_key"
    resp = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/messages",
        headers={"Authorization": f"Bearer {token}"},
        params={"receive_id_type": id_type},
        json={
            "receive_id": chat_id,
            "msg_type": msg_type,
            "content": json.dumps({key_field: key})
        }
    )
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"发送失败: {data}")
    return data["data"].get("message_id", "?")

def batch_send(chat_id, files, msg_type="file", delay=0.3, max_retries=3):
    token, expire = get_token()
    results = []

    for i, filepath in enumerate(files):
        if not os.path.exists(filepath):
            results.append({"file": filepath, "status": "skip", "error": "文件不存在"})
            print(f"[{i+1}/{len(files)}] ⏭️ 跳过: {filepath} (不存在)")
            continue

        # 检查 token 是否即将过期
        if expire < 300:
            token, expire = get_token()
            print("🔄 Token 已刷新")

        for attempt in range(max_retries):
            try:
                key = upload_file(token, filepath, "stream" if msg_type == "file" else "image")
                msg_id = send_file_msg(token, chat_id, key, msg_type)
                results.append({"file": filepath, "status": "ok", "msg_id": msg_id})
                print(f"[{i+1}/{len(files)}] ✅ {os.path.basename(filepath)} → {msg_id}")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    wait = 2 ** attempt
                    print(f"  ⚠️ 重试 ({attempt+1}/{max_retries}): {e}")
                    time.sleep(wait)
                else:
                    results.append({"file": filepath, "status": "fail", "error": str(e)})
                    print(f"  ❌ 失败: {filepath} - {e}")

        time.sleep(delay)

    # 汇总
    ok = sum(1 for r in results if r["status"] == "ok")
    fail = sum(1 for r in results if r["status"] == "fail")
    skip = sum(1 for r in results if r["status"] == "skip")
    print(f"\n📊 汇总: ✅{ok} ❌{fail} ⏭️{skip} 总计:{len(results)}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="飞书批量发送文件")
    parser.add_argument("--chat-id", required=True, help="飞书聊天 ID (oc_xxx)")
    parser.add_argument("--files", nargs="+", required=True, help="文件路径列表")
    parser.add_argument("--msg-type", default="file", choices=["file", "image"])
    parser.add_argument("--delay", type=float, default=0.3, help="请求间隔(秒)")
    args = parser.parse_args()
    batch_send(args.chat_id, args.files, args.msg_type, args.delay)
