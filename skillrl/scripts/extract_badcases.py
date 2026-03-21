#!/usr/bin/env python3
"""
skillrl/scripts/extract_badcases.py

从评测结果中提取失败 task 的关键信息，供 LLM 分析。
适配 claude-code.txt JSONL 轨迹格式。

用法:
  # 从 report JSON + jobs 目录提取
  python extract_badcases.py \
    --report skillrl/reports/report-r0.json \
    --jobs-dir /root/harbor-bump-eval/jobs/bump-dep-fix-100-nopre \
    --output skillrl/analysis/r0-badcases.json

  # 直接从 report JSON 提取（无 trajectory 解析）
  python extract_badcases.py \
    --report skillrl/reports/report-r0.json \
    --output skillrl/analysis/r0-badcases.json
"""

import json
import os
import re
import argparse


def find_trial_dir(jobs_dir: str, trial_name: str) -> str | None:
    """在 jobs 目录中找到 trial 对应的子目录（前缀匹配）"""
    if not jobs_dir or not os.path.isdir(jobs_dir):
        return None
    # trial_name 格式: task-bump-xxx__UUID 或 task-xxx__UUID
    for d in os.listdir(jobs_dir):
        if d == trial_name or d.startswith(trial_name.split("__")[0] + "__"):
            full = os.path.join(jobs_dir, d)
            if os.path.isdir(full):
                return full
    return None


def parse_claude_code_txt(trial_dir: str) -> dict:
    """
    解析 agent/claude-code.txt（JSONL 格式），提取：
    - result_summary: 最终 result 消息中的 summary 文本
    - is_error: 是否以错误结束
    - num_turns: Agent 轮数
    - last_bash_outputs: 最后几条 Bash 工具输出（用于提取编译错误）
    - used_skill: 是否调用了 Skill 工具
    """
    txt_path = os.path.join(trial_dir, "agent", "claude-code.txt")
    if not os.path.exists(txt_path):
        return {}

    result_msg = {}
    bash_outputs = []  # (command, output)
    used_skill = False

    with open(txt_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            t = obj.get("type", "")

            # 最终结果
            if t == "result":
                result_msg = obj
                continue

            # Skill 调用检测（assistant 消息中含 Skill tool_use）
            if t == "assistant":
                content = obj.get("message", {}).get("content", [])
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "tool_use":
                        if item.get("name") == "Skill":
                            used_skill = True

            # 工具结果（Bash 输出）
            if t == "tool":
                for item in obj.get("content", []):
                    if isinstance(item, dict) and item.get("type") == "tool_result":
                        # 找到对应的 Bash 命令输出
                        output = ""
                        for c in item.get("content", []):
                            if isinstance(c, dict) and c.get("type") == "text":
                                output += c.get("text", "")
                        if output:
                            bash_outputs.append(output)

    # 只保留最后 5 条 bash 输出（更可能包含编译错误）
    return {
        "result_summary": result_msg.get("result", ""),
        "is_error": result_msg.get("is_error", True),
        "subtype": result_msg.get("subtype", "unknown"),
        "num_turns": result_msg.get("num_turns", 0),
        "used_skill": used_skill,
        "last_bash_outputs": bash_outputs[-5:] if bash_outputs else [],
    }


def extract_compile_errors(bash_outputs: list[str]) -> str:
    """从 Bash 输出中提取编译错误行"""
    for output in reversed(bash_outputs):
        if "BUILD FAILURE" in output or "[ERROR]" in output:
            error_lines = [
                line for line in output.split("\n")
                if "[ERROR]" in line or "ERROR" in line
            ]
            return "\n".join(error_lines[:30])
    return ""


def classify_error_pattern(error_text: str, result_summary: str) -> str:
    """根据错误文本粗分类（规则库）"""
    combined = error_text + " " + result_summary

    if not combined.strip():
        return "no_output"

    if re.search(r"package javax\.\w+ does not exist", combined):
        return "namespace_migration_javax_jakarta"

    pkg_missing = re.findall(r"package ([\w.]+) does not exist", combined)
    if len(pkg_missing) >= 2:
        return "transitive_dependency_missing"

    if re.search(r"cannot find symbol.*symbol:\s+class|symbol:\s+method", combined, re.IGNORECASE | re.DOTALL):
        symbols = re.findall(r"symbol:\s+\w+\s+(\w+)", combined)
        if len(set(symbols)) > 8:
            return "massive_api_change"
        return "symbol_not_found"

    if re.search(r"incompatible types|method does not override|cannot be applied", combined, re.IGNORECASE):
        return "method_signature_change"

    if "timeout" in combined.lower():
        return "timeout"

    return "other"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True, help="评测结果 JSON（含 results 列表）")
    parser.add_argument("--jobs-dir", default=None, help="jobs 目录（可选，提供后解析 trajectory）")
    parser.add_argument("--round", type=int, default=0, help="轮次编号（0/1/2）")
    parser.add_argument("--output", required=True, help="输出文件路径")
    args = parser.parse_args()

    with open(args.report, encoding="utf-8") as f:
        report = json.load(f)

    # 兼容两种 report 格式
    results = report.get("results", report.get("trials", []))
    failed_tasks = [r for r in results if r.get("reward", 1.0) == 0.0]
    print(f"共 {len(failed_tasks)} 个失败 task（总计 {len(results)}）")

    badcases = []
    for task in failed_tasks:
        task_name = task.get("task_name", task.get("name", ""))
        trial = task.get("trial", task_name)

        traj_info = {}
        if args.jobs_dir:
            trial_dir = find_trial_dir(args.jobs_dir, trial)
            if trial_dir:
                traj_info = parse_claude_code_txt(trial_dir)
            else:
                print(f"  [WARN] 未找到 trial 目录: {trial}")

        compile_errors = extract_compile_errors(traj_info.get("last_bash_outputs", []))
        result_summary = traj_info.get("result_summary", "")
        error_pattern = classify_error_pattern(compile_errors, result_summary)

        badcases.append({
            "task_name": task_name,
            "trial": trial,
            "metadata": {
                "project": task.get("project", ""),
                "dep": task.get("dep", ""),
                "prevVersion": task.get("prevVersion", ""),
                "newVersion": task.get("newVersion", ""),
                "updateType": task.get("updateType", ""),
                "javaVersion": task.get("javaVersion", ""),
            },
            "error_pattern": error_pattern,
            "compile_errors": compile_errors[:2000],
            "result_summary": result_summary[:1000],
            "num_turns": traj_info.get("num_turns", 0),
            "used_skill": traj_info.get("used_skill", False),
            "is_timeout": traj_info.get("subtype") == "timeout",
        })
        print(f"  {task_name}: {error_pattern}  turns={traj_info.get('num_turns', '?')}  skill={traj_info.get('used_skill', '?')}")

    pattern_counts = {}
    for bc in badcases:
        p = bc["error_pattern"]
        pattern_counts[p] = pattern_counts.get(p, 0) + 1

    output = {
        "round": args.round,
        "total_failed": len(badcases),
        "pattern_summary": pattern_counts,
        "badcases": badcases,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n结果已写入: {args.output}")
    print(f"失败模式分布: {json.dumps(pattern_counts, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
