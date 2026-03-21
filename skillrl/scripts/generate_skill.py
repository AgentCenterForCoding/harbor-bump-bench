#!/usr/bin/env python3
"""
skillrl/scripts/generate_skill.py

基于 R0 失败分析，用当前模型生成初版 java-dep-fix SKILL.md（v1）。

用法:
  python generate_skill.py \
    --analysis skillrl/analysis/r0-deep-analysis.json \
    --output skillrl/skills/skill-v1-initial.md
"""

import json
import os
import argparse
from openai import OpenAI


GENERATION_PROMPT = """你是一位 AI Agent Skill 设计专家。你需要为一个修复 Java 依赖升级编译失败的 AI Agent 编写一个 Skill 指导文件（SKILL.md）。

## 背景

AI Agent（Claude Code + qwen3.5-plus）在 100 个 Java Maven 项目的编译修复任务中，成功率为 75%。
以下是对 25 个失败 task 的深度分析结果：

## 失败类别分布
{category_summary}

## 可通过 Skill 改进的失败案例（按 task 详细建议）
{skill_suggestions}

---

## 你的任务

请编写一个 SKILL.md，要求：

1. **YAML frontmatter** 包含 `name: java-dep-fix` 和触发词丰富的 `description`
2. **诊断框架**：说明修复依赖升级编译失败的分层诊断路线（API 变更 vs 包路径迁移 vs 传递依赖缺失等）
3. **五步操作流程**：
   - Step 1: 定位错误（mvn compile、提取 [ERROR] 行）
   - Step 2: 识别变更类型（查 CHANGELOG / javadoc / GitHub diff）
   - Step 3: 制定修复策略（不同错误模式 → 不同操作）
   - Step 4: 实施修复（具体代码改动，含常见模式示例）
   - Step 5: 验证（mvn compile 通过后汇报）
4. **高频错误模式库**：
   - 针对 category_summary 中每个高频类别，给出识别特征 + 对应修复操作
   - 特别强调"传递依赖链检查"（这是最常见的失败原因）
   - 包含 javax→jakarta 命名空间迁移的处理方式
5. **反模式提示**：列出 Agent 最常犯的错误（来自分析结果）
6. **长度控制**：200-300 行，太长会占满 Agent 的上下文窗口

关键原则：
- Skill 是给 AI Agent 看的操作指南，不是给人看的文档
- 要具体到"执行 X 命令 → 看 Y 输出 → 做 Z 操作"，不要泛泛说原因
- 对分析中发现的每一种高频失败，要有对应的具体操作指导

请直接输出完整的 SKILL.md 内容，从 YAML frontmatter 开始，不要有任何解释性前缀。"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis", required=True, help="深度分析 JSON 文件")
    parser.add_argument("--output", required=True, help="输出 SKILL.md 路径")
    parser.add_argument("--model", default="qwen3.5-plus")
    parser.add_argument("--api-base", default=os.environ.get(
        "ANTHROPIC_BASE_URL", "https://coding.dashscope.aliyuncs.com/apps/anthropic"))
    parser.add_argument("--api-key", default=os.environ.get("ANTHROPIC_AUTH_TOKEN", ""))
    args = parser.parse_args()

    with open(args.analysis, encoding="utf-8") as f:
        analysis = json.load(f)

    category_summary = json.dumps(analysis["category_summary"], indent=2, ensure_ascii=False)
    suggestions_text = ""
    for s in analysis.get("skill_suggestions", []):
        suggestions_text += f"\n**[{s['category']}] {s['task']}**:\n{s['suggestion']}\n"

    prompt = GENERATION_PROMPT.format(
        category_summary=category_summary,
        skill_suggestions=suggestions_text[:5000],
    )

    client = OpenAI(base_url=args.api_base, api_key=args.api_key)
    print("正在生成 Skill v1...")

    resp = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=8000,
    )

    skill_content = resp.choices[0].message.content.strip()
    if skill_content.startswith("```"):
        lines = skill_content.split("\n")
        skill_content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(skill_content)

    line_count = len(skill_content.split("\n"))
    print(f"Skill v1 已生成: {args.output}（{line_count} 行）")
    print("\n⚠️  请人工 Review skill-v1-initial.md，确认内容是否合理，必要时手动补充。")


if __name__ == "__main__":
    main()
