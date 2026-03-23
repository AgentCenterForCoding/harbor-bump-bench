#!/usr/bin/env python3
"""
将 retry job 的结果合并回原始 job 的结果（best-of-k 取最好结果）。
用法: python3 merge_retry_results.py <base_result.json> <retry_result.json> <output_result.json>
"""
import json
import sys
import copy


def get_task_prefix(task_id):
    return task_id.rsplit('__', 1)[0]


def merge_results(base_path, retry_path, output_path):
    with open(base_path) as f:
        base = json.load(f)
    with open(retry_path) as f:
        retry = json.load(f)

    base_evals = base['stats']['evals']['claude-code__harbor-bump-eval']
    retry_evals = retry['stats']['evals']['claude-code__harbor-bump-eval']

    # 构建 retry 结果映射: prefix -> (reward, new_task_id)
    retry_results = {}
    for task_id in retry_evals['reward_stats']['reward'].get('1.0', []):
        prefix = get_task_prefix(task_id)
        # 取 best (reward=1.0 优先)
        if prefix not in retry_results or retry_results[prefix][0] < 1.0:
            retry_results[prefix] = (1.0, task_id)
    for task_id in retry_evals['reward_stats']['reward'].get('0.0', []):
        prefix = get_task_prefix(task_id)
        if prefix not in retry_results:
            retry_results[prefix] = (0.0, task_id)

    merged_success = list(base_evals['reward_stats']['reward'].get('1.0', []))
    merged_fail = []
    replaced = []
    kept_fail = []

    for task_id in base_evals['reward_stats']['reward'].get('0.0', []):
        prefix = get_task_prefix(task_id)
        if prefix in retry_results:
            reward, new_task_id = retry_results[prefix]
            if reward == 1.0:
                merged_success.append(new_task_id)
                replaced.append((task_id, new_task_id))
            else:
                merged_fail.append(task_id)
                kept_fail.append(task_id)
        else:
            merged_fail.append(task_id)
            kept_fail.append(task_id)

    total = base['n_total_trials']
    merged_mean = len(merged_success) / total

    print(f"原始: 成功={len(base_evals['reward_stats']['reward'].get('1.0', []))}, "
          f"失败={len(base_evals['reward_stats']['reward'].get('0.0', []))}, "
          f"总={total}")
    print(f"retry 覆盖: {len(retry_results)} 个前缀")
    print(f"成功替换: {len(replaced)} 个")
    for old, new in replaced:
        print(f"  {old} -> {new}")
    print(f"仍失败: {len(kept_fail)} 个")
    print(f"合并后: 成功={len(merged_success)}, 失败={len(merged_fail)}, 总={total}")
    print(f"Mean reward: {merged_mean:.4f} ({merged_mean*100:.2f}%)")

    merged = copy.deepcopy(base)
    merged['_merged_from'] = f'{base_path} + {retry_path}'
    merged['stats']['evals']['claude-code__harbor-bump-eval']['n_trials'] = len(merged_success) + len(merged_fail)
    merged['stats']['evals']['claude-code__harbor-bump-eval']['metrics'] = [{'mean': merged_mean}]
    merged['stats']['evals']['claude-code__harbor-bump-eval']['reward_stats']['reward']['1.0'] = merged_success
    merged['stats']['evals']['claude-code__harbor-bump-eval']['reward_stats']['reward']['0.0'] = merged_fail

    with open(output_path, 'w') as f:
        json.dump(merged, f, indent=4)
    print(f"\n已写入: {output_path}")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("用法: python3 merge_retry_results.py <base_result.json> <retry_result.json> <output_result.json>")
        sys.exit(1)
    merge_results(sys.argv[1], sys.argv[2], sys.argv[3])
