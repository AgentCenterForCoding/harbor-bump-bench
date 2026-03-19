#!/usr/bin/env python3
"""
将 Harbor ATIF-v1.2 trajectory.json 导入 Langfuse。

用法：
  python import_trajectory_to_langfuse.py trajectory.json
  python import_trajectory_to_langfuse.py trajectory.json --task-name task-quickfixj-mina
  python import_trajectory_to_langfuse.py trajectory.json --dry-run

依赖：
  pip install langfuse
"""

import argparse
import base64
import json
import os
import sys
import uuid
from datetime import datetime, timezone

import httpx

# ---------------------------------------------------------------------------
# 配置（也可通过环境变量覆盖）
# ---------------------------------------------------------------------------
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY", "pk-lf-1bd10922-1615-49c7-80e1-5e310d58a6c5")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY", "sk-lf-8a2cddc7-a669-4735-9322-0ae483fd87ff")
LANGFUSE_HOST       = os.environ.get("LANGFUSE_BASE_URL",   "http://101.46.209.29:3000")


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
def _ts(iso: str | None):
    """将 ISO8601 字符串转为 datetime，缺失时返回 None。"""
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except Exception:
        return None


def _usage(metrics: dict | None):
    """ATIF metrics → Langfuse usage dict。"""
    if not metrics:
        return None
    return {
        "input":  metrics.get("prompt_tokens", 0),
        "output": metrics.get("completion_tokens", 0),
        "total":  (metrics.get("prompt_tokens", 0)
                   + metrics.get("completion_tokens", 0)),
    }


# ---------------------------------------------------------------------------
# 主导入逻辑
# ---------------------------------------------------------------------------
def import_trajectory(path: str, task_name: str | None, dry_run: bool) -> None:
    with open(path, encoding="utf-8") as f:
        traj = json.load(f)

    schema  = traj.get("schema_version", "unknown")
    session = traj.get("session_id", "unknown")
    agent   = traj.get("agent", {})
    steps   = traj.get("steps", [])
    metrics = traj.get("final_metrics", {})
    reward  = traj.get("reward")

    trace_name = f"harbor-trajectory/{task_name or session}"

    print(f"trajectory : {path}")
    print(f"schema     : {schema}")
    print(f"session_id : {session}")
    print(f"agent      : {agent.get('name')} v{agent.get('version')}  model={agent.get('model_name')}")
    print(f"steps      : {len(steps)}")
    print(f"metrics    : {metrics}")
    if reward is not None:
        print(f"reward     : {reward}")
    print()

    if dry_run:
        print("[dry-run] 不写入 Langfuse，仅打印前 3 步：")
        for s in steps[:3]:
            print(f"  step {s['step_id']:>3}  source={s.get('source'):<6}  "
                  f"tokens={s.get('metrics', {}).get('prompt_tokens', 0)}p "
                  f"msg={str(s.get('message',''))[:60]!r}")
        return

    auth = "Basic " + base64.b64encode(
        f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()).decode()
    headers = {"Authorization": auth, "Content-Type": "application/json"}

    # 找首尾时间戳
    timestamps = [_ts(s.get("timestamp")) for s in steps]
    timestamps = [t for t in timestamps if t]
    start_time = min(timestamps) if timestamps else datetime.now(timezone.utc)
    end_time   = max(timestamps) if timestamps else datetime.now(timezone.utc)

    trace_id = str(uuid.uuid4())

    # 构建 batch ingestion payload（Langfuse v3 统一写入接口）
    batch = []

    # trace 事件
    batch.append({
        "id": str(uuid.uuid4()),
        "type": "trace-create",
        "timestamp": start_time.isoformat(),
        "body": {
            "id": trace_id,
            "name": trace_name,
            "sessionId": session,
            "input": {"task": task_name or session},
            "output": {"reward": reward, "final_metrics": metrics},
            "metadata": {"schema_version": schema, "agent": agent, "task_name": task_name},
            "timestamp": start_time.isoformat(),
            "tags": ["harbor", "atif", agent.get("name", ""), task_name or ""],
        },
    })

    # 构建观测事件（带父子层级）
    #
    # 无 tool_calls 的 agent step：
    #   └── GENERATION: step-N  (直接挂 trace)
    #
    # 有 tool_calls 的 agent step：
    #   └── SPAN: turn-N         (父，覆盖整个 step)
    #         ├── GENERATION: llm-N   (LLM 推理，含 tokens)
    #         └── SPAN: tool-N-<fn>   (每个工具调用，含入参和结果)
    #
    gen_count = 0
    tool_span_count = 0

    for step in steps:
        if step.get("source") != "agent":
            continue

        ts         = _ts(step.get("timestamp"))
        ts_iso     = ts.isoformat() if ts else start_time.isoformat()
        tool_calls = step.get("tool_calls", [])
        obs_val    = step.get("observation")          # {"results": [{source_call_id, content}]}
        m          = step.get("metrics") or {}
        model_name = step.get("model_name") or agent.get("model_name")
        step_label = f"step-{step['step_id']:04d}"

        # 把 observation results 按 source_call_id 建索引
        result_map: dict[str, str] = {}
        if obs_val and isinstance(obs_val, dict):
            for r in obs_val.get("results", []):
                result_map[r.get("source_call_id", "")] = r.get("content", "")

        if not tool_calls:
            # ── 简单回复：直接挂 trace 的 GENERATION ──────────────────────────
            batch.append({
                "id": str(uuid.uuid4()),
                "type": "observation-create",
                "timestamp": ts_iso,
                "body": {
                    "id": str(uuid.uuid4()),
                    "traceId": trace_id,
                    "type": "GENERATION",
                    "name": step_label,
                    "model": model_name,
                    "input": step.get("message", ""),
                    "output": step.get("message", "") or None,
                    "usage": {
                        "input":  m.get("prompt_tokens", 0),
                        "output": m.get("completion_tokens", 0),
                        "total":  m.get("prompt_tokens", 0) + m.get("completion_tokens", 0),
                    },
                    "startTime": ts_iso,
                    "endTime":   ts_iso,
                    "metadata": {"reasoning": step.get("reasoning_content")},
                },
            })
            gen_count += 1
        else:
            # ── 含工具调用：SPAN(turn) > GENERATION(llm) + SPAN(tool)×N ──────
            turn_id = str(uuid.uuid4())
            llm_id  = str(uuid.uuid4())

            # 父 SPAN: turn-N
            batch.append({
                "id": str(uuid.uuid4()),
                "type": "observation-create",
                "timestamp": ts_iso,
                "body": {
                    "id": turn_id,
                    "traceId": trace_id,
                    "type": "SPAN",
                    "name": f"turn-{step['step_id']:04d}",
                    "startTime": ts_iso,
                    "endTime":   ts_iso,
                    "metadata": {"step_id": step["step_id"]},
                },
            })

            # 子 GENERATION: llm-N
            batch.append({
                "id": str(uuid.uuid4()),
                "type": "observation-create",
                "timestamp": ts_iso,
                "body": {
                    "id": llm_id,
                    "traceId": trace_id,
                    "parentObservationId": turn_id,
                    "type": "GENERATION",
                    "name": f"llm-{step['step_id']:04d}",
                    "model": model_name,
                    "input": step.get("message", ""),
                    "output": json.dumps([{
                        "function": tc["function_name"],
                        "arguments": tc.get("arguments", {}),
                    } for tc in tool_calls]),
                    "usage": {
                        "input":  m.get("prompt_tokens", 0),
                        "output": m.get("completion_tokens", 0),
                        "total":  m.get("prompt_tokens", 0) + m.get("completion_tokens", 0),
                    },
                    "startTime": ts_iso,
                    "endTime":   ts_iso,
                    "metadata": {"reasoning": step.get("reasoning_content")},
                },
            })
            gen_count += 1

            # 子 SPAN: tool-N-<fn> × 每个工具调用
            for tc in tool_calls:
                fn_name = tc.get("function_name", "unknown")
                call_id = tc.get("tool_call_id", "")
                result  = result_map.get(call_id, "")
                batch.append({
                    "id": str(uuid.uuid4()),
                    "type": "observation-create",
                    "timestamp": ts_iso,
                    "body": {
                        "id": str(uuid.uuid4()),
                        "traceId": trace_id,
                        "parentObservationId": turn_id,
                        "type": "SPAN",
                        "name": f"tool-{step['step_id']:04d}-{fn_name}",
                        "input": tc.get("arguments", {}),
                        "output": result or None,
                        "startTime": ts_iso,
                        "endTime":   ts_iso,
                        "metadata": {"tool_call_id": call_id},
                    },
                })
                tool_span_count += 1

    # 分批发送（每批最多 100 条）
    CHUNK = 100
    errors = 0
    with httpx.Client(timeout=30) as c:
        for i in range(0, len(batch), CHUNK):
            chunk = batch[i:i + CHUNK]
            r = c.post(f"{LANGFUSE_HOST}/api/public/ingestion",
                       headers=headers, json={"batch": chunk})
            if r.status_code not in (200, 201, 207):
                print(f"  批次 {i//CHUNK} 写入失败: {r.status_code} {r.text[:200]}", file=sys.stderr)
                errors += 1

    status = "完成" if not errors else f"部分失败({errors}批)"
    print(f"导入{status}：trace_id={trace_id}  generations={gen_count}  tool_spans={tool_span_count}")
    print(f"查看：{LANGFUSE_HOST}/trace/{trace_id}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="导入 Harbor trajectory.json 到 Langfuse")
    parser.add_argument("trajectory", help="trajectory.json 文件路径")
    parser.add_argument("--task-name", default=None, help="任务名称（用于 trace 命名）")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不写入 Langfuse")
    args = parser.parse_args()

    import_trajectory(args.trajectory, args.task_name, args.dry_run)


if __name__ == "__main__":
    main()
