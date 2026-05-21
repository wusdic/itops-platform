#!/bin/bash
# ==============================================================================
# ITOps Platform 前端部署脚本
# 功能：构建 → 备份旧版本 → 切换到新版本 → 支持回滚
# 用法：./deploy.sh [--rollback]
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKUP_BASE="$HOME/.hermes/backups/itops_platform"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$BACKUP_BASE/deploy.log"

# ------------------------------------------------------------------------------
# 初始化备份目录
# ------------------------------------------------------------------------------
init_backup_dir() {
    mkdir -p "$BACKUP_BASE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ====== Deploy started ======" >> "$LOG_FILE"
}

# ------------------------------------------------------------------------------
# 回滚操作
# ------------------------------------------------------------------------------
do_rollback() {
    local prev_link="$BACKUP_BASE/previous"

    if [ ! -L "$prev_link" ] || [ ! -d "$prev_link" ]; then
        echo "❌ 没有可用的回滚版本（previous 链接不存在）"
        exit 1
    fi

    local rollback_target=$(readlink -f "$prev_link")
    local current_dist="$FRONTEND_DIR/dist"
    local rollback_backup="$BACKUP_BASE/dist_$(date +%Y%m%d_%H%M%S)_rollback_backup"

    echo "⚠️  回滚操作"
    echo "   回滚到:   $rollback_target"
    echo ""

    read -p "确认回滚？ (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "已取消"
        exit 0
    fi

    # 备份当前版本（仅当 zcxx 持有时）
    if [ -d "$current_dist" ] && [ -O "$current_dist" ]; then
        echo "📦 备份当前版本到: $rollback_backup"
        cp -a "$current_dist" "$rollback_backup"
    fi

    # 用 rsync 恢复（避免 mv bug）
    echo "⚙️  恢复 dist/ ..."
    rsync -a "$rollback_target/" "$current_dist/"
    chmod -R a+rX "$current_dist" 2>/dev/null || true

    # 更新 previous 链接指向这次回滚的版本
    if [ -d "$rollback_backup" ]; then
        ln -sfn "$rollback_backup" "$prev_link"
    fi

    echo "✅ 回滚完成"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ROLLBACK to $rollback_target" >> "$LOG_FILE"
}

# ------------------------------------------------------------------------------
# 构建新版本
# ------------------------------------------------------------------------------
do_build() {
    echo "🔨 开始构建..."
    cd "$FRONTEND_DIR"

    # 清理旧 dist-new（如果存在且为其他用户拥有则跳过清理）
    if [ -d "$FRONTEND_DIR/dist-new" ]; then
        if [ -O "$FRONTEND_DIR/dist-new" ]; then
            rm -rf "$FRONTEND_DIR/dist-new"
        else
            echo "⚠️  dist-new 已被其他用户拥有，跳过清理"
        fi
    fi

    npm run build

    if [ ! -d "$FRONTEND_DIR/dist-new" ]; then
        echo "❌ 构建失败：dist-new 目录不存在"
        exit 1
    fi

    echo "✅ 构建成功"
}

# ------------------------------------------------------------------------------
# 部署新版本
# ------------------------------------------------------------------------------
do_deploy() {
    echo ""
    echo "🚀 开始部署..."

    local current_dist="$FRONTEND_DIR/dist"
    local new_dist="$FRONTEND_DIR/dist-new"
    local backup_path="$BACKUP_BASE/dist_$TIMESTAMP"
    local prev_link="$BACKUP_BASE/previous"

    # 1. 备份当前版本（仅当可读时）
    if [ -d "$current_dist" ]; then
        if [ -O "$current_dist" ]; then
            echo "📦 备份当前版本到: $backup_path"
            cp -a "$current_dist" "$backup_path"
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup: $backup_path" >> "$LOG_FILE"
        else
            echo "⚠️  当前 dist/ 被 root 拥有，无法备份（Docker 环境正常，跳过）"
        fi
    fi

    # 2. 如果有旧的 previous 备份，清理（只保留一个 previous）
    if [ -L "$prev_link" ]; then
        local prev_target=$(readlink -f "$prev_link")
        if [ "$prev_target" != "$backup_path" ] && [ -d "$prev_target" ]; then
            rm -rf "$prev_target"
            echo "🗑️  清理旧 previous: $prev_target"
        fi
    fi

    # 3. 建立 previous 链接（指向可用的旧版本，备用回滚）
    if [ -d "$backup_path" ]; then
        ln -sfn "$backup_path" "$prev_link"
        echo "🔗 previous → $backup_path"
    fi

    # 4. 替换 dist/
    #    关键：必须用 rsync 或显式路径，避免 mv 误将 dist-new 作为子目录移入 dist/
    echo "⚙️  替换 dist/ ..."

    # 4a. 如果 dist/ 已存在，先备份再清理（zcxx 持有的部分）
    if [ -d "$current_dist" ]; then
        # 只删除 zcxx 持有的子目录（assets_old, dist-new 等残余）
        for subdir in assets_old dist-new; do
            if [ -d "$current_dist/$subdir" ] && [ -O "$current_dist/$subdir" ]; then
                rm -rf "$current_dist/$subdir" && echo "   🗑️  清理残余目录 $current_dist/$subdir"
            fi
        done
        # 如果整个 dist 都是 zcxx 持有，直接清空
        if [ -O "$current_dist" ]; then
            # 先把 index.html 移出（避免与 dist-new 的 index.html 冲突）
            [ -f "$current_dist/index.html" ] && mv "$current_dist/index.html" /tmp/dist_index_old_$$.html
            # 用 rsync 把 dist-new 的内容同步进来（保留目录本身）
            rsync -a "$new_dist/" "$current_dist/"
            [ -f /tmp/dist_index_old_$$.html ] && mv /tmp/dist_index_old_$$.html "$current_dist/index.html"
        else
            # dist 部分是 root 持有，只替换 assets 目录
            rsync -a "$new_dist/assets/" "$current_dist/assets/"
            [ -f "$new_dist/index.html" ] && cp "$new_dist/index.html" "$current_dist/index.html"
        fi
    else
        # dist 完全不存在，直接移动
        mv "$new_dist" "$current_dist"
    fi

    # 5. 确保权限可读
    chmod -R a+rX "$current_dist" 2>/dev/null || true

    # 6. 清理 dist-new（如果还存在）
    [ -d "$new_dist" ] && rm -rf "$new_dist" && echo "🧹 清理残留 dist-new"

    # 7. 记录
    echo "✅ 部署完成，版本: $TIMESTAMP"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Deployed: $TIMESTAMP" >> "$LOG_FILE"
    echo ""
    echo "📋 备份目录: $BACKUP_BASE"
    echo "🔄 回滚: ./deploy.sh --rollback"
}

# ------------------------------------------------------------------------------
# 查看状态
# ------------------------------------------------------------------------------
do_status() {
    echo "📊 部署状态"
    echo ""
    echo "当前 dist/:"
    if [ -L "$FRONTEND_DIR/dist" ]; then
        echo "   链接 → $(readlink -f "$FRONTEND_DIR/dist")"
    elif [ -d "$FRONTEND_DIR/dist" ]; then
        echo "   目录（owner: $(stat -c '%U' "$FRONTEND_DIR/dist" 2>/dev/null || echo 'unknown')）"
    else
        echo "   不存在"
    fi
    echo ""
    echo "dist-new/:"
    if [ -d "$FRONTEND_DIR/dist-new" ]; then
        echo "   目录（owner: $(stat -c '%U' "$FRONTEND_DIR/dist-new" 2>/dev/null || echo 'unknown')）"
    else
        echo "   不存在"
    fi
    echo ""
    echo "previous 链接:"
    if [ -L "$BACKUP_BASE/previous" ]; then
        echo "   $(readlink -f "$BACKUP_BASE/previous")"
    else
        echo "   无"
    fi
    echo ""
    echo "备份历史:"
    ls -lt "$BACKUP_BASE"/dist_* 2>/dev/null | head -5 | awk '{print "   " $9, "(" $6, $7, $8 ")"}'
    echo ""
    echo "部署日志（最近10条）:"
    tail -10 "$LOG_FILE" 2>/dev/null | sed 's/^/   /'
}

# ------------------------------------------------------------------------------
# 主流程
# ------------------------------------------------------------------------------
init_backup_dir

if [ "$1" == "--rollback" ]; then
    do_rollback
elif [ "$1" == "--status" ]; then
    do_status
elif [ "$1" == "--build-only" ]; then
    do_build
else
    do_build
    do_deploy
    echo ""
    echo "⚠️  重要：main.py 中的 dist_path 需同步更新为 dist"
    echo "   或运行此脚本后，重启后端服务使静态文件生效"
fi
