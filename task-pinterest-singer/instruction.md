# Fix Maven Compilation Failure: libthrift 0.12.0->0.16.0

## Context

Project has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped `libthrift` from `0.12.0` to `0.16.0`.

## Your Task

The source code is in the WORKDIR. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```
2. **Understand breaking changes:** The new version has API changes vs the old version.
3. **Fix the code:** Modify source files to use the new API.
4. **Verify:** Run `mvn compile -B -q` to confirm the fix.
