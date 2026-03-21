#!/usr/bin/env python3
"""
skillrl/scripts/classify_failures.py

用当前模型（qwen3.5-plus）深度分析每个失败 task 的 trajectory，
提炼出 Skill 改进建议。

用法:
  python classify_failures.py \
    --badcases skillrl/analysis/r0-badcases.json \
    --output skillrl/analysis/r0-deep-analysis.json
"""

import json
import os
import argparse
from openai import OpenAI


ANALYSIS_PROMPT = """你是一位 Java 编译错误修复专家。下面是一个 AI Agent 尝试修复 Java 依赖升级编译失败的记录，该 Agent 修复**失败**了。

## 任务信息
- 项目: {project}
- 升级依赖: {dep}
- 版本变更: {prev_version} → {new_version}
- 升级类型: {update_type}
- Java 版本: {java_version}

## Agent 最终总结（失败时的输出）
```
{result_summary}
```

## 最后一次编译错误（节选）
```
{compile_errors}
```

## 其他信息
- Agent 轮数: {num_turns}
- 是否超时: {is_timeout}
- 规则分类: {error_pattern}
- 是否调用了 Skill: {used_skill}

---

请分析失败原因，输出以下 JSON（只输出 JSON，不要其他内容）：

```json
{{
  "failure_category": "从以下选一：namespace_migration | transitive_dependency | api_signature_change | ecosystem_incompatibility | agent_strategy_error | timeout_complexity | model_capability_limit | other",
  "root_cause": "一句话说明核心原因",
  "agent_mistake": "Agent 在修复过程中犯了什么错误？如果 Agent 的操作是正确的但问题太难，写'问题超出当前能力'",
  "skill_suggestion": "如果为 Agent 提供一个 Skill 指导，应该包含什么操作/知识才能避免此次失败？具体到执行步骤",
  "fixable_by_skill": true或false,
  "confidence": 0.0到1.0之间的浮点数
}}
```"""


def analyze_single_badcase(client, badcase: dict, model: str = "qwen3.5-plus") -> dict:
    meta = badcase.get("metadata", {})
    prompt = ANALYSIS_PROMPT.format(
        project=meta.get("project", "unknown"),
        dep=meta.get("dep", "unknown"),
        prev_version=meta.get("prevVersion", "?"),
        new_version=meta.get("newVersion", "?"),
        update_type=meta.get("updateType", "unknown"),
        java_version=meta.get("javaVersion", "?"),
        result_summary=badcase.get("result_summary", "(空)")[:1200],
        compile_errors=badcase.get("compile_errors", "(空)")[:1200],
        num_turns=badcase.get("num_turns", 0),
        is_timeout=badcase.get("is_timeout", False),
        error_pattern=badcase.get("error_pattern", "unknown"),
        used_skill=badcase.get("used_skill", False),
    )

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=600,
        )
        content = resp.choices[0].message.content.strip()
        # 提取 JSON 块
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
    parser.add_argument("--model", default="qwen3.5-plus")
    parser.add_argument("--api-base", default=os.environ.get(
        "ANTHROPIC_BASE_URL", "https://coding.dashscope.aliyuncs.com/apps/anthropic"))
    parser.add_argument("--api-key", default=os.environ.get("ANTHROPIC_AUTH_TOKEN", ""))
    args = parser.parse_args()

    with open(args.badcases, encoding="utf-8") as f:
        data = json.load(f)

    client = OpenAI(base_url=args.api_base, api_key=args.api_key)

    results = []
    for i, bc in enumerate(data["badcases"]):
        print(f"[{i+1}/{len(data['badcases'])}] 分析 {bc['task_name']}...")
        analysis = analyze_single_badcase(client, bc, args.model)
        results.append({
            "task_name": bc["task_name"],
            "rule_pattern": bc["error_pattern"],
            "llm_analysis": analysis,
        })
        cat = analysis.get("failure_category", "?")
        fixable = analysis.get("fixable_by_skill", False)
        print(f"  → {cat}  fixable={fixable}  {analysis.get('root_cause', '')[:60]}")

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
        "fixable_by_skill_count": len(skill_suggestions),
        "skill_suggestions": skill_suggestions,
        "details": results,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n分析结果: {args.output}")
    print(f"类别分布: {json.dumps(category_counts, indent=2, ensure_ascii=False)}")
    print(f"可通过 Skill 修复: {len(skill_suggestions)}/{len(results)}")


if __name__ == "__main__":
    main()
