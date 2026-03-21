# SkillRL 三轮迭代实施方案

**版本**: v2.0
**更新**: 2026-03-21
**目标**: 通过 3 轮"运行评测 → 分析失败 → 优化 Skill"循环，不断提升 Skill 对 Agent 修复编译失败的引导效果。

---

## 总体流程

```
Round 0: 无 Skill 基线评测
  ↓  确保服务器 ~/.claude/skills/ 目录不存在或为空（无 java-dep-fix skill）
  ↓  harbor run job-100tasks-nopre.yaml（job: bump-dep-fix-100-nopre）
  ↓  report-r0.json
  ↓
Phase A: Bad Case 分析（R0 → Skill v1）
  ↓  extract_badcases.py  →  r0-badcases.json
  ↓  classify_failures.py →  r0-deep-analysis.json
  ↓  generate_skill.py    →  skill-v1-initial.md
  ↓  【人工 Review】
  ↓
Round 1: 带 Skill v1 评测
  ↓  deploy_skill.sh skill-v1-initial.md
  ↓  harbor run job-100tasks-skill-v1.yaml（job: bump-dep-fix-100-skill-v1）
  ↓  report-r1.json
  ↓
Phase B: Delta 分析（R0 vs R1 → Skill v2）
  ↓  optimize_skill.py    →  r1-delta-analysis.json + skill-v2-optimized.md
  ↓  【人工 Review】
  ↓
Round 2: 带 Skill v2 评测
  ↓  deploy_skill.sh skill-v2-optimized.md
  ↓  harbor run job-100tasks-skill-v2.yaml（job: bump-dep-fix-100-skill-v2）
  ↓  report-r2.json
  ↓
Final: 三轮对比报告
  ↓  generate_comparison_report.py
  ↓  comparison-report.md + comparison-report.json
  ↓
Done
```

---

## 目录结构

```
harbor-bump-eval/
├── skillrl/
│   ├── scripts/
│   │   ├── extract_badcases.py           # Phase A/B: 从 report 提取失败 task 详情
│   │   ├── classify_failures.py          # Phase A/B: 用 LLM 分析失败原因
│   │   ├── generate_skill.py             # Phase A: 基于分析生成初版 Skill
│   │   ├── optimize_skill.py             # Phase B: 基于 delta 优化 Skill
│   │   ├── generate_comparison_report.py # Final: 三轮对比报告
│   │   └── deploy_skill.sh               # 部署: 将 SKILL.md 推送到 Agent 主目录
│   ├── configs/
│   │   └── job-r1-skill-v1.yaml          # R1 备用配置（主配置在根目录）
│   ├── skills/
│   │   ├── skill-v1-initial.md           # R1 生成的初版 Skill（人工 Review 后使用）
│   │   └── skill-v2-optimized.md         # R2 优化后的 Skill（人工 Review 后使用）
│   ├── analysis/
│   │   ├── r0-badcases.json              # Round 0 失败概况
│   │   ├── r0-deep-analysis.json         # Round 0 LLM 深度分析
│   │   └── r1-delta-analysis.json        # Round 1→2 变化分析
│   └── reports/
│       ├── report-r0.json                # Round 0 评测报告（无 Skill 基线）
│       ├── report-r1.json                # Round 1 评测报告
│       ├── report-r2.json                # Round 2 评测报告
│       ├── comparison-report.json        # 三轮对比（机器格式）
│       └── comparison-report.md          # 三轮对比（可读报告）
├── jobs/                                 # 已有: 各轮评测输出目录
│   ├── bump-dep-fix-100-nopre/           # Round 0 结果
│   ├── bump-dep-fix-100-skill-v1/        # Round 1 结果
│   └── bump-dep-fix-100-skill-v2/        # Round 2 结果
├── job-100tasks-nopre.yaml               # Round 0 配置
├── job-100tasks-skill.yaml               # 同 job-r1（job_name: bump-dep-fix-100-skill）
├── job-100tasks-skill-v2.yaml            # Round 2 配置（job_name: bump-dep-fix-100-skill-v2）
└── task-*/                               # 110 个任务目录
```

---

## 为什么这样能工作

```
评测服务器 ~/.claude/skills/java-dep-fix/SKILL.md
        ↓ install.sh 自动执行:
        ↓ cp -r ~/.claude/skills $CLAUDE_CONFIG_DIR/skills
容器内 $CLAUDE_CONFIG_DIR/skills/java-dep-fix/SKILL.md
        ↓ Claude Code 启动时自动加载
claude --print -- '任务指令'
  → skills 列表中有 java-dep-fix
  → 任务是 "Fix Maven Compilation Failure"（命中触发词）
  → 自动调用 Skill 工具，按 Skill 指导流程修复
```

**三个 job 对比**：

| 项目 | job-100tasks-nopre | job-100tasks-skill (-v1) | job-100tasks-skill-v2 |
|------|---------------------|--------------------------|------------------------|
| job_name | bump-dep-fix-100-nopre | bump-dep-fix-100-skill | bump-dep-fix-100-skill-v2 |
| Skill | 无 | java-dep-fix v1 | java-dep-fix v2 |
| 测试集 | 相同 110 个任务 | 相同 110 个任务 | 相同 110 个任务 |
| 状态 | 待运行 | 待运行 | 待运行 |

---

## Round 0：无 Skill 基线评测

> **目标**：获取 Agent 在**没有任何 java-dep-fix Skill** 情况下的真实基线成功率。
> 需要重新运行评测，确保服务器上没有部署 Skill。

```bash
# 在评测服务器上执行（harbor-bump-eval 根目录）

# 1. 确认服务器上没有部署 java-dep-fix skill（有则先删除）
rm -rf ~/.claude/skills/java-dep-fix

# 2. 运行基线评测
harbor run job-100tasks-nopre.yaml

# 3. 生成 R0 报告
mkdir -p skillrl/reports
python skillrl/scripts/extract_badcases.py \
  --report jobs/bump-dep-fix-100-nopre/result.json \
  --jobs-dir jobs/bump-dep-fix-100-nopre \
  --round 0 \
  --output skillrl/reports/report-r0.json
```

---

## Phase A：Bad Case 分析（R0 → Skill v1）

### Step A1：提取失败 task 详情

```bash
python skillrl/scripts/extract_badcases.py \
  --report skillrl/reports/report-r0.json \
  --jobs-dir jobs/bump-dep-fix-100-nopre \
  --round 0 \
  --output skillrl/analysis/r0-badcases.json
```

输出示例：
```json
{
  "round": 0,
  "total_failed": 25,
  "pattern_summary": {
    "symbol_not_found": 10,
    "method_signature_change": 6,
    "transitive_dependency_missing": 5,
    "namespace_migration_javax_jakarta": 2,
    "other": 2
  },
  "badcases": [...]
}
```

### Step A2：LLM 深度分析

```bash
python skillrl/scripts/classify_failures.py \
  --badcases skillrl/analysis/r0-badcases.json \
  --output skillrl/analysis/r0-deep-analysis.json
```

### Step A3：生成初版 Skill v1

```bash
python skillrl/scripts/generate_skill.py \
  --analysis skillrl/analysis/r0-deep-analysis.json \
  --output skillrl/skills/skill-v1-initial.md
```

> **⚠️ 人工 Review 检查点**（约 30min）：
> - 确认 5 步流程是否清晰、可执行
> - 确认高频失败模式均有对应操作指导
> - 确认长度在 200-300 行（太长占满上下文窗口）
> - 必要时手动补充或精简

---

## Round 1：带 Skill v1 评测

### 部署 Skill（在评测服务器上执行）

```bash
# 方式一：使用脚本
bash skillrl/scripts/deploy_skill.sh skillrl/skills/skill-v1-initial.md

# 方式二：手动（与用户提供的步骤完全一致）
mkdir -p ~/.claude/skills/java-dep-fix
cp skillrl/skills/skill-v1-initial.md ~/.claude/skills/java-dep-fix/SKILL.md

# 验证
head -5 ~/.claude/skills/java-dep-fix/SKILL.md
```

### 运行评测

```bash
# 使用根目录的 job yaml（与 job-100tasks-skill.yaml 等价，job_name 不同）
harbor run job-100tasks-skill.yaml
# 或使用 skillrl/configs 下的备用配置（job_name: bump-dep-fix-100-skill-v1）
harbor run skillrl/configs/job-r1-skill-v1.yaml
```

### 生成报告

```bash
python skillrl/scripts/extract_badcases.py \
  --report jobs/bump-dep-fix-100-skill-v1/result.json \
  --jobs-dir jobs/bump-dep-fix-100-skill-v1 \
  --round 1 \
  --output skillrl/reports/report-r1.json
```

### 预期结果

| 指标 | 预期值 |
|------|-------|
| 成功率 | 80–83% |
| vs R0 | +5%~+8% |
| 退步数 | ≤ 3 个 |

---

## Phase B：Delta 分析（R0 vs R1 → Skill v2）

```bash
python skillrl/scripts/optimize_skill.py \
  --report-r0 skillrl/reports/report-r0.json \
  --report-r1 skillrl/reports/report-r1.json \
  --jobs-dir-r1 jobs/bump-dep-fix-100-skill-v1 \
  --skill-v1 skillrl/skills/skill-v1-initial.md \
  --output-analysis skillrl/analysis/r1-delta-analysis.json \
  --output-skill skillrl/skills/skill-v2-optimized.md
```

分析结果示例：
```json
{
  "summary": {
    "r0_success": 75, "r1_success": 82,
    "fixed_count": 9, "regression_count": 2, "still_failed_count": 16
  },
  "fixed": ["task-xxx", ...],
  "regressed": ["task-yyy", ...],
  "still_failed": ["task-zzz", ...]
}
```

> **⚠️ 人工 Review 检查点**（约 30min）：
> - 重点检查退步原因（Skill 是否过于激进？）
> - 确认 v2 针对仍然失败的模式有新的操作指导
> - 对比 v1 和 v2 的 diff，确认改动方向正确

---

## Round 2：带 Skill v2 评测

### 部署 Skill v2

```bash
bash skillrl/scripts/deploy_skill.sh skillrl/skills/skill-v2-optimized.md
# 等价于:
cp skillrl/skills/skill-v2-optimized.md ~/.claude/skills/java-dep-fix/SKILL.md
```

### 运行评测

```bash
harbor run job-100tasks-skill-v2.yaml
```

### 生成报告

```bash
python skillrl/scripts/extract_badcases.py \
  --report jobs/bump-dep-fix-100-skill-v2/result.json \
  --jobs-dir jobs/bump-dep-fix-100-skill-v2 \
  --round 2 \
  --output skillrl/reports/report-r2.json
```

### 预期结果

| 指标 | 预期值 |
|------|-------|
| 成功率 | 84–88% |
| vs R0 | +9%~+13% |
| R1 退步已修复 | 是 |

---

## Final：三轮对比报告

```bash
python skillrl/scripts/generate_comparison_report.py \
  --r0 skillrl/reports/report-r0.json \
  --r1 skillrl/reports/report-r1.json \
  --r2 skillrl/reports/report-r2.json \
  --output-json skillrl/reports/comparison-report.json \
  --output-md skillrl/reports/comparison-report.md
```

---

## 操作 Checklist

### 前置准备

- [ ] 评测服务器上 harbor 已安装，Python 环境有 `openai` 包
- [ ] API Token 可用（`echo $ANTHROPIC_AUTH_TOKEN` 有输出）
- [ ] 克隆/同步本仓库到评测服务器 `/root/harbor-bump-eval/`

### Round 0（约 6-8h）

- [ ] 确认 `~/.claude/skills/java-dep-fix` 不存在（`rm -rf ~/.claude/skills/java-dep-fix`）
- [ ] `harbor run job-100tasks-nopre.yaml`
- [ ] 生成 `skillrl/reports/report-r0.json`
- [ ] 记录基线成功率

### Phase A（约 1-2h）

- [ ] `python skillrl/scripts/extract_badcases.py ...` → r0-badcases.json
- [ ] `python skillrl/scripts/classify_failures.py ...` → r0-deep-analysis.json
- [ ] `python skillrl/scripts/generate_skill.py ...` → skill-v1-initial.md
- [ ] **人工 Review** skill-v1-initial.md（30min），必要时手动补充

### Round 1（约 6-8h）

- [ ] `bash skillrl/scripts/deploy_skill.sh skillrl/skills/skill-v1-initial.md`
- [ ] `harbor run job-100tasks-skill.yaml`（或 skillrl/configs/job-r1-skill-v1.yaml）
- [ ] 生成 report-r1.json
- [ ] 确认成功率 ≥ 80%，退步 ≤ 3

### Phase B（约 1-2h）

- [ ] `python skillrl/scripts/optimize_skill.py ...` → r1-delta-analysis.json + skill-v2-optimized.md
- [ ] **人工 Review** skill-v2-optimized.md（30min），重点检查退步修复

### Round 2（约 6-8h）

- [ ] `bash skillrl/scripts/deploy_skill.sh skillrl/skills/skill-v2-optimized.md`
- [ ] `harbor run job-100tasks-skill-v2.yaml`
- [ ] 生成 report-r2.json
- [ ] 确认成功率 ≥ 84%

### Final

- [ ] `python skillrl/scripts/generate_comparison_report.py ...`
- [ ] Review comparison-report.md

---

## 时间与成本估算

| 阶段 | 耗时 | API 成本 | 人工介入 |
|------|------|---------|---------|
| Round 0 评测 | 6-8h | ~$15-25 | 无 |
| Phase A 分析 | 1-2h | ~$0.5（25 次 LLM 调用）| Review Skill v1（30min） |
| Round 1 评测 | 6-8h | ~$15-25 | 无 |
| Phase B 分析 | 0.5-1h | ~$0.5 | Review Skill v2（30min） |
| Round 2 评测 | 6-8h | ~$15-25 | 无 |
| Final 报告 | 5min | 0 | Review（30min） |
| **总计** | **~3 天** | **~$50-75** | **~2h** |

---

## 预期结果与判断标准

| Round | Skill | 预期成功率 | 预期增幅 |
|-------|-------|-----------|---------|
| R0 | 无 | 75% | 基线 |
| R1 | v1（初版，针对高频失败模式） | 80-83% | +5%~+8% |
| R2 | v2（修复退步 + 补充新模式） | 84-88% | +9%~+13% |

**成功判断标准**：
- 最低成功：R2 成功率 ≥ 82%（vs R0 +7%）
- 预期成功：R2 成功率 ≥ 85%（vs R0 +10%）
- 超预期：R2 成功率 ≥ 88%（vs R0 +13%）

**异常处理**：
1. **R1 提升 < 3%**：检查 Skill 是否被正确加载（看 claude-code.txt 中有无 `used_skill: true`）
2. **R1 退步 > 5**：Skill 内容过于激进，重写 v1 中的操作指导，加"谨慎操作"约束
3. **R2 vs R1 无提升**：Skill prompt 已到边际，考虑升级模型（如 Claude Sonnet）
4. **始终失败 > 20**：这些 task 超出 Skill 能力范围，记录为"需模型能力提升"
