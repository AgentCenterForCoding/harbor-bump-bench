# Fix Maven Compilation Failure: zip4j 1.3.2 -> 2.11.1

## Context

Project `allure-maven` (by allure-framework) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`net.lingala.zip4j:zip4j` from `1.3.2` to `2.11.1` (major update).

Reference PR: https://github.com/allure-framework/allure-maven/pull/241

## Your Task

The source code is in `/allure-maven`. Fix all compilation errors so that `mvn compile` succeeds.

## Available Skills

**IMPORTANT: This task requires using the java-dep-fix skill.**

The `java-dep-fix` skill is available at `.opencode/skills/java-dep-fix/SKILL.md` in the container.

### Trigger Phrases (these should trigger the skill):
- "Fix Maven Compilation Failure"
- "dependency upgrade"
- "compilation error"
- "bump dependency"
- "cannot find symbol"
- "package does not exist"

### How to Use

1. First read the skill file: `cat .opencode/skills/java-dep-fix/SKILL.md`
2. Follow the skill's systematic diagnostic steps
3. Apply fixes according to the patterns in the skill
4. Verify with `mvn compile`

## Expected Workflow (from java-dep-fix skill)

1. **Step 0**: Verify baseline - check if build failed before the upgrade
2. **Step 1**: Locate compilation errors with `mvn compile`
3. **Step 2**: Identify change type (API change, class removal, package migration)
4. **Step 3**:制定修复策略 based on error patterns
5. **Step 4**: Implement fixes
6. **Step 5**: Verify with full build - must return `BUILD SUCCESS`
