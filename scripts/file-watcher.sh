#!/bin/bash
# Hermes File Watcher Daemon (v4.1 - True Background Indexing)
# v4.0 有个问题：如果事件停止，read 阻塞，索引更新检查就不会执行。
# 这里引入一个后台任务来定期检查和更新索引。

HERMES_DIR="/home/ubuntu/.hermes"
LOG="$HERMES_DIR/watcher.log"
INDEX_SCRIPT="$HERMES_DIR/scripts/file-index.py"
ORGANIZE_SCRIPT="$HERMES_DIR/scripts/file-organize-single.py"

echo "🚀 Hermes 文件治理守护者 (Bash v4.1) 启动" >> $LOG
echo "📅 动态索引: 后台自动维护" >> $LOG

# --- 索引守护进程 ---
# 每 5 秒检查一次，如果有变动且处于安静状态，则更新索引
index_daemon() {
    local LAST_CHANGE=0
    local COOLDOWN=5  # 变动后等待 5 秒

    while true; do
        if [ -f /tmp/hermes_fs_dirty ]; then
            local CHANGE_TIME=$(stat -c %Y /tmp/hermes_fs_dirty)
            local NOW=$(date +%s)
            
            if [ $((NOW - CHANGE_TIME)) -ge $COOLDOWN ]; then
                # 安静了 5 秒，更新索引！
                rm -f /tmp/hermes_fs_dirty
                echo "$(date +%H:%M:%S) 🔄 正在更新全局索引..." >> $LOG
                /usr/bin/python3 -u "$INDEX_SCRIPT" >> $LOG 2>&1
                echo "$(date +%H:%M:%S) ✅ 索引更新完成" >> $LOG
            fi
        fi
        sleep 5
    done
}

# 启动后台索引守护进程
index_daemon &
INDEX_PID=$!
echo "Index Daemon PID: $INDEX_PID" >> $LOG

# 确保 inotifywait 存在
if ! command -v inotifywait &> /dev/null; then
    echo "❌ inotifywait 未安装！" >> $LOG
    kill $INDEX_PID
    exit 1
fi

# --- 事件处理循环 ---
inotifywait -m -e create,modify,moved_to,delete --exclude '(output/|archive/|scripts/|skills/|cache/|node_modules/|cron/)' --format '%w%f' "$HERMES_DIR" | while read FILEPATH; do
    
    # 忽略目录变动
    [ -d "$FILEPATH" ] && continue
    
    FILENAME=$(basename "$FILEPATH")
    
    # 忽略文件
    [[ "$FILENAME" == .* ]] && continue
    [[ "$FILENAME" == "watcher.log" ]] && continue
    [[ "$FILENAME" == "FILE_INDEX.md" ]] && continue
    [[ "$FILENAME" == "FILE_INDEX.json" ]] && continue
    [[ "$FILENAME" == "governance.yaml" ]] && continue # 别把自己更新了导致循环

    # 标记系统为 "Dirty" (触发索引更新倒计时)
    touch /tmp/hermes_fs_dirty

    # 如果是创建或移入，尝试进行文件治理
    # 为了减少竞争，稍微等一下确保文件写完
    sleep 0.5
    
    [ ! -f "$FILEPATH" ] && continue

    # 执行治理
    # 注意：file-organize-single.py 也会修改文件系统，这会再次触发 inotifywait
    # 但我们的 exclude 规则排除了 output/ 等目录，且 ignore_patterns 会处理保护文件
    # 所以不会造成无限循环，只是会再次标记 dirty (没关系，只是重置时间)
    /usr/bin/python3 -u "$ORGANIZE_SCRIPT" "$FILEPATH" >> $LOG 2>&1
    
done

# 清理
kill $INDEX_PID
