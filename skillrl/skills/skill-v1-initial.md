---
name: java-dep-fix
description: >
  修复 Java Maven 项目因依赖版本升级导致的编译失败。触发场景：
  Fix Maven Compilation Failure、dependency upgrade compile error、
  bump dependency、依赖升级编译失败、cannot find symbol、
  package does not exist、maven compile error after version bump。
  当任务描述中包含"升级依赖"、"bump"、"compilation error"时自动使用此 Skill。
---

# Java 依赖升级编译修复 Skill

## 诊断优先级（按处理顺序）

```
1. 先判断失败类型（API 变更 / 类移除 / 包迁移 / 环境问题）
2. 再判断升级幅度（major.minor.patch 跨度）
3. 最后制定修复策略（逐个修复 vs 批量迁移 vs 报告超范围）
```

---

## Step 1：定位编译错误

```bash
# 执行编译，捕获所有错误
mvn compile 2>&1 | tee /tmp/compile-errors.txt

# 提取所有唯一的 [ERROR] 行（去掉重复）
grep '\[ERROR\]' /tmp/compile-errors.txt | grep -v 'To see the full' | grep -v 'Re-run Maven' | sort -u

# 统计 cannot find symbol 的数量（决定修复策略）
grep 'cannot find symbol' /tmp/compile-errors.txt | wc -l
```

**关键判断**：
- `cannot find symbol` 数量 > 10 → 批量分析模式（见 Step 2B）
- `requires Maven version` 或 `plugin incompatible` → 环境问题，直接报告（见 Step 5E）
- `package xxx does not exist` → 包路径迁移（优先检查 javax→jakarta）

---

## Step 2：识别变更类型

### Step 2A：单一/少量 symbol 缺失（≤10个）

```bash
# 提取缺失的具体 symbol 名称
grep -A2 'cannot find symbol' /tmp/compile-errors.txt | grep 'symbol:' | awk '{print $2, $3}' | sort -u

# 查看该依赖的版本差异（帮助判断变更类型）
# 在 pom.xml 中找当前版本，对比 prevVersion/newVersion
cat pom.xml | grep -A2 '<dependency>' | grep -E 'artifactId|version'
```

判断规则：
- `class XXX` 缺失 → 类被移除或重命名 → 查新版 API
- `method XXX` 缺失 → 方法签名变更 → 查 changelog
- `package XXX does not exist` → 包路径迁移（javax→jakarta 最常见）

### Step 2B：大量 symbol 缺失（>10个）—— 批量策略

```bash
# 汇总所有缺失 symbol，按类分组
grep -A3 'cannot find symbol' /tmp/compile-errors.txt \
  | grep -E 'symbol:|location:' \
  | paste - - \
  | awk -F'\t' '{print $1, "|", $2}' \
  | sort -u > /tmp/missing-symbols.txt
cat /tmp/missing-symbols.txt

# 查看涉及的源文件
grep '\[ERROR\].*\.java:' /tmp/compile-errors.txt | sed 's/\[ERROR\] //;s/:[0-9].*//' | sort -u
```

批量分析后，制定一次性修复计划，不要逐个文件修复后再次编译。

---

## Step 3：制定修复策略

根据错误模式选择策略：

| 错误类型 | 识别特征 | 修复策略 |
|---------|---------|---------|
| 方法签名变更 | `cannot find symbol` + `method XXX` | 查新版 javadoc/源码，找替代方法 |
| 类被移除 | `cannot find symbol` + `class XXX` | 查 changelog，找新类名或替代 API |
| 包路径迁移 | `package javax.XXX does not exist` | 全局替换 javax→jakarta（见模式库）|
| 类移到新模块 | `cannot find symbol` + 特定工具类 | 检查新版 jar，找正确 import |
| API 完全重写 | 涉及核心框架类（@Plugin, CommandSource 等）| 对照迁移文档系统性重写 |
| 接口实现不完整 | `is not abstract and does not override` | 实现所有新增抽象方法 |
| 泛型推断失败 | `incompatible types` + lambda | 添加显式类型参数 |

---

## Step 4：实施修复

### 模式 A：方法不再抛受检异常

```java
// 旧版（如 snakeyaml 1.x / Representer）
protected Set<Property> getProperties(Class type) throws IntrospectionException { ... }

// 新版（移除 throws 声明）
protected Set<Property> getProperties(Class type) { ... }
```

操作：删除方法签名中的 `throws XxxException`，同时删除 import。

### 模式 B：构造函数新增必填参数

```java
// 旧版（如 snakeyaml 2.0 的 Constructor/Representer）
new Constructor(Model.class)            // 旧
new Constructor(Model.class, new LoaderOptions())  // 新

new Representer()                       // 旧
new Representer(new DumperOptions())    // 新
```

操作：查看新版本源码/javadoc，补充新增的必填参数。

### 模式 C：javax → jakarta 包迁移

```bash
# 找所有 javax.annotation 引用
grep -r 'javax\.annotation' src/ --include='*.java' -l
# 批量替换
find src/ -name "*.java" -exec sed -i 's/javax\.annotation\./jakarta.annotation./g' {} \;

# 常见迁移映射：
# javax.annotation.* → jakarta.annotation.*
# javax.servlet.*    → jakarta.servlet.*
# javax.validation.* → jakarta.validation.*
# javax.persistence.* → jakarta.persistence.*
# javax.ws.rs.*      → jakarta.ws.rs.*
```

### 模式 D：类被移除/重命名（plexus-archiver 类型）

```bash
# 查看新版本 jar 中的类列表，确认正确包名
mvn dependency:get -Dartifact=org.codehaus.plexus:plexus-archiver:4.4.0
jar tf ~/.m2/repository/org/codehaus/plexus/plexus-archiver/4.4.0/plexus-archiver-4.4.0.jar \
  | grep -i 'UnArchiver'
```

### 模式 E：大版本 API 重构（jedis 3→4 类型）

jedis 3.x → 4.x 已知变更：
- `RedisPipeline` → `Pipeline`（直接使用 `Pipeline` 类）
- `getConnection()` 方法被移除
- `getResponse(Builder<T>)` 方法调用方式变化

cactoos 0.35 → 0.55 已知变更：
- `LengthOf.intValue()` → `LengthOf.value()`（或 `.intValue()` 需转型）
- `IterableOf` 泛型推断更严格，需要显式类型参数
- `Filtered.isEmpty()` → `new IsEmpty<>(filtered).value()`

snakeyaml 1.x → 2.0 已知变更：
- `Constructor(Class)` → `Constructor(Class, new LoaderOptions())`
- `new Representer()` → `new Representer(new DumperOptions())`
- `getProperties()` 移除 `throws IntrospectionException`

### 模式 F：接口新增抽象方法

```bash
# 查看接口定义，找所有 abstract 方法
# 在实现类中补全未实现的方法
```

---

## Step 5：验证与收尾

### Step 5A：标准验证（必须执行）

```bash
# 必须使用完整编译，不能使用 -pl 排除任何模块
mvn compile 2>&1 | tail -20

# 确认输出包含 BUILD SUCCESS
echo "Exit code: $?"
```

**⚠️ 严禁使用 `mvn compile -pl !module-name` 排除失败模块来规避验证。**  
若某模块本来（升级前）就构建失败，需先验证基线状态再判断。

### Step 5B：成功时的 Summary 格式

```
## 修复完成

**依赖**: groupId:artifactId 版本 X → Y
**错误模式**: [类型，如 方法签名变更 / 包路径迁移]

### 修改文件
1. `src/main/java/...Foo.java`: 删除 throws IntrospectionException
2. `src/main/java/...Bar.java`: 替换 javax.annotation → jakarta.annotation

### 验证结果
mvn compile → BUILD SUCCESS
```

### Step 5C：仍有失败时的策略

```bash
# 重新获取错误列表
mvn compile 2>&1 | grep '\[ERROR\]' | grep -v 'For more\|To see\|Re-run' | sort -u

# 循环：分析新错误 → 修复 → 验证（最多 5 轮）
```

### Step 5D：超范围任务的处理

当满足以下条件时，报告为"超范围失败"，不要无限循环：
- 修复轮次 ≥ 5 次且未收敛
- 框架核心 API 大重构（如 SpongeAPI 7→8，Spring 5→6 全局迁移）
- 需要重写的文件超过 20 个

报告格式：
```
## 修复超范围

**根因**: [升级依赖] X.X → Y.Y 涉及框架级 API 重构，影响 N 个文件 M 处调用。
**已完成**: [已修复的部分]
**未完成**: [剩余工作和原因]
**建议**: 需要参考 [官方迁移文档URL] 进行系统性迁移。
```

### Step 5E：环境问题的处理

当错误是：
- `requires Maven version X.X.X`
- `The plugin XXX requires Maven version`
- `plugin incompatibility`

这是**构建环境问题**，不是依赖升级的代码兼容性问题。

报告格式：
```
## 环境不兼容（非代码问题）

错误: [错误信息]
说明: 此失败由构建工具版本不满足要求导致，与依赖版本升级无直接关系。
不在本次修复范围内。
```

---

## 高频依赖升级速查

| 依赖 | 版本变化 | 主要变更 |
|-----|---------|---------|
| snakeyaml | 1.x → 2.0 | Constructor/Representer 构造函数新增参数，getProperties 移除 throws |
| jedis | 3.x → 4.x | RedisPipeline 类移除，getConnection/getResponse 变更 |
| cactoos | 0.35 → 0.55 | LengthOf.intValue()→value()，泛型更严格 |
| hamcrest | 1.x → 2.x | Matchers 类方法签名调整 |
| jakarta.annotation-api | 1.x → 2.x | javax.annotation.* → jakarta.annotation.* |
| Spring | 5.x → 6.x | javax.* → jakarta.* 全局迁移 |
| dropwizard | 2.x → 4.x | javax.ws.rs → jakarta.ws.rs，jersey 升级 |
| hibernate-validator | 5.x → 8.x | javax.validation → jakarta.validation |

---

## 反模式警告

❌ **不要做的事**：
1. 逐个文件修复 cannot find symbol，不汇总全局再修复（效率低，容易遗漏）
2. 使用 `-pl !module` 排除失败模块后声称任务完成
3. 遇到框架大版本升级（major bump）时不查官方迁移文档直接猜测
4. 修复 5 轮以上仍未收敛时还在继续无限尝试
5. 将构建环境问题（Maven版本不足）误认为代码问题

✅ **应该做的事**：
1. 先运行 `mvn compile` 获取完整错误列表，再制定修复计划
2. 批量 symbol 缺失时先汇总所有缺失 symbol，再查 changelog
3. 怀疑大版本迁移时搜索 `[dependency] migration guide` 或 BREAKING_CHANGES
4. 最终验证必须是 `mvn compile`（完整，无模块排除）
5. 超范围任务清晰报告原因和已完成内容
