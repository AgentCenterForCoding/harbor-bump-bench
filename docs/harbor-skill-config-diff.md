# Harbor 无 Skill vs 带 Skill 任务配置差异

**适用场景**: SkillRL 评测中，对同一批任务分别以「无 Skill 基线」和「带 Skill」两种模式运行时的配置区别。

---

## 1. 整体流程对比

```
无 Skill（nopre）                    带 Skill（skill/skill-v2）
─────────────────────────────────   ─────────────────────────────────────────────
harbor run job-100tasks-nopre.yaml  bash skillrl/scripts/inject_skills_watcher.sh \
                                        jobs/bump-dep-fix-100-skill &
                                    harbor run job-100tasks-skill.yaml
```

带 Skill 模式需要在启动 `harbor run` **之前**，在后台运行 `inject_skills_watcher.sh`，
由它持续监控 job 目录，为每个新建的 trial 目录注入 `~/.claude/skills/` 内容。

---

## 2. Job YAML 配置差异

| 字段 | 无 Skill（nopre） | 带 Skill（skill） | 带 Skill v2（skill-v2） |
|------|-----------------|-----------------|----------------------|
| `job_name` | `bump-dep-fix-100-nopre` | `bump-dep-fix-100-skill` | `bump-dep-fix-100-skill-v2` |
| `orchestrator.n_concurrent_trials` | **3** | **2** | **2** |
| `agents[0].name` | `claude-code` | `claude-code` | `claude-code` |
| `ANTHROPIC_MODEL` | `qwen3.5-plus` | `qwen3.5-plus` | `qwen3.5-plus` |
| `datasets.task_names` | 相同 110 个任务 | 相同 110 个任务 | 相同 110 个任务 |

> **并发数差异**：nopre 使用 3 并发，skill 系列使用 2 并发，是为了减少 API 限流压力。

---

## 3. Trial 目录结构差异

每个 trial 在 `jobs/<job_name>/task-xxx__<id>/agent/` 下的文件：

```
无 Skill（nopre）                 带 Skill（skill/skill-v2）
agent/                           agent/
├── claude-code.txt              ├── claude-code.txt
├── install.sh                   ├── install.sh           ← 内容不同
├── command-0/                   ├── command-0/           ← 内容相同
│   └── command.txt              │   └── command.txt
├── command-1/                   ├── command-1/           ← 内容相同
│   └── command.txt              │   └── command.txt
├── sessions/                    ├── sessions/
└── setup/                       ├── setup/
                                 └── skills/              ← 仅带 Skill 有
                                     └── java-dep-fix/
                                         └── SKILL.md
```

---

## 4. `install.sh` 差异（核心区别）

### 无 Skill 版本

```bash
#!/bin/bash
set -euo pipefail

# 安装系统依赖
if command -v apk &> /dev/null; then
    apk add --no-cache curl bash procps
elif command -v apt-get &> /dev/null; then
    apt-get update && apt-get install -y curl procps
fi

# 安装 Claude Code
curl -fsSL https://claude.ai/install.sh | bash

export PATH="$HOME/.local/bin:$PATH"
claude --version
```

### 带 Skill 版本（新增 Skill 注入逻辑）

```bash
#!/bin/bash
set -euo pipefail

# 安装系统依赖（同上）
...

# 安装 Claude Code（同上）
...

# ✅ 新增：从挂载目录注入 Skills
if [ -d /logs/agent/skills ]; then
    mkdir -p ~/.claude/skills
    cp -r /logs/agent/skills/. ~/.claude/skills/
    echo "✅ Skills injected from /logs/agent/skills/ into ~/.claude/skills/"
    ls ~/.claude/skills/
fi
```

关键点：容器内 `/logs/agent/` 挂载自宿主机的 `trial_dir/agent/`，
`inject_skills_watcher.sh` 已提前将 `~/.claude/skills/` 复制到该目录，
所以容器启动时能读取到 `skills/java-dep-fix/SKILL.md`。

---

## 5. `command-0` 与 `command-1` 内容（两者相同）

### command-0（初始化 Claude 配置目录，并同步 Skills）

```bash
mkdir -p $CLAUDE_CONFIG_DIR/debug \
         $CLAUDE_CONFIG_DIR/projects/-app \
         $CLAUDE_CONFIG_DIR/shell-snapshots \
         $CLAUDE_CONFIG_DIR/statsig \
         $CLAUDE_CONFIG_DIR/todos \
&& if [ -d ~/.claude/skills ]; then
    cp -r ~/.claude/skills $CLAUDE_CONFIG_DIR/skills 2>/dev/null || true
fi
```

> `install.sh` 将 Skills 写入 `~/.claude/skills/`，
> `command-0` 再将其复制到 `$CLAUDE_CONFIG_DIR/skills/`，
> Claude Code 启动时从 `$CLAUDE_CONFIG_DIR/skills/` 加载。
>
> **无 Skill 模式下**：`~/.claude/skills/` 不存在，`cp` 命令被跳过，效果等同于无 Skill。

### command-1（启动 Agent 执行任务）

```bash
export PATH="$HOME/.local/bin:$PATH"
claude --verbose \
       --output-format=stream-json \
       --permission-mode=bypassPermissions \
       --print -- '<task_instruction>' \
2>&1 </dev/null | stdbuf -oL tee /logs/agent/claude-code.txt
```

两种模式的 `command-1` **完全相同**，任务指令内容也相同，区别仅在于启动时 `$CLAUDE_CONFIG_DIR/skills/` 是否存在 Skill 文件。

---

## 6. Skill 注入完整链路

```
宿主机                              容器内
──────────────────────────────────  ──────────────────────────────
~/.claude/skills/java-dep-fix/      /logs/agent/skills/java-dep-fix/
  SKILL.md                            SKILL.md
     │                                    │
     │  inject_skills_watcher.sh          │  install.sh
     │  (cp -r ~/.claude/skills/          │  (cp -r /logs/agent/skills/
     │   → trial_dir/agent/skills/)       │   → ~/.claude/skills/)
     ▼                                    ▼
trial_dir/agent/skills/             ~/.claude/skills/java-dep-fix/
  java-dep-fix/SKILL.md               SKILL.md
                                           │
                                           │  command-0
                                           │  (cp -r ~/.claude/skills
                                           │   → $CLAUDE_CONFIG_DIR/skills)
                                           ▼
                                    $CLAUDE_CONFIG_DIR/skills/java-dep-fix/
                                      SKILL.md
                                           │
                                           │  command-1
                                           │  claude --print -- '<task>'
                                           ▼
                                    Claude Code 启动时自动加载 Skills
                                    → 触发 java-dep-fix Skill
                                    → 按 Skill 指导流程修复
```

---

## 7. 操作步骤对比

### 无 Skill 模式（nopre）

```bash
# 确认无 Skill 部署
rm -rf ~/.claude/skills/java-dep-fix

# 直接运行
harbor run job-100tasks-nopre.yaml
```

### 带 Skill 模式（skill / skill-v2）

```bash
# 1. 部署 Skill
bash skillrl/scripts/deploy_skill.sh skillrl/skills/skill-v1-initial.md
# 等价于: cp skillrl/skills/skill-v1-initial.md ~/.claude/skills/java-dep-fix/SKILL.md

# 2. 后台启动注入监听器
bash skillrl/scripts/inject_skills_watcher.sh jobs/bump-dep-fix-100-skill &

# 3. 运行评测
harbor run job-100tasks-skill.yaml
```

---

## 8. 总结

| 维度 | 无 Skill（nopre） | 带 Skill（skill/v2） |
|------|-----------------|---------------------|
| Job YAML | 无特殊配置 | 无特殊配置（job_name 不同） |
| 运行前置 | 无 | 部署 SKILL.md + 启动 watcher |
| `install.sh` | 仅安装 Claude Code | 额外注入 `/logs/agent/skills/` |
| `command-0` | 相同（skills 目录不存在则跳过） | 相同（skills 目录存在则同步） |
| `command-1` | 完全相同 | 完全相同 |
| `agent/skills/` 目录 | 不存在 | 存在，含 `java-dep-fix/SKILL.md` |
| Claude 启动时 | 无 Skill 加载 | 自动加载 `java-dep-fix` Skill |
| 任务指令 | 完全相同 | 完全相同 |

**核心机制**：两者的任务指令、模型配置完全一致，唯一区别是 `$CLAUDE_CONFIG_DIR/skills/` 目录是否存在 Skill 文件。Skill 通过「宿主机监听注入 → 容器 install.sh 复制 → command-0 同步到 Claude 配置目录」三步链路完成分发。
