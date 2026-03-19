# Fix Maven Compilation Failure: google-api-services-cloudresourcemanager v1-rev20220807-2.0.0 -> v3-rev20220807-2.0.0

## Context

Project `google-cloud-java` (by googleapis) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`com.google.apis:google-api-services-cloudresourcemanager` from `v1-rev20220807-2.0.0` to `v3-rev20220807-2.0.0` (other update).

Reference PR: https://github.com/googleapis/google-cloud-java/pull/8183

## Your Task

The source code is in `/google-cloud-java`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /google-cloud-java && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `v3-rev20220807-2.0.0` has API changes vs `v1-rev20220807-2.0.0`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/com/google/apis/google-api-services-cloudresourcemanager/v1-rev20220807-2.0.0/google-api-services-cloudresourcemanager-v1-rev20220807-2.0.0-sources.jar
   - New API sources: https://repo1.maven.org/maven2/com/google/apis/google-api-services-cloudresourcemanager/v3-rev20220807-2.0.0/google-api-services-cloudresourcemanager-v3-rev20220807-2.0.0-sources.jar

3. **Apply fixes** to the Java source files in `/google-cloud-java`.

4. **Verify:**
   ```bash
   cd /google-cloud-java && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
