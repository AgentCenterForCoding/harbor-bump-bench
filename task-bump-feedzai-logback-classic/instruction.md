# Fix Maven Compilation Failure: logback-classic 1.2.11 -> 1.4.5

## Context

Project `pdb` (by feedzai) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`ch.qos.logback:logback-classic` from `1.2.11` to `1.4.5` (minor update).

Reference PR: https://github.com/feedzai/pdb/pull/365

## Your Task

The source code is in `/pdb`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /pdb && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `1.4.5` has API changes vs `1.2.11`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/ch/qos/logback/logback-classic/1.2.11/logback-classic-1.2.11-sources.jar
   - New API sources: https://repo1.maven.org/maven2/ch/qos/logback/logback-classic/1.4.5/logback-classic-1.4.5-sources.jar

3. **Apply fixes** to the Java source files in `/pdb`.

4. **Verify:**
   ```bash
   cd /pdb && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
