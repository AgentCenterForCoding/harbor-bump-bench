#!/usr/bin/env python3
"""
skillrl/scripts/optimize_skill.py

对比 R0/R1 评测结果，分析 delta，然后用 LLM 生成优化后的 Skill v2。

用法:
  python optimize_skill.py \
    --report-r0 skillrl/reports/report-r0.json \
    --report-r1 skillrl/reports/report-r1.json \
    --jobs-dir-r1 /root/harbor-bump-eval/jobs/bump-dep-fix-100-skill-v1 \
    --skill-v1 skillrl/skills/skill-v1-initial.md \
    --output-analysis skillrl/analysis/r1-delta-analysis.json \
    --output-skill skillrl/skills/skill-v2-optimized.md
"""

import json
import os
import argparse
from openai import OpenAI

try:
    from extract_badcases import parse_claude_code_txt, find_trial_dir
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from extract_badcases import parse_claude_code_txt, find_trial_dir


def diff_results(r0_report: dict, r1_report: dict) -> dict:
    """对比两轮结果，分类为 fixed / still_failed / regressed / stable_pass"""
    r0_map = {r.get("task_name", r.get("name", "")): r.get("reward", -1)
              for r in r0_report.get("results", r0_report.get("trials", []))}
    r1_map = {r.get("task_name", r.get("name", "")): r.get("reward", -1)
              for r in r1_report.get("results", r1_report.get("trials", []))}

    all_tasks = sorted(set(r0_map) | set(r1_map))
    fixed, still_failed, regressed, stable_pass = [], [], [], []

    for task in all_tasks:
        r0 = r0_map.get(task, -1)
        r1 = r1_map.get(task, -1)
        if r0 == 0.0 and r1 == 1.0:
            fixed.append(task)
        elif r0 == 0.0 and r1 == 0.0:
            still_failed.append(task)
        elif r0 == 1.0 and r1 == 0.0:
            regressed.append(task)
        else:
            stable_pass.append(task)

    r0_success = sum(1 for v in r0_map.values() if v == 1.0)
    r1_success = sum(1 for v in r1_map.values() if v == 1.0)
    total = len(all_tasks)

    return {
        "fixed": fixed,
        "still_failed": still_failed,
        "regressed": regressed,
        "stable_pass": stable_pass,
        "summary": {
            "r0_success": r0_success,
            "r1_success": r1_success,
            "r0_rate": r0_success / total if total else 0,
            "r1_rate": r1_success / total if total else 0,
            "delta": r1_success - r0_success,
            "fixed_count": len(fixed),
            "regression_count": len(regressed),
            "still_failed_count": len(still_failed),
            "total": total,
        }
    }


OPTIMIZE_PROMPT = """你是一位 AI Agent Skill 优化专家。你需要根据两轮评测的对比结果，优化一个 Java 依赖升级编译修复 Skill。

## 当前 Skill (v1)

```markdown
{current_skill}
```

## 评测对比结果

| 指标 | Round 0（无 Skill） | Round 1（Skill v1） |
|------|-------------------|--------------------|
| 成功数 | {r0_success}/{total} | {r1_success}/{total} |
| 成功率 | {r0_rate:.1f}% | {r1_rate:.1f}% |
| 变化 | — | {delta:+d} 个 task |

- 修复了（R0失败→R1成功）: {fixed_count} 个
- 退步了（R0成功→R1失败）: {regression_count} 个
- 仍然失败: {still_failed_count} 个

### 退步的 task（重点！Skill v1 造成干扰的任务）：
{regression_details}

### 仍然失败的 task（Skill v1 未能覆盖或覆盖不足）：
{still_failed_details}

---

## 你的任务

请基于上述分析，输出优化后的 SKILL.md v2，要求：

1. **保留有效部分**：R1 修复了 {fixed_count} 个 task，说明 Skill v1 中有效的操作应保留
2. **修复退步原因**：
   - 退步通常是 Skill 给出了过于激进的建议，导致 Agent 改动了本不需要改的代码
   - 需要添加"谨慎操作"提示：只改变编译失败直接相关的代码，不要扩大改动范围
3. **补充仍然失败的模式**：
   - 分析仍然失败的 task 名称，推断可能的失败原因（依赖名中有线索），添加对应操作指导
4. **操作隔离原则**：不同类型错误的修复步骤应互相独立，修复一个不影响其他
5. **长度控制**：200-300 行

请直接输出完整的 SKILL.md v2 内容，从 YAML frontmatter 开始。"""


def get_regression_details(regressed: list[str], jobs_dir_r1: str) -> str:
    """获取退步 task 的简要摘要（从 R1 轨迹中）"""
    details = []
    for task in regressed[:8]:
        detail = f"- {task}"
        if jobs_dir_r1:
            trial_dir = find_trial_dir(jobs_dir_r1, task)
            if trial_dir:
                traj = parse_claude_code_txt(trial_dir)
                summary = traj.get("result_summary", "")[:200]
                if summary:
                    detail += f"\n  最终输出: {summary}"
        details.append(detail)
    return "\n".join(details) if details else "（无退步）"


def get_still_failed_details(still_failed: list[str]) -> str:
    lines = [f"- {t}" for t in still_failed[:15]]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-r0", required=True)
    parser.add_argument("--report-r1", required=True)
    parser.add_argument("--jobs-dir-r1", default=None, help="R1 jobs 目录（可选，用于提取退步细节）")
    parser.add_argument("--skill-v1", required=True)
    parser.add_argument("--output-analysis", required=True)
    parser.add_argument("--output-skill", required=True)
    parser.add_argument("--model", default="qwen3.5-plus")
    parser.add_argument("--api-base", default=os.environ.get(
        "ANTHROPIC_BASE_URL", "https://coding.dashscope.aliyuncs.com/apps/anthropic"))
    parser.add_argument("--api-key", default=os.environ.get("ANTHROPIC_AUTH_TOKEN", ""))
    args = parser.parse_args()

    with open(args.report_r0, encoding="utf-8") as f:
        r0 = json.load(f)
    with open(args.report_r1, encoding="utf-8") as f:
        r1 = json.load(f)
    with open(args.skill_v1, encoding="utf-8") as f:
        skill_v1 = f.read()

    diff = diff_results(r0, r1)
    s = diff["summary"]
    print(f"对比结果:")
    print(f"  R0: {s['r0_success']}/{s['total']} = {s['r0_rate']*100:.1f}%")
    print(f"  R1: {s['r1_success']}/{s['total']} = {s['r1_rate']*100:.1f}%")
    print(f"  修复: {s['fixed_count']} | 退步: {s['regression_count']} | 仍失败: {s['still_failed_count']}")

    os.makedirs(os.path.dirname(args.output_analysis), exist_ok=True)
    with open(args.output_analysis, "w", encoding="utf-8") as f:
        json.dump(diff, f, indent=2, ensure_ascii=False)
    print(f"Delta 分析已保存: {args.output_analysis}")

    regression_details = get_regression_details(diff["regressed"], args.jobs_dir_r1)
    still_failed_details = get_still_failed_details(diff["still_failed"])

    prompt = OPTIMIZE_PROMPT.format(
        current_skill=skill_v1[:5000],
        r0_success=s["r0_success"],
        r1_success=s["r1_success"],
        total=s["total"],
        r0_rate=s["r0_rate"] * 100,
        r1_rate=s["r1_rate"] * 100,
        delta=s["delta"],
        fixed_count=s["fixed_count"],
        regression_count=s["regression_count"],
        still_failed_count=s["still_failed_count"],
        regression_details=regression_details,
        still_failed_details=still_failed_details,
    )

    client = OpenAI(base_url=args.api_base, api_key=args.api_key)
    print("\n正在生成 Skill v2...")
    resp = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=8000,
    )

    skill_v2 = resp.choices[0].message.content.strip()
    if skill_v2.startswith("```"):
        lines = skill_v2.split("\n")
        skill_v2 = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    os.makedirs(os.path.dirname(args.output_skill), exist_ok=True)
    with open(args.output_skill, "w", encoding="utf-8") as f:
        f.write(skill_v2)

    print(f"Skill v2 已生成: {args.output_skill}")
    print("\n⚠️  请人工 Review skill-v2-optimized.md，重点检查退步修复 + 新增覆盖。")


if __name__ == "__main__":
    main()
