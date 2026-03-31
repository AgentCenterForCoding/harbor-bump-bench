const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5

const FONT = "Microsoft YaHei";
const slide = pres.addSlide();
slide.background = { color: "FFFFFF" };

// ── Header ──
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 13.33, h: 0.50,
  fill: { color: "C0392B" }, line: { color: "C0392B" }
});
slide.addText("Skill 开发流程：8 步从定义到生产演进", {
  x: 0.28, y: 0.05, w: 9.0, h: 0.40,
  fontSize: 21, bold: true, color: "FFFFFF", fontFace: FONT,
  valign: "middle", margin: 0
});
slide.addText("定义 · 编写 · 合规校验 · 离线评测 · 生产监控", {
  x: 9.2, y: 0.05, w: 3.9, h: 0.40,
  fontSize: 9, italic: true, color: "FFCCCC", fontFace: FONT,
  valign: "middle", align: "right", margin: 0
});

// ── Layout constants ──
const pColX  = 0.13;   // phase column x
const pColW  = 1.05;   // phase column width
const stepX  = 1.28;   // step content area start
const stepW  = 11.90;  // step content total width (to x≈13.18)
const circX  = stepX + 0.10;  // circle center-left
const badgeD = 0.32;   // circle diameter
const titleW = 2.10;   // step title text width
const rowY0  = 0.52;   // first row top y
const rowH   = 0.862;  // (7.5 - 0.52 - 0.06) / 8
const rowGap = 0.040;  // gap between rows (background rect = rowH - rowGap)

// divider between title and description
const divX  = circX + badgeD + 0.10 + titleW + 0.08;
const descX = divX + 0.10;
const descW = stepX + stepW - descX - 0.15;

// ── Phases (color spans rows) ──
const phases = [
  { lines: ["开发前", "定义阶段"], color: "8E44AD", rows: [0] },
  { lines: ["开发期", "编写阶段"], color: "2980B9", rows: [1, 2] },
  { lines: ["合规校验", "单元测试"], color: "D35400", rows: [3, 4] },
  { lines: ["离线评测", "集成测试"], color: "27AE60", rows: [5, 6] },
  { lines: ["生产监控", "持续改进"], color: "C0392B", rows: [7] },
];

// ── Steps ──
const steps = [
  {
    phaseIdx: 0, num: "1", title: "定义成功标准",
    desc: "将「成功」拆成 Outcome / Process / Style / Efficiency 四类，锚定后续所有 Eval 的评判基准，防止「凭感觉改」"
  },
  {
    phaseIdx: 1, num: "2", title: "创建 SKILL.md",
    desc: "通过 $skill-creator 生成 name + description，二者直接决定触发逻辑，是 Skill 的「公开契约」，写错则后续所有测试漂移"
  },
  {
    phaseIdx: 1, num: "3", title: "手动触发挖假设",
    desc: "手动激活 Skill，主动暴露对环境、顺序、权限的隐含前提；每次手动修复 = 一条未来的自动化 Eval 用例"
  },
  {
    phaseIdx: 2, num: "4", title: "建 prompt 集",
    desc: "用 CSV 记录 10–20 条，覆盖显式触发 / 隐式触发 / 上下文变体 / 负向控制，验证触发精度"
  },
  {
    phaseIdx: 2, num: "5", title: "确定性断言",
    desc: "用 JSONL 事件流做程序化检查（文件存在？命令执行？序列正确？），快速可解释，最先发现回归"
  },
  {
    phaseIdx: 3, num: "6", title: "LLM-as-Judge",
    desc: "用 JSON Schema 约束 LLM 评判输出（passed / score / 说明），覆盖确定性规则无法判断的风格、结构、语义质量"
  },
  {
    phaseIdx: 3, num: "7", title: "分层深层信号",
    desc: "按成熟度追加命令次数分析、Token 追踪、构建验证、权限回归等；原则：只在能减少真实风险时才加昂贵检查"
  },
  {
    phaseIdx: 4, num: "8", title: "真实失败驱动演进",
    desc: "线上每次回归反哺 prompt 数据集，形成「生产故障 → 补充 Eval 用例 → 防止复发」的持续改进飞轮"
  },
];

// ── 1. Draw step row backgrounds ──
steps.forEach((_, i) => {
  const ry = rowY0 + i * rowH;
  const rh = rowH - rowGap;
  slide.addShape(pres.shapes.RECTANGLE, {
    x: stepX, y: ry, w: stepW, h: rh,
    fill: { color: i % 2 === 0 ? "FAFAFA" : "FFFFFF" },
    line: { color: "EBEBEB", width: 0.5 }
  });
});

// ── 2. Draw phase column blocks ──
phases.forEach(phase => {
  const r0 = phase.rows[0];
  const rN = phase.rows[phase.rows.length - 1];
  const py = rowY0 + r0 * rowH;
  const ph = (rN - r0 + 1) * rowH - rowGap;

  slide.addShape(pres.shapes.RECTANGLE, {
    x: pColX, y: py, w: pColW, h: ph,
    fill: { color: phase.color }, line: { color: phase.color }
  });
  // Two-line label
  slide.addText([
    { text: phase.lines[0], options: { breakLine: true, fontSize: 9.5, bold: true, color: "FFFFFF", fontFace: FONT } },
    { text: phase.lines[1], options: { fontSize: 8.5, color: "EEE8FF", fontFace: FONT } }
  ], {
    x: pColX, y: py, w: pColW, h: ph,
    align: "center", valign: "middle", margin: 0, lineSpacingMultiple: 1.4
  });
});

// ── 3. Vertical timeline connector (through all circles) ──
const lineTopY    = rowY0 + (rowH - rowGap) / 2;
const lineBottomY = rowY0 + 7 * rowH + (rowH - rowGap) / 2;
slide.addShape(pres.shapes.LINE, {
  x: circX + badgeD / 2, y: lineTopY + badgeD / 2 + 0.02,
  w: 0, h: lineBottomY - lineTopY - badgeD - 0.04,
  line: { color: "D0D0D0", width: 1 }
});

// ── 4. Draw each step ──
steps.forEach((step, i) => {
  const ry  = rowY0 + i * rowH;
  const rh  = rowH - rowGap;
  const cy  = ry + (rh - badgeD) / 2;
  const pColor = phases[step.phaseIdx].color;

  // Step circle
  slide.addShape(pres.shapes.OVAL, {
    x: circX, y: cy, w: badgeD, h: badgeD,
    fill: { color: pColor }, line: { color: "FFFFFF", width: 1.5 }
  });
  slide.addText(step.num, {
    x: circX, y: cy, w: badgeD, h: badgeD,
    fontSize: 10, bold: true, color: "FFFFFF", fontFace: FONT,
    align: "center", valign: "middle", margin: 0
  });

  // Step title
  const titleX = circX + badgeD + 0.10;
  slide.addText(step.title, {
    x: titleX, y: ry + 0.06, w: titleW, h: rh - 0.12,
    fontSize: 11, bold: true, color: "1A1A1A", fontFace: FONT,
    valign: "middle", margin: 0
  });

  // Vertical divider
  slide.addShape(pres.shapes.LINE, {
    x: divX, y: ry + 0.09, w: 0, h: rh - 0.18,
    line: { color: "D8D8D8", width: 0.75 }
  });

  // Description
  slide.addText(step.desc, {
    x: descX, y: ry + 0.06, w: descW, h: rh - 0.12,
    fontSize: 9.5, color: "444444", fontFace: FONT,
    valign: "middle", margin: 0, lineSpacingMultiple: 1.2
  });
});

// ── 5. Flywheel hint: dashed loop on right edge ──
const flY1 = rowY0 + 0.20;
const flY2 = rowY0 + 8 * rowH - rowGap - 0.20;
const flX  = 13.22;
slide.addShape(pres.shapes.LINE, {
  x: flX, y: flY1, w: 0, h: flY2 - flY1,
  line: { color: "DDCCEE", width: 1.5, dashType: "sysDash",
          endArrowType: "open", beginArrowType: "open" }
});

pres.writeFile({ fileName: "skill-dev-process.pptx" })
  .then(() => console.log("Generated: skill-dev-process.pptx"))
  .catch(e => { console.error(e); process.exit(1); });
