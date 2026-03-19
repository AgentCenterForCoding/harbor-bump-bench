# Fix Maven Compilation Failure: snakeyaml 1.17 → 1.31

## Context

Project `polyglot-maven` has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.yaml:snakeyaml` from `1.17` to `1.31`.

Reference PR: https://github.com/takari/polyglot-maven/pull/244

## Your Task

The source code is in `/polyglot-maven`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /polyglot-maven && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `1.31` has API changes vs `1.17`.
   Review the failing source files and update calls to match the new API.

3. **Apply fixes** to the Java source files in `/polyglot-maven`.

4. **Verify:**
   ```bash
   cd /polyglot-maven && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
