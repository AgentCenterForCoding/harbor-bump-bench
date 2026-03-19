# Fix Maven Compilation Failure: mina-core 2.1.5 → 2.2.1

## Context

Project `quickfixj` has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.apache.mina:mina-core` from `2.1.5` to `2.2.1`.

Reference PR: https://github.com/quickfix-j/quickfixj/pull/502

## Your Task

The source code is in `/quickfixj`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /quickfixj && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `2.2.1` has API changes vs `2.1.5`.
   Review the failing source files and update calls to match the new API.

3. **Apply fixes** to the Java source files in `/quickfixj`.

4. **Verify:**
   ```bash
   cd /quickfixj && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
