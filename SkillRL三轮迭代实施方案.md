# SkillRL 三轮迭代实施方案

**版本**：v1.0
**日期**：2026-03-21
**目标**：从零 Skill 出发，通过 3 轮"评测→归因→生成/优化 Skill→再评测"闭环，量化 Skill 对 Agent 修复能力的提升效果

---

## 总体流程

```
Round 0: 无 Skill 基线
  │  运行 100 tasks 评测
  │  输出 report-r0.json
  ▼
Phase A: Bad Case 归因
  │  脚本提取失败 task 编译错误特征
  │  当前模型分析 trajectory → 失败分类
  ▼
Round 1: 初版 Skill
  │  基于归因结果生成 java-dep-fix SKILL.md v1
  | git commit
  │  运行 100 tasks 评测
  │  输出 report-r1.json
  ▼
Phase B: 增量归因
  │  对比 R0/R1 结果，分析 R1 新增失败 + 残留失败
  │  当前模型分析 → 优化建议
  ▼
Round 2: 优化 Skill
  │  基于增量归因优化 SKILL.md v2
  |git commit
  │  运行 100 tasks 评测
  │  输出 report-r2.json
  ▼
Final: 三轮对比报告
  │  generate_comparison_report.py
  │  输出 comparison-report.md + comparison-report.json
  ▼
Done
```

---

## 目录结构

```
harbor-bump-eval/                          # 评测服务器 /root/harbor-bump-eval/
├── skillrl/                               # ★ 新增：SkillRL 工作目录
│   ├── scripts/
│   │   ├── extract_badcases.py            # Phase A/B: 从 report 提取失败 task 列表
│   │   ├── classify_failures.py           # Phase A/B: 分析 trajectory 做失败归因
│   │   ├── generate_skill.py              # Round 1: 基于归因生成初版 Skill
│   │   ├── optimize_skill.py              # Round 2: 基于增量归因优化 Skill
│   │   ├── generate_comparison_report.py  # Final: 三轮对比报告
│   │   └── deploy_skill.sh               # 辅助: 将 SKILL.md 部署到 Agent 环境
│   ├── configs/
│   │   ├── job-r0-noskill.yaml            # Round 0 评测配置
│   │   ├── job-r1-skill-v1.yaml           # Round 1 评测配置
│   │   └── job-r2-skill-v2.yaml           # Round 2 评测配置
│   ├── skills/
│   │   ├── skill-v0-none.md               # 占位: 无 Skill
│   │   ├── skill-v1-initial.md            # Round 1 生成的初版 Skill
│   │   └── skill-v2-optimized.md          # Round 2 优化后的 Skill
│   ├── analysis/
│   │   ├── r0-badcases.json               # Round 0 失败归因结果
│   │   ├── r1-badcases.json               # Round 1 失败归因结果
│   │   └── r1-delta-analysis.json         # Round 1→2 增量分析
│   └── reports/
│       ├── report-r0.json                 # Round 0 评测报告
│       ├── report-r1.json                 # Round 1 评测报告
│       ├── report-r2.json                 # Round 2 评测报告
│       └── comparison-report.md           # 三轮对比报告
├── jobs/                                  # 已有: 评测运行目录
├── task-*/                                # 已有: 任务定义
└── job-*.yaml                             # 已有: 评测配置
```

---

## Round 0：无 Skill 基线评测

### 目的

获取 Agent **裸跑**（无任何 java-dep-fix Skill 注入）时的修复成功率作为基线。

> **注意**：如果当前 `report-100tasks.json`（75% 成功率）就是无 Skill 跑的，可直接复用为 R0 基线，跳过此轮评测。需要确认 `job-100tasks-nopre.yaml` 运行时是否加载了 java-dep-fix Skill。

### 评测配置

```yaml
# skillrl/configs/job-r0-noskill.yaml
job_name: skillrl-r0-noskill
jobs_dir: /root/harbor-bump-eval/jobs

orchestrator:
  n_concurrent_trials: 3

agents:
  - name: claude-code
    env:
      ANTHROPIC_AUTH_TOKEN: "${ANTHROPIC_AUTH_TOKEN}"
      ANTHROPIC_BASE_URL: "https://coding.dashscope.aliyuncs.com/apps/anthropic"
      ANTHROPIC_MODEL: "qwen3.5-plus"
      ANTHROPIC_SMALL_FAST_MODEL: "qwen3.5-plus"
      # 关键: 不注入任何 Skill，Agent 仅依赖 instruction.md 中的指引

datasets:
  - path: /root/harbor-bump-eval
    task_names:
      # ... 100 个 task（同 job-100tasks-nopre.yaml 完整列表）
```

### 执行

```bash
# 在评测服务器上
cd /root/harbor-bump-eval
harbor run skillrl/configs/job-r0-noskill.yaml

# 完成后生成报告
python skillrl/scripts/extract_badcases.py \
  --job-dir jobs/skillrl-r0-noskill \
  --output skillrl/reports/report-r0.json
```

### 预期输出

```json
{
  "round": 0,
  "skill_version": "none",
  "total": 100,
  "success": 75,
  "failed": 25,
  "success_rate": 0.75,
  "results": [...]
}
```

---

## Phase A：Bad Case 失败归因（R0 → Skill v1）

### 目的

从 Round 0 的 25 个失败 task 中提取失败模式，用当前模型（qwen3.5-plus）自动分类归因，作为生成初版 Skill 的输入。

### Step A1：提取失败 task 的关键特征

```python
#!/usr/bin/env python3
"""
skillrl/scripts/extract_badcases.py

从评测结果中提取失败 task 的关键信息：
- 最后一次编译错误
- Agent 的修复策略（从 trajectory 中提取）
- 任务元数据（依赖、版本、updateType）
"""

import json
import os
import re
import sys
import argparse


def extract_last_compile_errors(trajectory: dict) -> str:
    """从 trajectory 中提取最后一次 mvn compile 的错误输出"""
    steps = trajectory.get("steps", [])
    last_compile_output = ""

    for step in reversed(steps):
        tool_calls = step.get("tool_calls", [])
        obs = step.get("observation", {})
        results = obs.get("results", []) if obs else []

        for tc in tool_calls:
            cmd = tc.get("arguments", {}).get("command", "")
            if "mvn compile" in cmd or "mvn install" in cmd:
                # 找到对应的 observation
                call_id = tc.get("tool_call_id", "")
                for r in results:
                    if r.get("source_call_id") == call_id:
                        last_compile_output = r.get("content", "")
                        break
                if last_compile_output:
                    break
        if last_compile_output:
            break

    # 提取 [ERROR] 行
    error_lines = [
        line for line in last_compile_output.split("\n")
        if "[ERROR]" in line
    ]
    return "\n".join(error_lines[:30])


def extract_agent_strategy(trajectory: dict) -> str:
    """从 trajectory 中提取 Agent 的主要修复动作摘要"""
    steps = trajectory.get("steps", [])
    actions = []

    for step in steps:
        if step.get("source") != "agent":
            continue
        tool_calls = step.get("tool_calls", [])
        for tc in tool_calls:
            fn = tc.get("function_name", "")
            args = tc.get("arguments", {})
            if fn == "Edit":
                file_path = args.get("file_path", "")
                actions.append(f"Edit: {os.path.basename(file_path)}")
            elif fn == "Bash":
                cmd = args.get("command", "")[:80]
                if "mvn" in cmd or "grep" in cmd or "find" in cmd:
                    actions.append(f"Bash: {cmd}")

    # 去重并限制数量
    seen = set()
    unique = []
    for a in actions:
        if a not in seen:
            seen.add(a)
            unique.append(a)
    return "\n".join(unique[:20])


def count_agent_steps(trajectory: dict) -> int:
    """统计 Agent 的总步骤数"""
    return len([s for s in trajectory.get("steps", []) if s.get("source") == "agent"])


def detect_timeout(trajectory: dict) -> bool:
    """检测是否因超时终止"""
    steps = trajectory.get("steps", [])
    if not steps:
        return False
    last = steps[-1]
    msg = last.get("message", "")
    return "timeout" in msg.lower() or "AgentTimeoutError" in msg


def classify_error_pattern(error_text: str) -> str:
    """基于编译错误文本做规则分类（初步）"""
    if not error_text:
        return "no_compile_output"

    # 命名空间迁移
    if re.search(r"package javax\.\w+ does not exist", error_text):
        return "namespace_migration_javax_jakarta"

    # 传递依赖缺失（非项目内的 package does not exist）
    pkg_missing = re.findall(r"package ([\w.]+) does not exist", error_text)
    if pkg_missing:
        # 判断是否为外部包
        external_count = sum(1 for p in pkg_missing if not p.startswith("com.github"))
        if external_count >= 2:
            return "transitive_dependency_missing"

    # 泛型不兼容
    if re.search(r"incompatible types.*generic|incompatible types.*<", error_text, re.IGNORECASE):
        return "generic_type_incompatibility"

    # 大量 cannot find symbol（>10个不同的符号）
    symbols = re.findall(r"cannot find symbol.*symbol:\s+(\w+\s+\w+)", error_text)
    if len(set(symbols)) > 10:
        return "massive_api_change"

    # 方法签名变更
    if re.search(r"cannot be applied|method does not override", error_text):
        return "method_signature_change"

    # 单个/少量 cannot find symbol
    if "cannot find symbol" in error_text:
        return "symbol_not_found"

    return "other"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-dir", required=True, help="Job 运行目录")
    parser.add_argument("--report", default=None, help="已有的 report.json（可选，直接提供则跳过扫描）")
    parser.add_argument("--output", required=True, help="输出文件路径")
    args = parser.parse_args()

    # 加载评测结果
    if args.report:
        with open(args.report) as f:
            report = json.load(f)
    else:
        result_path = os.path.join(args.job_dir, "result.json")
        with open(result_path) as f:
            report = json.load(f)

    # 筛选失败 task
    failed_tasks = [r for r in report.get("results", []) if r.get("reward", 1.0) == 0.0]
    print(f"共 {len(failed_tasks)} 个失败 task")

    badcases = []
    for task in failed_tasks:
        task_name = task.get("task_name", "")
        trial = task.get("trial", "")

        # 读取 trajectory
        traj_path = os.path.join(args.job_dir, trial, "agent", "trajectory.json")
        if not os.path.exists(traj_path):
            print(f"  [WARN] trajectory 不存在: {traj_path}")
            badcases.append({
                "task_name": task_name,
                "trial": trial,
                "metadata": task,
                "error_pattern": "trajectory_missing",
                "compile_errors": "",
                "agent_strategy": "",
                "agent_steps": 0,
                "is_timeout": False,
            })
            continue

        with open(traj_path) as f:
            traj = json.load(f)

        compile_errors = extract_last_compile_errors(traj)
        agent_strategy = extract_agent_strategy(traj)
        agent_steps = count_agent_steps(traj)
        is_timeout = detect_timeout(traj)
        error_pattern = "timeout" if is_timeout else classify_error_pattern(compile_errors)

        badcases.append({
            "task_name": task_name,
            "trial": trial,
            "metadata": {
                "project": task.get("project"),
                "dep": task.get("dep"),
                "prevVersion": task.get("prevVersion"),
                "newVersion": task.get("newVersion"),
                "updateType": task.get("updateType"),
                "javaVersion": task.get("javaVersion"),
            },
            "error_pattern": error_pattern,
            "compile_errors": compile_errors[:2000],  # 截断
            "agent_strategy": agent_strategy,
            "agent_steps": agent_steps,
            "is_timeout": is_timeout,
        })
        print(f"  {task_name}: {error_pattern} (steps={agent_steps}, timeout={is_timeout})")

    # 统计分类
    pattern_counts = {}
    for bc in badcases:
        p = bc["error_pattern"]
        pattern_counts[p] = pattern_counts.get(p, 0) + 1

    output = {
        "round": 0,
        "total_failed": len(badcases),
        "pattern_summary": pattern_counts,
        "badcases": badcases,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n归因结果已写入: {args.output}")
    print(f"失败模式分布: {json.dumps(pattern_counts, indent=2)}")


if __name__ == "__main__":
    main()
```

### Step A2：用当前模型做深层归因

```python
#!/usr/bin/env python3
"""
skillrl/scripts/classify_failures.py

用当前模型（qwen3.5-plus）分析每个失败 task 的 trajectory，
输出深层归因和 Skill 改进建议。

用法:
  python classify_failures.py \
    --badcases skillrl/analysis/r0-badcases.json \
    --output skillrl/analysis/r0-deep-analysis.json
"""

import json
import os
import sys
import argparse
from openai import OpenAI  # 兼容 OpenAI 协议的客户端


ANALYSIS_PROMPT = """你是一位 Java 依赖升级修复专家。以下是一个 AI Agent 尝试修复 Java 依赖升级编译失败的记录，但最终修复**失败**了。

## 任务信息
- 项目: {project}
- 依赖: {dep}
- 版本变更: {prev_version} → {new_version}
- 更新类型: {update_type}
- Java 版本: {java_version}

## 编译错误（最后一次 mvn compile 的输出）
```
{compile_errors}
```

## Agent 的修复动作摘要
```
{agent_strategy}
```

## Agent 步骤数: {agent_steps}
## 是否超时: {is_timeout}
## 规则分类: {error_pattern}

---

请分析这个失败案例，输出以下 JSON 格式（不要包含其他文字）：

```json
{{
  "failure_category": "从以下选择一个: namespace_migration | transitive_dependency | api_signature_change | ecosystem_incompatibility | agent_strategy_error | timeout_complexity | model_capability_limit | other",
  "root_cause": "一句话描述根本原因",
  "agent_mistake": "Agent 在修复过程中犯了什么错误？如果 Agent 的策略正确但问题本身太难，写'问题超出当前能力'",
  "skill_suggestion": "如果有一个 Skill 来指导 Agent，应该包含什么规则/知识才能避免这个失败？具体到可执行的指令",
  "fixable_by_skill": true/false,
  "confidence": 0.0-1.0
}}
```"""


def analyze_single_badcase(client, badcase: dict) -> dict:
    """用 LLM 分析单个失败案例"""
    meta = badcase.get("metadata", {})
    prompt = ANALYSIS_PROMPT.format(
        project=meta.get("project", "unknown"),
        dep=meta.get("dep", "unknown"),
        prev_version=meta.get("prevVersion", "?"),
        new_version=meta.get("newVersion", "?"),
        update_type=meta.get("updateType", "unknown"),
        java_version=meta.get("javaVersion", "?"),
        compile_errors=badcase.get("compile_errors", "(无)")[:1500],
        agent_strategy=badcase.get("agent_strategy", "(无)")[:1000],
        agent_steps=badcase.get("agent_steps", 0),
        is_timeout=badcase.get("is_timeout", False),
        error_pattern=badcase.get("error_pattern", "unknown"),
    )

    try:
        resp = client.chat.completions.create(
            model="qwen3.5-plus",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500,
        )
        content = resp.choices[0].message.content.strip()

        # 提取 JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        return json.loads(content)
    except Exception as e:
        return {
            "failure_category": "analysis_error",
            "root_cause": f"分析失败: {str(e)}",
            "agent_mistake": "",
            "skill_suggestion": "",
            "fixable_by_skill": False,
            "confidence": 0.0,
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--badcases", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--api-base", default="https://coding.dashscope.aliyuncs.com/apps/anthropic")
    parser.add_argument("--api-key", default=os.environ.get("ANTHROPIC_AUTH_TOKEN", ""))
    args = parser.parse_args()

    with open(args.badcases) as f:
        data = json.load(f)

    client = OpenAI(base_url=args.api_base, api_key=args.api_key)

    results = []
    for i, bc in enumerate(data["badcases"]):
        print(f"[{i+1}/{len(data['badcases'])}] 分析 {bc['task_name']}...")
        analysis = analyze_single_badcase(client, bc)
        results.append({
            "task_name": bc["task_name"],
            "rule_pattern": bc["error_pattern"],
            "llm_analysis": analysis,
        })
        print(f"  → {analysis.get('failure_category')}: {analysis.get('root_cause', '')[:80]}")

    # 汇总
    category_counts = {}
    skill_suggestions = []
    for r in results:
        cat = r["llm_analysis"].get("failure_category", "unknown")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        if r["llm_analysis"].get("fixable_by_skill"):
            skill_suggestions.append({
                "task": r["task_name"],
                "category": cat,
                "suggestion": r["llm_analysis"].get("skill_suggestion", ""),
            })

    output = {
        "round": data.get("round", 0),
        "total_analyzed": len(results),
        "category_summary": category_counts,
        "fixable_by_skill": len(skill_suggestions),
        "skill_suggestions": skill_suggestions,
        "details": results,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n深层归因完成: {args.output}")
    print(f"类别分布: {json.dumps(category_counts, indent=2, ensure_ascii=False)}")
    print(f"可通过 Skill 修复: {len(skill_suggestions)}/{len(results)}")


if __name__ == "__main__":
    main()
```

### Step A3：基于归因结果生成初版 Skill

```python
#!/usr/bin/env python3
"""
skillrl/scripts/generate_skill.py

基于失败归因结果，用当前模型生成 java-dep-fix SKILL.md 初版。

用法:
  python generate_skill.py \
    --analysis skillrl/analysis/r0-deep-analysis.json \
    --output skillrl/skills/skill-v1-initial.md
"""

import json
import os
import argparse
from openai import OpenAI


GENERATION_PROMPT = """你是一位 AI Agent Skill 设计专家。你需要为一个修复 Java 依赖升级编译失败的 AI Agent 编写一份 Skill 指南（SKILL.md）。

## 背景

AI Agent（Claude Code + qwen3.5-plus）在 100 个 Java Maven 依赖升级修复任务上跑了一轮评测，成功率 75%。
以下是 25 个失败任务的归因分析，按失败类别分组：

## 失败归因分析

### 类别分布
{category_summary}

### 具体改进建议（来自逐 task 分析）
{skill_suggestions}

---

## 你的任务

基于以上失败归因，生成一份 SKILL.md。要求：

1. **YAML frontmatter** 包含 `name: java-dep-fix` 和 `description`（用于触发匹配）
2. **核心理念**：说明修复策略的分层决策（适配新 API vs 降级版本）
3. **工作流程**：5 步工作流（获取代码 → 复现错误 → 可行性评估 → 分析&修复 → 验证）
4. **关键决策规则**：
   - 针对每种失败类别，给出明确的检测信号和处理策略
   - 特别强化"生态级不兼容"的检测（这是最大的失败原因）
   - 给出迭代上限和兜底策略
5. **常见 API 变更模式**：用表格列出变更类型、编译错误表现、修复策略
6. **输出格式**：修复完成后的汇报模板

关键要求：
- Skill 是给 AI Agent 看的操作指南，不是给人看的文档——语言要直接、可执行
- 规则要具体到"看到 X 错误 → 做 Y 操作"，不要空泛的原则
- 针对归因中发现的每一类高频失败，都要有对应的检测规则和处理策略
- 控制在 200-300 行以内，太长会占用 Agent 的上下文窗口

请直接输出完整的 SKILL.md 内容（包含 YAML frontmatter），不要其他解释文字。"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis", required=True, help="深层归因结果 JSON")
    parser.add_argument("--output", required=True, help="输出 SKILL.md 路径")
    parser.add_argument("--api-base", default="https://coding.dashscope.aliyuncs.com/apps/anthropic")
    parser.add_argument("--api-key", default=os.environ.get("ANTHROPIC_AUTH_TOKEN", ""))
    args = parser.parse_args()

    with open(args.analysis) as f:
        analysis = json.load(f)

    # 格式化归因数据
    category_summary = json.dumps(analysis["category_summary"], indent=2, ensure_ascii=False)

    suggestions_text = ""
    for s in analysis.get("skill_suggestions", []):
        suggestions_text += f"\n**[{s['category']}] {s['task']}**:\n{s['suggestion']}\n"

    prompt = GENERATION_PROMPT.format(
        category_summary=category_summary,
        skill_suggestions=suggestions_text[:4000],  # 截断防止超长
    )

    client = OpenAI(base_url=args.api_base, api_key=args.api_key)

    print("正在生成 Skill v1...")
    resp = client.chat.completions.create(
        model="qwen3.5-plus",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=8000,
    )

    skill_content = resp.choices[0].message.content.strip()

    # 清理可能的 markdown 代码块包裹
    if skill_content.startswith("```"):
        lines = skill_content.split("\n")
        skill_content = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(skill_content)

    line_count = len(skill_content.split("\n"))
    print(f"Skill v1 已生成: {args.output} ({line_count} 行)")


if __name__ == "__main__":
    main()
```

---

## Round 1：初版 Skill 评测

### Skill 部署

```bash
#!/bin/bash
# skillrl/scripts/deploy_skill.sh
# 将 SKILL.md 部署到 Agent 运行环境的 skill 目录
#
# 用法: ./deploy_skill.sh <skill_file> <agent_home>
# 示例: ./deploy_skill.sh skillrl/skills/skill-v1-initial.md /root/.claude/skills/java-dep-fix/

SKILL_FILE=$1
AGENT_SKILL_DIR=$2

if [ -z "$SKILL_FILE" ] || [ -z "$AGENT_SKILL_DIR" ]; then
    echo "用法: $0 <skill_file> <agent_skill_dir>"
    exit 1
fi

mkdir -p "$AGENT_SKILL_DIR"
cp "$SKILL_FILE" "$AGENT_SKILL_DIR/SKILL.md"
echo "已部署: $SKILL_FILE → $AGENT_SKILL_DIR/SKILL.md"
```

### 评测配置

```yaml
# skillrl/configs/job-r1-skill-v1.yaml
job_name: skillrl-r1-skill-v1
jobs_dir: /root/harbor-bump-eval/jobs

orchestrator:
  n_concurrent_trials: 3

agents:
  - name: claude-code
    env:
      ANTHROPIC_AUTH_TOKEN: "${ANTHROPIC_AUTH_TOKEN}"
      ANTHROPIC_BASE_URL: "https://coding.dashscope.aliyuncs.com/apps/anthropic"
      ANTHROPIC_MODEL: "qwen3.5-plus"
      ANTHROPIC_SMALL_FAST_MODEL: "qwen3.5-plus"
      # Skill v1 已通过 deploy_skill.sh 部署到 Agent 环境

datasets:
  - path: /root/harbor-bump-eval
    task_names:
      # ... 同 Round 0 完整 100 task 列表
```

### 执行

```bash
# 1. 部署 Skill v1
./skillrl/scripts/deploy_skill.sh \
  skillrl/skills/skill-v1-initial.md \
  /root/.claude/skills/java-dep-fix/

# 2. 运行评测
harbor run skillrl/configs/job-r1-skill-v1.yaml

# 3. 生成报告
python skillrl/scripts/extract_badcases.py \
  --job-dir jobs/skillrl-r1-skill-v1 \
  --output skillrl/reports/report-r1.json
```

---

## Phase B：增量归因（R1 → Skill v2）

### 目的

对比 R0 和 R1 的结果，分析三类任务：
1. **R0 失败 → R1 成功**（Skill v1 解决的）：验证 Skill 的有效性
2. **R0 失败 → R1 仍失败**（残留失败）：Skill v1 未覆盖或策略不够
3. **R0 成功 → R1 失败**（回归）：Skill v1 引入了副作用

### 增量分析脚本

```python
#!/usr/bin/env python3
"""
skillrl/scripts/optimize_skill.py

对比 R0 和 R1 结果，做增量归因，然后用 LLM 生成 Skill v2。

用法:
  python optimize_skill.py \
    --report-r0 skillrl/reports/report-r0.json \
    --report-r1 skillrl/reports/report-r1.json \
    --r1-job-dir jobs/skillrl-r1-skill-v1 \
    --skill-v1 skillrl/skills/skill-v1-initial.md \
    --output-analysis skillrl/analysis/r1-delta-analysis.json \
    --output-skill skillrl/skills/skill-v2-optimized.md
"""

import json
import os
import argparse
from openai import OpenAI


def diff_results(r0_report, r1_report):
    """对比两轮结果，分类为 fixed / still_failed / regressed"""
    r0_map = {r["task_name"]: r["reward"] for r in r0_report["results"]}
    r1_map = {r["task_name"]: r["reward"] for r in r1_report["results"]}

    all_tasks = set(r0_map.keys()) | set(r1_map.keys())

    fixed = []         # R0=0, R1=1
    still_failed = []  # R0=0, R1=0
    regressed = []     # R0=1, R1=0
    stable_pass = []   # R0=1, R1=1

    for task in all_tasks:
        r0 = r0_map.get(task, -1)
        r1 = r1_map.get(task, -1)

        if r0 == 0.0 and r1 == 1.0:
            fixed.append(task)
        elif r0 == 0.0 and r1 == 0.0:
            still_failed.append(task)
        elif r0 == 1.0 and r1 == 0.0:
            regressed.append(task)
        elif r0 == 1.0 and r1 == 1.0:
            stable_pass.append(task)

    return {
        "fixed": fixed,
        "still_failed": still_failed,
        "regressed": regressed,
        "stable_pass": stable_pass,
        "summary": {
            "r0_success": r0_report["success"],
            "r1_success": r1_report["success"],
            "delta": r1_report["success"] - r0_report["success"],
            "fixed_count": len(fixed),
            "regression_count": len(regressed),
            "still_failed_count": len(still_failed),
        }
    }


OPTIMIZE_PROMPT = """你是一位 AI Agent Skill 优化专家。你需要基于评测数据优化一份 Java 依赖升级修复 Skill。

## 当前 Skill (v1)

```markdown
{current_skill}
```

## 评测对比结果

- Round 0（无 Skill）成功率: {r0_rate}%
- Round 1（Skill v1）成功率: {r1_rate}%
- 提升: +{delta}
- 新修复的 task: {fixed_count} 个
- 回归的 task: {regression_count} 个
- 仍失败的 task: {still_failed_count} 个

### 回归分析（R0 通过但 R1 失败的 task）
{regression_details}

### 残留失败分析（R0 和 R1 都失败的 task）
{still_failed_details}

---

## 你的任务

基于以上数据，输出优化后的 SKILL.md v2。要求：

1. **保留有效部分**：R1 新修复了 {fixed_count} 个 task，说明 Skill v1 中对应的规则有效，保留
2. **修复回归**：分析回归原因，调整导致回归的规则（通常是规则过于激进，把本该适配 API 的 task 错误地降级了）
3. **补充残留失败**：针对仍失败的 task，增加新的检测规则和处理策略
4. **规则隔离**：不同失败类别的处理规则应相互独立，修改一类不影响其他类
5. **控制长度**：200-300 行以内

请直接输出完整的 SKILL.md v2 内容（包含 YAML frontmatter）。"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-r0", required=True)
    parser.add_argument("--report-r1", required=True)
    parser.add_argument("--r1-job-dir", required=True)
    parser.add_argument("--skill-v1", required=True)
    parser.add_argument("--output-analysis", required=True)
    parser.add_argument("--output-skill", required=True)
    parser.add_argument("--api-base", default="https://coding.dashscope.aliyuncs.com/apps/anthropic")
    parser.add_argument("--api-key", default=os.environ.get("ANTHROPIC_AUTH_TOKEN", ""))
    args = parser.parse_args()

    # 加载数据
    with open(args.report_r0) as f:
        r0 = json.load(f)
    with open(args.report_r1) as f:
        r1 = json.load(f)
    with open(args.skill_v1) as f:
        skill_v1 = f.read()
    
    # 对比分析
    diff = diff_results(r0, r1)
    print(f"对比结果:")
    print(f"  修复: {diff['summary']['fixed_count']} 个")
    print(f"  回归: {diff['summary']['regression_count']} 个")
    print(f"  仍失败: {diff['summary']['still_failed_count']} 个")
    
    # 保存增量分析
    with open(args.output_analysis, "w", encoding="utf-8") as f:
        json.dump(diff, f, indent=2, ensure_ascii=False)
    
    # 对回归和残留失败的 task 做简要归因
    # （这里简化处理，实际可复用 classify_failures.py 的逻辑）
    regression_details = ""
    for task in diff["regressed"][:10]:
        regression_details += f"- {task}\n"
    if not regression_details:
        regression_details = "(无回归)"
    
    still_failed_details = ""
    for task in diff["still_failed"][:15]:
        still_failed_details += f"- {task}\n"
    
    # 生成 Skill v2
    prompt = OPTIMIZE_PROMPT.format(
        current_skill=skill_v1[:5000],
        r0_rate=round(r0["success_rate"] * 100, 1),
        r1_rate=round(r1["success_rate"] * 100, 1),
        delta=f"{(r1['success_rate'] - r0['success_rate']) * 100:+.1f}%",
        fixed_count=diff["summary"]["fixed_count"],
        regression_count=diff["summary"]["regression_count"],
        still_failed_count=diff["summary"]["still_failed_count"],
        regression_details=regression_details,
        still_failed_details=still_failed_details,
    )
    
    client = OpenAI(base_url=args.api_base, api_key=args.api_key)
    
    print("\n正在生成 Skill v2...")
    resp = client.chat.completions.create(
        model="qwen3.5-plus",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=8000,
    )
    
    skill_v2 = resp.choices[0].message.content.strip()
    if skill_v2.startswith("```"):
        lines = skill_v2.split("\n")
        skill_v2 = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
    
    with open(args.output_skill, "w", encoding="utf-8") as f:
        f.write(skill_v2)
    
    print(f"Skill v2 已生成: {args.output_skill}")


if __name__ == "__main__":
    main()
```

---

## Round 2：优化 Skill 评测

### 执行

```bash
# 1. 部署 Skill v2
./skillrl/scripts/deploy_skill.sh \
  skillrl/skills/skill-v2-optimized.md \
  /root/.claude/skills/java-dep-fix/

# 2. 运行评测
harbor run skillrl/configs/job-r2-skill-v2.yaml

# 3. 生成报告
python skillrl/scripts/extract_badcases.py \
  --job-dir jobs/skillrl-r2-skill-v2 \
  --output skillrl/reports/report-r2.json
```

---

## Final：三轮对比报告

```python
#!/usr/bin/env python3
"""
skillrl/scripts/generate_comparison_report.py

生成三轮评测的对比报告（JSON + Markdown）。

用法:
  python generate_comparison_report.py \
    --r0 skillrl/reports/report-r0.json \
    --r1 skillrl/reports/report-r1.json \
    --r2 skillrl/reports/report-r2.json \
    --output-json skillrl/reports/comparison-report.json \
    --output-md skillrl/reports/comparison-report.md
"""

import json
import argparse
from datetime import datetime


def load_report(path):
    with open(path) as f:
        return json.load(f)


def per_task_diff(r0, r1, r2):
    """逐 task 对比三轮结果"""
    r0_map = {r["task_name"]: r for r in r0["results"]}
    r1_map = {r["task_name"]: r for r in r1["results"]}
    r2_map = {r["task_name"]: r for r in r2["results"]}

    all_tasks = sorted(set(r0_map) | set(r1_map) | set(r2_map))
    rows = []
    for t in all_tasks:
        rows.append({
            "task_name": t,
            "r0": r0_map.get(t, {}).get("reward", -1),
            "r1": r1_map.get(t, {}).get("reward", -1),
            "r2": r2_map.get(t, {}).get("reward", -1),
            "updateType": r0_map.get(t, r1_map.get(t, {})).get("updateType", "?"),
            "dep": r0_map.get(t, r1_map.get(t, {})).get("dep", "?"),
        })
    return rows


def classify_trajectory(row):
    """分类每个 task 的三轮轨迹"""
    r0, r1, r2 = row["r0"], row["r1"], row["r2"]
    if r0 == 0 and r1 == 0 and r2 == 0:
        return "never_fixed"
    if r0 == 0 and r1 == 1 and r2 == 1:
        return "fixed_by_v1"
    if r0 == 0 and r1 == 0 and r2 == 1:
        return "fixed_by_v2"
    if r0 == 0 and r1 == 1 and r2 == 0:
        return "v1_only"
    if r0 == 1 and r1 == 0 and r2 == 0:
        return "regressed_by_v1"
    if r0 == 1 and r1 == 0 and r2 == 1:
        return "v1_regress_v2_fixed"
    if r0 == 1 and r1 == 1 and r2 == 0:
        return "regressed_by_v2"
    if r0 == 1 and r1 == 1 and r2 == 1:
        return "always_pass"
    return "other"


def generate_markdown(r0, r1, r2, rows, traj_summary):
    """生成 Markdown 报告"""
    md = []
    md.append("# SkillRL 三轮评测对比报告\n")
    md.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    md.append(f"**评测集**: {r0['total']} tasks\n")
    md.append(f"**模型**: qwen3.5-plus\n")

    # 总览表
    md.append("\n## 1. 总览\n")
    md.append("| 指标 | Round 0 (无 Skill) | Round 1 (Skill v1) | Round 2 (Skill v2) |")
    md.append("|------|-------------------|-------------------|-------------------|")
    md.append(f"| **成功数** | {r0['success']} | {r1['success']} | {r2['success']} |")
    md.append(f"| **失败数** | {r0['failed']} | {r1['failed']} | {r2['failed']} |")
    md.append(f"| **成功率** | {r0['success_rate']*100:.1f}% | {r1['success_rate']*100:.1f}% | {r2['success_rate']*100:.1f}% |")
    d1 = (r1['success_rate'] - r0['success_rate']) * 100
    d2 = (r2['success_rate'] - r0['success_rate']) * 100
    md.append(f"| **vs 基线** | — | {d1:+.1f}% | {d2:+.1f}% |")

    # 按 updateType 分组
    md.append("\n## 2. 按更新类型分组\n")
    md.append("| 更新类型 | R0 | R1 | R2 |")
    md.append("|---------|----|----|---|")
    for ut in ["minor", "major", "unknown", "other"]:
        r0_ut = r0.get("by_update_type", {}).get(ut, {})
        r1_ut = r1.get("by_update_type", {}).get(ut, {})
        r2_ut = r2.get("by_update_type", {}).get(ut, {})
        r0_s = f"{r0_ut.get('success',0)}/{r0_ut.get('total',0)}"
        r1_s = f"{r1_ut.get('success',0)}/{r1_ut.get('total',0)}"
        r2_s = f"{r2_ut.get('success',0)}/{r2_ut.get('total',0)}"
        md.append(f"| {ut} | {r0_s} | {r1_s} | {r2_s} |")

    # 轨迹分类
    md.append("\n## 3. Task 轨迹分类\n")
    md.append("| 轨迹类型 | 数量 | 说明 |")
    md.append("|---------|------|------|")
    labels = {
        "always_pass": "三轮全过",
        "fixed_by_v1": "v1 修复（持续有效）",
        "fixed_by_v2": "v2 新增修复",
        "v1_only": "v1 修复但 v2 回归",
        "regressed_by_v1": "v1 引入回归",
        "v1_regress_v2_fixed": "v1 回归 v2 修复",
        "regressed_by_v2": "v2 引入回归",
        "never_fixed": "三轮全败",
        "other": "其他",
    }
    for key, label in labels.items():
        count = traj_summary.get(key, 0)
        if count > 0:
            md.append(f"| {label} | {count} | |")

    # 关键洞察
    md.append("\n## 4. 关键洞察\n")
    md.append(f"- Skill v1 新修复 **{traj_summary.get('fixed_by_v1', 0)}** 个 task")
    md.append(f"- Skill v2 额外修复 **{traj_summary.get('fixed_by_v2', 0)}** 个 task")
    md.append(f"- 三轮全败（需要模型能力提升或 Skill 无法覆盖）: **{traj_summary.get('never_fixed', 0)}** 个")
    v1_reg = traj_summary.get('regressed_by_v1', 0) + traj_summary.get('v1_only', 0)
    v2_reg = traj_summary.get('regressed_by_v2', 0)
    if v1_reg > 0:
        md.append(f"- v1 回归: **{v1_reg}** 个 task（Skill 规则过于激进）")
    if v2_reg > 0:
        md.append(f"- v2 回归: **{v2_reg}** 个 task")

    # 逐 task 明细
    md.append("\n## 5. 逐 Task 明细\n")
    md.append("| Task | 依赖 | 类型 | R0 | R1 | R2 | 轨迹 |")
    md.append("|------|------|------|----|----|----|----|")
    for row in sorted(rows, key=lambda x: x["task_name"]):
        traj = classify_trajectory(row)
        r0_icon = "Pass" if row["r0"] == 1 else "Fail"
        r1_icon = "Pass" if row["r1"] == 1 else "Fail"
        r2_icon = "Pass" if row["r2"] == 1 else "Fail"
        md.append(f"| {row['task_name'][:40]} | {row['dep'][:30]} | {row['updateType']} | {r0_icon} | {r1_icon} | {r2_icon} | {traj} |")

    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--r0", required=True)
    parser.add_argument("--r1", required=True)
    parser.add_argument("--r2", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    r0 = load_report(args.r0)
    r1 = load_report(args.r1)
    r2 = load_report(args.r2)

    rows = per_task_diff(r0, r1, r2)

    # 统计轨迹分类
    traj_summary = {}
    for row in rows:
        traj = classify_trajectory(row)
        traj_summary[traj] = traj_summary.get(traj, 0) + 1

    # 生成 JSON
    comparison = {
        "generated_at": datetime.now().isoformat(),
        "rounds": {
            "r0": {"success": r0["success"], "failed": r0["failed"], "rate": r0["success_rate"]},
            "r1": {"success": r1["success"], "failed": r1["failed"], "rate": r1["success_rate"]},
            "r2": {"success": r2["success"], "failed": r2["failed"], "rate": r2["success_rate"]},
        },
        "trajectory_summary": traj_summary,
        "per_task": rows,
    }
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    # 生成 Markdown
    md = generate_markdown(r0, r1, r2, rows, traj_summary)
    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"对比报告已生成:")
    print(f"  JSON: {args.output_json}")
    print(f"  Markdown: {args.output_md}")
    print(f"\n总览:")
    print(f"  R0: {r0['success_rate']*100:.1f}%")
    print(f"  R1: {r1['success_rate']*100:.1f}%  ({(r1['success_rate']-r0['success_rate'])*100:+.1f}%)")
    print(f"  R2: {r2['success_rate']*100:.1f}%  ({(r2['success_rate']-r0['success_rate'])*100:+.1f}%)")
    print(f"\n轨迹分类: {json.dumps(traj_summary, indent=2)}")


if __name__ == "__main__":
    main()
```

---

## 完整执行手册（逐步 Checklist）

### 前置条件

- [ ] 评测服务器可用（harbor 已部署）
- [ ] API 配额充足（100 task × 3 轮 = 300 次 Agent 运行）
- [ ] Python 环境有 `openai`, `httpx` 包

### Round 0: 基线（预计 6-8h）

```bash
# 如果 report-100tasks.json 就是无 Skill 的基线，直接复用：
cp report-100tasks.json skillrl/reports/report-r0.json

# 否则运行：
harbor run skillrl/configs/job-r0-noskill.yaml
python skillrl/scripts/extract_badcases.py \
  --job-dir jobs/skillrl-r0-noskill \
  --output skillrl/reports/report-r0.json
```

- [ ] 确认 report-r0.json 生成，记录基线成功率

### Phase A: 失败归因（预计 1-2h）

```bash
# Step A1: 规则分类
python skillrl/scripts/extract_badcases.py \
  --report skillrl/reports/report-r0.json \
  --job-dir jobs/skillrl-r0-noskill \
  --output skillrl/analysis/r0-badcases.json

# Step A2: LLM 深层归因
python skillrl/scripts/classify_failures.py \
  --badcases skillrl/analysis/r0-badcases.json \
  --output skillrl/analysis/r0-deep-analysis.json

# Step A3: 生成 Skill v1
python skillrl/scripts/generate_skill.py \
  --analysis skillrl/analysis/r0-deep-analysis.json \
  --output skillrl/skills/skill-v1-initial.md
```

- [ ] 确认 r0-badcases.json 中失败模式分布合理（≤ 5 类覆盖 ≥ 80%）
- [ ] 确认 r0-deep-analysis.json 中 `fixable_by_skill` 数量 ≥ 10
- [ ] **人工 Review** skill-v1-initial.md：检查规则是否合理，必要时手动调整
- [ ] 记录 Skill v1 的行数、关键规则数量

### Round 1: 初版 Skill 评测（预计 6-8h）

```bash
# 部署 + 评测
./skillrl/scripts/deploy_skill.sh \
  skillrl/skills/skill-v1-initial.md \
  /root/.claude/skills/java-dep-fix/
harbor run skillrl/configs/job-r1-skill-v1.yaml
python skillrl/scripts/extract_badcases.py \
  --job-dir jobs/skillrl-r1-skill-v1 \
  --output skillrl/reports/report-r1.json
```

- [ ] 确认成功率提升（预期 75% → 80%+）
- [ ] 确认回归数 ≤ 3

### Phase B: 增量归因 + Skill v2（预计 1-2h）

```bash
python skillrl/scripts/optimize_skill.py \
  --report-r0 skillrl/reports/report-r0.json \
  --report-r1 skillrl/reports/report-r1.json \
  --r1-job-dir jobs/skillrl-r1-skill-v1 \
  --skill-v1 skillrl/skills/skill-v1-initial.md \
  --output-analysis skillrl/analysis/r1-delta-analysis.json \
  --output-skill skillrl/skills/skill-v2-optimized.md
```

- [ ] 确认增量分析中 fixed / regressed / still_failed 分布合理
- [ ] **人工 Review** skill-v2-optimized.md：重点检查回归修复 + 新增规则
- [ ] 记录 Skill v2 vs v1 的 diff

### Round 2: 优化 Skill 评测（预计 6-8h）

```bash
./skillrl/scripts/deploy_skill.sh \
  skillrl/skills/skill-v2-optimized.md \
  /root/.claude/skills/java-dep-fix/
harbor run skillrl/configs/job-r2-skill-v2.yaml
python skillrl/scripts/extract_badcases.py \
  --job-dir jobs/skillrl-r2-skill-v2 \
  --output skillrl/reports/report-r2.json
```

- [ ] 确认成功率再次提升（预期 80%+ → 85%+）
- [ ] 确认 R1 回归已修复

### Final: 对比报告

```bash
python skillrl/scripts/generate_comparison_report.py \
  --r0 skillrl/reports/report-r0.json \
  --r1 skillrl/reports/report-r1.json \
  --r2 skillrl/reports/report-r2.json \
  --output-json skillrl/reports/comparison-report.json \
  --output-md skillrl/reports/comparison-report.md
```

- [ ] Review comparison-report.md
- [ ] 将最佳 Skill 版本正式部署

---

## 时间线和成本估算

| 阶段 | 耗时 | API 成本 | 人工介入 |
|------|------|---------|---------|
| Round 0 评测 | 6-8h（可复用已有数据） | ~$15-25 | 无 |
| Phase A 归因 | 1-2h | ~$0.5（25 次 LLM 调用）| Review Skill v1：30min |
| Round 1 评测 | 6-8h | ~$15-25 | 无 |
| Phase B 优化 | 1-2h | ~$0.5 | Review Skill v2：30min |
| Round 2 评测 | 6-8h | ~$15-25 | 无 |
| 对比报告 | 5min | 0 | Review：30min |
| **总计** | **~3 天** | **~$50-75** | **~2h** |

---

## 预期结果

| Round | Skill | 预期成功率 | 预期提升 |
|-------|-------|-----------|---------|
| R0 | 无 | 75% | — |
| R1 | v1（初版，覆盖高频失败模式） | 80-83% | +5-8% |
| R2 | v2（修复回归 + 补充残留） | 84-88% | +9-13% |

### 成功判定标准

- **最低成功**：R2 成功率 ≥ 82%（vs R0 提升 ≥ 7%）
- **预期成功**：R2 成功率 ≥ 85%（vs R0 提升 ≥ 10%）
- **超预期**：R2 成功率 ≥ 88%（vs R0 提升 ≥ 13%）
- **失败判定**：R2 成功率 < 80% 或回归 > 5 个 → 需分析原因，可能是模型能力瓶颈

### 如果效果不达预期

1. **R1 提升 < 3%**：归因分类可能不准确 → 人工复查 5 个失败 task 的 trajectory
2. **R1 回归 > 5**：Skill 规则过于激进 → 收紧"降级"触发条件
3. **R2 vs R1 无提升**：Skill prompt 优化达到天花板 → 考虑切换更强模型（如 Claude Sonnet）
4. **三轮全败的 task > 15**：这些 task 超出 Skill-level 优化能力 → 记录为"需要模型能力升级"
