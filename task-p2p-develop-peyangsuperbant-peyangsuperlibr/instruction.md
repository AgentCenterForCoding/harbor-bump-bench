# Fix Maven Compilation Failure: PeyangSuperLibrary 114.191.9 -> 114.191.98.10

## Context

Project `PeyangSuperbAntiCheat` (by P2P-Develop) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`com.github.P2P-Develop:PeyangSuperLibrary` from `114.191.9` to `114.191.98.10` (other update).

Reference PR: https://github.com/P2P-Develop/PeyangSuperbAntiCheat/pull/92

## Your Task

The source code is in `/PeyangSuperbAntiCheat`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /PeyangSuperbAntiCheat && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `114.191.98.10` has API changes vs `114.191.9`.
   Review the failing source files and update calls to match the new API.
   
   

3. **Apply fixes** to the Java source files in `/PeyangSuperbAntiCheat`.

4. **Verify:**
   ```bash
   cd /PeyangSuperbAntiCheat && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
