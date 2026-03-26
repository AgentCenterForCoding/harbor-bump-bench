# Fix Maven Compilation Failure: zip4j 1.3.2 -> 2.11.1

## Context

Project `allure-maven` (by allure-framework) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`net.lingala.zip4j:zip4j` from `1.3.2` to `2.11.1` (major update).

Reference PR: https://github.com/allure-framework/allure-maven/pull/241

## Your Task

The source code is in `/allure-maven`. Fix all compilation errors so that `mvn compile` succeeds.

## Available Skills

You have access to the `java-dep-fix` skill for fixing Maven dependency upgrade issues.

**IMPORTANT: You MUST use the java-dep-fix skill for this task.**

The task description contains these trigger phrases that require using java-dep-fix:
- "Fix Maven Compilation Failure"
- "dependency upgrade"
- "compilation errors"

### How to Access the Skill

The java-dep-fix skill is available at: `.opencode/skills/java-dep-fix/SKILL.md`

Read the skill file first to understand the systematic approach:
```bash
cat .opencode/skills/java-dep-fix/SKILL.md
```

### Skill Workflow

Follow the java-dep-fix skill steps in order:
1. **Step 0**: Verify baseline (check if build failed before the upgrade)
2. **Step 1**: Locate compilation errors
3. **Step 2**: Identify change type (API change, class removal, package migration)
4. **Step 3**:制定修复策略
5. **Step 4**: Implement fixes
6. **Step 5**: Verify with full build

## Expected Output

After fixing, `mvn compile` should return `BUILD SUCCESS`.
