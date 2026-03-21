#!/bin/bash
# skillrl/scripts/deploy_skill.sh
#
# 将 SKILL.md 部署到 Agent 主机的 skill 目录
# 部署后，command-0 的 install.sh 会自动 cp -r ~/.claude/skills $CLAUDE_CONFIG_DIR/skills
#
# 用法:
#   ./skillrl/scripts/deploy_skill.sh <skill_file> [agent_skill_dir]
#
# 示例:
#   # 部署 v1（在评测服务器上执行）
#   ./skillrl/scripts/deploy_skill.sh skillrl/skills/skill-v1-initial.md
#
#   # 部署 v2
#   ./skillrl/scripts/deploy_skill.sh skillrl/skills/skill-v2-optimized.md

set -e

SKILL_FILE="${1}"
AGENT_SKILL_DIR="${2:-$HOME/.claude/skills/java-dep-fix}"

if [ -z "$SKILL_FILE" ]; then
    echo "用法: $0 <skill_file> [agent_skill_dir]"
    exit 1
fi

if [ ! -f "$SKILL_FILE" ]; then
    echo "错误: 文件不存在: $SKILL_FILE"
    exit 1
fi

mkdir -p "$AGENT_SKILL_DIR"
cp "$SKILL_FILE" "$AGENT_SKILL_DIR/SKILL.md"

echo "✓ Skill 已部署: $SKILL_FILE → $AGENT_SKILL_DIR/SKILL.md"
echo ""
echo "验证部署结果:"
head -5 "$AGENT_SKILL_DIR/SKILL.md"
echo ""
echo "下一步: 运行 harbor 评测命令"
