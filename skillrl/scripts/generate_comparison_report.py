#!/usr/bin/env python3
"""
skillrl/scripts/generate_comparison_report.py

生成三轮评测对比报告（JSON + Markdown）。

用法:
  python generate_comparison_report.py \
    --r0 skillrl/reports/report-r0.json \
    --r1 skillrl/reports/report-r1.json \
    --r2 skillrl/reports/report-r2.json \
    --output-json skillrl/reports/comparison-report.json \
    --output-md skillrl/reports/comparison-report.md
"""

import json
import os
import argparse
from datetime import datetime


def load_report(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def task_prefix(task_name: str) -> str:
    """去掉末尾随机 ID（__XXXXXXX），返回可跨轮对比的前缀"""
    return task_name.rsplit("__", 1)[0]


def get_results_map(report: dict) -> dict[str, float]:
    """返回 prefix -> reward 映射（best-of 取最高分）"""
    results = report.get("results", report.get("trials", []))
    prefix_map: dict[str, float] = {}
    for r in results:
        name = r.get("task_name", r.get("name", ""))
        prefix = task_prefix(name)
        reward = r.get("reward", -1)
        # 取 best（reward=1.0 优先）
        if prefix not in prefix_map or reward > prefix_map[prefix]:
            prefix_map[prefix] = reward
    return prefix_map


def per_task_diff(r0: dict, r1: dict, r2: dict) -> list[dict]:
    r0_map = get_results_map(r0)
    r1_map = get_results_map(r1)
    r2_map = get_results_map(r2)
    all_tasks = sorted(set(r0_map) | set(r1_map) | set(r2_map))

    rows = []
    for t in all_tasks:
        rows.append({
            "task_name": t,
            "r0": r0_map.get(t, -1),
            "r1": r1_map.get(t, -1),
            "r2": r2_map.get(t, -1),
            "dep": next(
                (r.get("dep", "") for r in r0.get("results", [])
                 if task_prefix(r.get("task_name", "")) == t), ""),
            "updateType": next(
                (r.get("updateType", "") for r in r0.get("results", [])
                 if task_prefix(r.get("task_name", "")) == t), ""),
        })
    return rows


def classify_trajectory(row: dict) -> str:
    r0, r1, r2 = row["r0"], row["r1"], row["r2"]
    if r0 == 1 and r1 == 1 and r2 == 1:
        return "always_pass"
    if r0 == 0 and r1 == 0 and r2 == 0:
        return "never_fixed"
    if r0 == 0 and r1 == 1 and r2 == 1:
        return "fixed_by_v1"
    if r0 == 0 and r1 == 0 and r2 == 1:
        return "fixed_by_v2"
    if r0 == 0 and r1 == 1 and r2 == 0:
        return "v1_only"
    if r0 == 1 and r1 == 0 and r2 == 1:
        return "v1_regress_v2_fixed"
    if r0 == 1 and r1 == 0 and r2 == 0:
        return "regressed_by_v1"
    if r0 == 1 and r1 == 1 and r2 == 0:
        return "regressed_by_v2"
    return "other"


def count_success(report: dict) -> tuple[int, int]:
    """基于 prefix 去重后统计成功/总数（与 result_merged 保持一致）"""
    prefix_map = get_results_map(report)
    total = report.get("n_total_trials", len(prefix_map))
    success = sum(1 for v in prefix_map.values() if v == 1.0)
    return success, total


def generate_markdown(r0: dict, r1: dict, r2: dict, rows: list, traj_summary: dict) -> str:
    r0_s, r0_t = count_success(r0)
    r1_s, r1_t = count_success(r1)
    r2_s, r2_t = count_success(r2)
    d1 = (r1_s / r1_t - r0_s / r0_t) * 100 if r0_t and r1_t else 0
    d2 = (r2_s / r2_t - r0_s / r0_t) * 100 if r0_t and r2_t else 0

    md = [
        "# SkillRL 三轮评测对比报告\n",
        f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"**测评集**: {r0_t} tasks  |  **模型**: qwen3.5-plus\n",
        "\n---\n",
        "## 1. 总览\n",
        "| 指标 | Round 0（无 Skill） | Round 1（Skill v1） | Round 2（Skill v2） |",
        "|------|-------------------|--------------------|---------------------|",
        f"| **成功数** | {r0_s} | {r1_s} | {r2_s} |",
        f"| **失败数** | {r0_t - r0_s} | {r1_t - r1_s} | {r2_t - r2_s} |",
        f"| **成功率** | {r0_s/r0_t*100:.1f}% | {r1_s/r1_t*100:.1f}% | {r2_s/r2_t*100:.1f}% |",
        f"| **vs 基线** | — | {d1:+.1f}% | {d2:+.1f}% |",
        "",
        "## 2. Task 轨迹分类\n",
        "| 轨迹类型 | 数量 | 说明 |",
        "|---------|------|------|",
    ]

    labels = {
        "always_pass":       ("始终通过",       "三轮全部成功"),
        "fixed_by_v1":       ("v1 修复并稳定",  "Skill v1 有效，且 v2 保持"),
        "fixed_by_v2":       ("v2 额外修复",    "Skill v2 才解决"),
        "v1_only":           ("v1 修复但 v2 退步", "需检查 v2 是否引入干扰"),
        "v1_regress_v2_fixed": ("v1 退步 v2 修复", "v2 纠正了 v1 的问题"),
        "regressed_by_v1":   ("v1 导致退步",    "Skill 干扰了原本可以成功的 task"),
        "regressed_by_v2":   ("v2 导致退步",    "v2 优化引入新问题"),
        "never_fixed":       ("始终失败",       "三轮全部失败，超出 Skill 能力范围"),
        "other":             ("其他",           ""),
    }
    for key, (label, desc) in labels.items():
        count = traj_summary.get(key, 0)
        if count > 0:
            md.append(f"| {label} | **{count}** | {desc} |")

    md += [
        "",
        "## 3. 关键结论\n",
        f"- Skill v1 直接修复了 **{traj_summary.get('fixed_by_v1', 0) + traj_summary.get('v1_only', 0)}** 个 task",
        f"- Skill v2 额外修复了 **{traj_summary.get('fixed_by_v2', 0)}** 个 task",
        f"- 始终失败（模型能力瓶颈）: **{traj_summary.get('never_fixed', 0)}** 个",
    ]

    v1_reg = traj_summary.get("regressed_by_v1", 0)
    v2_reg = traj_summary.get("regressed_by_v2", 0)
    if v1_reg > 0:
        md.append(f"- ⚠️  Skill v1 退步: **{v1_reg}** 个 task（Skill 内容过于激进）")
    if v2_reg > 0:
        md.append(f"- ⚠️  Skill v2 退步: **{v2_reg}** 个 task（v2 优化引入新问题）")

    md += [
        "",
        "## 4. 各 Task 详细结果\n",
        "| Task | 依赖 | 升级类型 | R0 | R1 | R2 | 轨迹 |",
        "|------|------|----------|----|----|----|----|",
    ]
    traj_labels = {
        "always_pass": "✅始终通过",
        "fixed_by_v1": "🔧v1修复",
        "fixed_by_v2": "🔧v2修复",
        "v1_only": "⚠️v1修v2退",
        "v1_regress_v2_fixed": "🔄v1退v2修",
        "regressed_by_v1": "❌v1退步",
        "regressed_by_v2": "❌v2退步",
        "never_fixed": "💀始终失败",
        "other": "？其他",
    }
    for row in sorted(rows, key=lambda x: x["task_name"]):
        traj = classify_trajectory(row)
        r0_icon = "✅" if row["r0"] == 1 else "❌"
        r1_icon = "✅" if row["r1"] == 1 else "❌"
        r2_icon = "✅" if row["r2"] == 1 else "❌"
        label = traj_labels.get(traj, traj)
        dep = (row.get("dep") or "")[:30]
        md.append(f"| `{row['task_name'][:45]}` | {dep} | {row.get('updateType','')} | {r0_icon} | {r1_icon} | {r2_icon} | {label} |")

    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--r0", required=True)
    parser.add_argument("--r1", required=True)
    parser.add_argument("--r2", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    r0, r1, r2 = load_report(args.r0), load_report(args.r1), load_report(args.r2)
    rows = per_task_diff(r0, r1, r2)

    traj_summary = {}
    for row in rows:
        traj = classify_trajectory(row)
        traj_summary[traj] = traj_summary.get(traj, 0) + 1

    r0_s, r0_t = count_success(r0)
    r1_s, r1_t = count_success(r1)
    r2_s, r2_t = count_success(r2)

    comparison = {
        "generated_at": datetime.now().isoformat(),
        "rounds": {
            "r0": {"success": r0_s, "total": r0_t, "rate": r0_s / r0_t if r0_t else 0},
            "r1": {"success": r1_s, "total": r1_t, "rate": r1_s / r1_t if r1_t else 0},
            "r2": {"success": r2_s, "total": r2_t, "rate": r2_s / r2_t if r2_t else 0},
        },
        "trajectory_summary": traj_summary,
        "per_task": rows,
    }

    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    os.makedirs(os.path.dirname(args.output_md), exist_ok=True)
    md = generate_markdown(r0, r1, r2, rows, traj_summary)
    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"对比报告已生成:")
    print(f"  JSON: {args.output_json}")
    print(f"  Markdown: {args.output_md}")
    print(f"\n结果:")
    print(f"  R0: {r0_s/r0_t*100:.1f}%")
    print(f"  R1: {r1_s/r1_t*100:.1f}%  ({(r1_s/r1_t - r0_s/r0_t)*100:+.1f}%)")
    print(f"  R2: {r2_s/r2_t*100:.1f}%  ({(r2_s/r2_t - r0_s/r0_t)*100:+.1f}%)")
    print(f"\n轨迹分布: {json.dumps(traj_summary, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
