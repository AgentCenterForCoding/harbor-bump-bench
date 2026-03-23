# SkillRL 三轮评测对比报告

**生成时间**: 2026-03-23 14:40

**测评集**: 110 tasks  |  **模型**: qwen3.5-plus


---

## 1. 总览

| 指标 | Round 0（无 Skill） | Round 1（Skill v1） | Round 2（Skill v2） |
|------|-------------------|--------------------|---------------------|
| **成功数** | 68 | 87 | 91 |
| **失败数** | 42 | 23 | 19 |
| **成功率** | 61.8% | 79.1% | 82.7% |
| **vs 基线** | — | +17.3% | +20.9% |

## 2. Task 轨迹分类

| 轨迹类型 | 数量 | 说明 |
|---------|------|------|
| 始终通过 | **64** | 三轮全部成功 |
| v1 修复并稳定 | **18** | Skill v1 有效，且 v2 保持 |
| v2 额外修复 | **5** | Skill v2 才解决 |
| v1 修复但 v2 退步 | **2** | 需检查 v2 是否引入干扰 |
| v1 退步 v2 修复 | **1** | v2 纠正了 v1 的问题 |
| v1 导致退步 | **3** | Skill 干扰了原本可以成功的 task |
| 始终失败 | **9** | 三轮全部失败，超出 Skill 能力范围 |
| 其他 | **3** |  |

## 3. 关键结论

- Skill v1 直接修复了 **20** 个 task
- Skill v2 额外修复了 **5** 个 task
- 始终失败（模型能力瓶颈）: **9** 个
- ⚠️  Skill v1 退步: **3** 个 task（Skill 内容过于激进）

## 4. 各 Task 详细结果

| Task | 依赖 | 升级类型 | R0 | R1 | R2 | 轨迹 |
|------|------|----------|----|----|----|----|
| `task-1and1-snmpman-snmp4j-agent` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-allure-framewor-allure-mave` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-alphagov-pay-adminusers-log` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-artipie-docker-adapter-asto` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-artipie-docker-adapter-http` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-artipie-http-asto-core` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-assert-kth-depclean-plexus-` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-assert-kth-sorald-sonarlint` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-assertkth-flacoco` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-btrplace-scheduler-javapars` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-1and1-snmp4j-agent` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-allure-frame-zip4j` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-bump-alphagov-logback-class` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-artipie-asto-core` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-artipie-http` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-assert-kth-maven-suref` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-assert-kth-plexus-util` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-assert-kth-sonarlint-c` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-btrplace-javaparser-co` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-camunda-comm-spring-co` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-feedzai-logback-classi` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-games647-spongeapi` |  |  | ❌ | ✅ | ❌ | ⚠️v1修v2退 |
| `task-bump-getgauge-reflections` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-google-struts2-core` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-googleapis-google-api-` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-bump-googleapis-google-clou` |  |  | ❌ | ❌ | ❌ | 💀始终失败 |
| `task-bump-guhilling-jakarta-anno` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-bump-hantsy-jakarta-mvc-api` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-internationa-spring-bo` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-internationa-spring-co` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-internationa-spring-we` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-jadler-mocki-jetty-ser` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-jcabi-hamcrest-library` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-bump-jcabi-jcabi-aspects` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-jenkinsci-acceptance-t` |  |  | ❌ | ❌ | ❌ | 💀始终失败 |
| `task-bump-kokuwaio-spring-contex` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-lukas-krecan-spring-co` |  |  | ✅ | ❌ | ❌ | ❌v1退步 |
| `task-bump-mathieucarbo-maven-dep` |  |  | ❌ | ❌ | ✅ | 🔧v2修复 |
| `task-bump-maxmind-geoip2` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-micycle1-tinspin-index` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-nemproject-flyway-core` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-nemproject-hibernate-v` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-bump-p2p-develop-peyangsupe` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-pac4j-jakarta-servlet-` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-bump-pkiraly-metadata-qa-ap` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-bump-premium-mind-jakarta-v` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-premium-mind-jaxb2-bas` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-bump-qqxx6661-spring-cloud-` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-redisgraph-jedis` |  |  | ❌ | ❌ | ✅ | 🔧v2修复 |
| `task-bump-sabomichal-jooq-meta` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-samsung-spring-core` |  |  | ❌ | ❌ | ✅ | 🔧v2修复 |
| `task-bump-saucelabs-plexus-archi` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-bump-takari-snakeyaml` |  |  | ❌ | ❌ | ❌ | 💀始终失败 |
| `task-bump-volodya-lomb-opennlp-t` |  |  | ❌ | ❌ | ✅ | 🔧v2修复 |
| `task-bump-wesleyosanto-mapstruct` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-bump-wireapp-dropwizard-cli` |  |  | ✅ | ❌ | ❌ | ❌v1退步 |
| `task-bump-wmaarts-pitest-entry` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-xdev-softwar-jasperrep` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-bump-zold-io-cactoos` |  |  | ❌ | ✅ | ❌ | ⚠️v1修v2退 |
| `task-camunda-communi-camunda-pla` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-feedzai-pdb` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-feedzai-pdb-logback-classic` |  |  | ❌ | ✅ | ✅ | ？其他 |
| `task-games647-changeskin-spongea` |  |  | ❌ | ❌ | ❌ | 💀始终失败 |
| `task-getgauge-gauge-java-reflect` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-google-guice-struts2-core` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-googleapis-google-cloud-ja-` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-googleapis-java-pubsub-gro-` |  |  | ❌ | ❌ | ❌ | 💀始终失败 |
| `task-guhilling-cdi-test-jakarta.` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-hantsy-jakartaee-mvc-s-jaka` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-ids-spring` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-international-d-ids-messagi` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-jadler-mocking-jadler-jetty` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-jcabi-jcabi-github-jcabi-as` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-jcabi-jcabi-http-hamcrest-l` |  |  | ❌ | ✅ | ✅ | ？其他 |
| `task-jcabi-jcabi-s3-jcabi-aspect` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-jcabi-jcabi-simpledb-jcabi-` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-jcabi-jcabi-ssh-jcabi-aspec` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-jenkinsci-code-coverage-a-a` |  |  | ❌ | ❌ | ❌ | 💀始终失败 |
| `task-kokuwaio-micronaut-opena-sp` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-lukas-krecan-future-convert` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-mathieucarbou-license-maven` |  |  | ✅ | ❌ | ❌ | ❌v1退步 |
| `task-maxmind-minfraud-api-ja-geo` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-micycle1-pgs-tinspin-indexe` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-nemproject-nem-flyway-core` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-nemproject-nem-hibernate-va` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-p2p-develop-peyangsuperbant` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-pac4j-dropwizard-pac4-jakar` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-pinterest-singer` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-pkiraly-qa-catalogue-metada` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-polyglot-snakeyaml` |  |  | ❌ | ❌ | ❌ | 💀始终失败 |
| `task-premium-minds-billy-jaxb2-b` |  |  | ✅ | ❌ | ✅ | 🔄v1退v2修 |
| `task-premium-minds-wicket-crudif` |  |  | ❌ | ✅ | ✅ | ？其他 |
| `task-qqxx6661-log-record-spring-` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-quickfixj-mina` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-redisgraph-jredisgraph-jedi` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-sabomichal-jooq-meta-postg-` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-samsung-lpvs-spring-core` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-saucelabs-ci-sauce-plexus-a` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |
| `task-takari-polyglot-maven-snake` |  |  | ❌ | ❌ | ❌ | 💀始终失败 |
| `task-volodya-lombroz-jtcop-openn` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-wesleyosantos91-poc-multi-m` |  |  | ❌ | ❌ | ✅ | 🔧v2修复 |
| `task-wireapp-lithium-dropwizard-` |  |  | ❌ | ❌ | ❌ | 💀始终失败 |
| `task-wmaarts-pitest-mutation-pit` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-xdev-software-biapi-jasperr` |  |  | ✅ | ✅ | ✅ | ✅始终通过 |
| `task-zold-io-java-api-cactoos` |  |  | ❌ | ✅ | ✅ | 🔧v1修复 |