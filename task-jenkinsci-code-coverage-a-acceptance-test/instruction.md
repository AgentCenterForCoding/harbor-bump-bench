# Fix Maven Compilation Failure: acceptance-test-harness 5588.vd13b_52985008 -> 5623.v3e1d330b_89e0

## Context

Project `code-coverage-api-plugin` (by jenkinsci) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.jenkins-ci:acceptance-test-harness` from `5588.vd13b_52985008` to `5623.v3e1d330b_89e0` (other update).

Reference PR: https://github.com/jenkinsci/code-coverage-api-plugin/pull/707

## Your Task

The source code is in `/code-coverage-api-plugin`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /code-coverage-api-plugin && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `5623.v3e1d330b_89e0` has API changes vs `5588.vd13b_52985008`.
   Review the failing source files and update calls to match the new API.
   
   

3. **Apply fixes** to the Java source files in `/code-coverage-api-plugin`.

4. **Verify:**
   ```bash
   cd /code-coverage-api-plugin && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
