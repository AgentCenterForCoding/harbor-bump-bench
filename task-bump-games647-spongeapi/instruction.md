# Fix Maven Compilation Failure: spongeapi 7.4.0 -> 8.0.0

## Context

Project `ChangeSkin` (by games647) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.spongepowered:spongeapi` from `7.4.0` to `8.0.0` (major update).

Reference PR: https://github.com/games647/ChangeSkin/pull/240

## Your Task

The source code is in `/ChangeSkin`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /ChangeSkin && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `8.0.0` has API changes vs `7.4.0`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/org/spongepowered/spongeapi/7.4.0/spongeapi-7.4.0-sources.jar
   - New API sources: https://repo1.maven.org/maven2/org/spongepowered/spongeapi/8.0.0/spongeapi-8.0.0-sources.jar

3. **Apply fixes** to the Java source files in `/ChangeSkin`.

4. **Verify:**
   ```bash
   cd /ChangeSkin && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
