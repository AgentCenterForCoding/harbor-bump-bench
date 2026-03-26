# Agent Instructions for allure-maven Dependency Fix

## Available Skills

This task has the `java-dep-fix` skill available.

**Skill Location:** `.opencode/skills/java-dep-fix/SKILL.md`

## Trigger Conditions

The java-dep-fix skill should be triggered when the task description contains:
- "Fix Maven Compilation Failure"
- "dependency upgrade"
- "compilation error"
- "bump dependency"
- "cannot find symbol"
- "package does not exist"

## Usage

1. Read the skill file first: `cat .opencode/skills/java-dep-fix/SKILL.md`
2. Follow the systematic diagnostic steps in the skill
3. Apply the fix patterns described
4. Verify with `mvn compile`

## Skill Summary

The java-dep-fix skill provides:
- Step 0: Baseline verification (check pre-upgrade build status)
- Step 1: Error location and categorization
- Step 2: Change type identification (API change, class removal, package migration)
- Step 3: Fix strategy selection
- Step 4: Implementation patterns for common dependencies
- Step 5: Verification and reporting
