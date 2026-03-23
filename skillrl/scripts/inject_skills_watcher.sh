#!/bin/bash
# inject_skills_watcher.sh
#
# 在后台监控 job_dir，每当有新 trial 目录创建时，
# 立即将 ~/.claude/skills/ 复制到 trial_dir/agent/skills/
# 这样容器内 install.sh 执行时能从 /logs/agent/skills/ 读取到 skill
#
# 用法:
#   bash skillrl/scripts/inject_skills_watcher.sh <job_dir> [skills_src]
#
# 示例:
#   bash skillrl/scripts/inject_skills_watcher.sh \
#     jobs/bump-dep-fix-100-skill \
#     ~/.claude/skills

JOB_DIR="${1}"
SKILLS_SRC="${2:-$HOME/.claude/skills}"
INTERVAL=2

if [ -z "$JOB_DIR" ]; then
    echo "用法: $0 <job_dir> [skills_src]"
    exit 1
fi

echo "[inject_skills_watcher] 启动，监控目录: $JOB_DIR"
echo "[inject_skills_watcher] Skills 来源: $SKILLS_SRC"
echo "[inject_skills_watcher] 按 Ctrl+C 停止"

mkdir -p "$JOB_DIR"

declare -A INJECTED

while true; do
    for trial_dir in "$JOB_DIR"/*/; do
        [ -d "$trial_dir" ] || continue
        trial_name=$(basename "$trial_dir")

        # 跳过已处理的
        if [ -n "${INJECTED[$trial_name]+_}" ]; then
            continue
        fi

        agent_dir="$trial_dir/agent"
        if [ -d "$agent_dir" ]; then
            target_skills="$agent_dir/skills"
            if [ ! -d "$target_skills" ] && [ -d "$SKILLS_SRC" ]; then
                mkdir -p "$target_skills"
                cp -r "$SKILLS_SRC/." "$target_skills/"
                echo "[inject_skills_watcher] ✅ 注入 skills -> $target_skills"
                INJECTED[$trial_name]=1
            else
                INJECTED[$trial_name]=1
            fi
        fi
    done
    sleep "$INTERVAL"
done
