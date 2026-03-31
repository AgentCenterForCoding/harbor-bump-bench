const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5

const FONT = "Microsoft YaHei";
const slide = pres.addSlide();
slide.background = { color: "FFFFFF" };

// ── Header bar ──
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 13.33, h: 0.56,
  fill: { color: "C0392B" }, line: { color: "C0392B" }
});
slide.addText("业界 Skill/Agent 测评现状全景", {
  x: 0.3, y: 0.06, w: 9.2, h: 0.44,
  fontSize: 22, bold: true, color: "FFFFFF", fontFace: FONT,
  valign: "middle", margin: 0
});
slide.addText("4阶段评测体系 · 框架对比 · 趋势判断", {
  x: 9.5, y: 0.06, w: 3.6, h: 0.44,
  fontSize: 10, italic: true, color: "FFCCCC", fontFace: FONT,
  valign: "middle", align: "right", margin: 0
});

// ── Card definitions ──
const cards = [
  {
    num: "①", title: "合规校验",
    analogy: "对应传统：单元测试",
    analogySub: "验证最小单元结构正确性",
    hc: "C0392B", fc: "FEF0EF", qBg: "FADBD8",
    maturity: "Adopt ✓", mc: "C0392B",
    trigger: "提交前 · 秒级",
    question: "格式对不对？",
    caps: [
      "Schema 格式自动校验（JSON/Pydantic）",
      "触发规则精度测试（正/负样本分类）",
      "文件引用完整性静态分析",
      "安全/毒性内容扫描"
    ]
  },
  {
    num: "②", title: "离线评测",
    analogy: "对应传统：集成测试",
    analogySub: "验证组件协作与输出质量",
    hc: "7F8C8D", fc: "F4F6F6", qBg: "E5E8E8",
    maturity: "Adopt ✓", mc: "27AE60",
    trigger: "CI/CD · 分钟级",
    question: "效果好不好？",
    caps: [
      "确定性断言（接口可用、文件存在）",
      "LLM-as-Judge 输出质量评分",
      "轨迹分析（工具调用路径是否合理）",
      "多维指标量化（成功率/步骤效率/幻觉率/Token成本）"
    ]
  },
  {
    num: "③", title: "灰度测试",
    analogy: "对应传统：预发验证",
    analogySub: "真实环境小范围上线",
    hc: "5D6D7E", fc: "EBF0F4", qBg: "D5D8DC",
    maturity: "Trial", mc: "E67E22",
    trigger: "灰度发布前",
    question: "上线安全吗？",
    caps: [
      "Shadow 模式并行运行（不影响用户）",
      "Canary 小流量放量（5%-10%）",
      "Champion-Challenger 长期对照实验",
      "生产分布数据捕获"
    ]
  },
  {
    num: "④", title: "生产监控",
    analogy: "对应传统：线上监控",
    analogySub: "持续观测运行健康度",
    hc: "2C3E50", fc: "E8EDF2", qBg: "C8D0DC",
    maturity: "Trial→Adopt", mc: "8E44AD",
    trigger: "上线后持续",
    question: "在漂移吗？",
    caps: [
      "触发精度/召回率实时告警",
      "任务完成率周环比检测",
      "用户满意度信号采集",
      "输入分布漂移检测（KL散度）"
    ]
  }
];

// ── Layout constants ──
const cW   = 3.1;
const gap  = 0.14;
const totalCardsW = 4 * cW + 3 * gap; // 12.82
const sX   = (13.33 - totalCardsW) / 2; // ~0.255
const cY   = 0.65;
const cH   = 7.5 - cY - 0.12; // ~6.73

cards.forEach((card, i) => {
  const cx = sX + i * (cW + gap);

  // ── Card background ──
  slide.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cY, w: cW, h: cH,
    fill: { color: card.fc }, line: { color: "D5D8DC", width: 0.75 }
  });

  // ── Analogy tag (top gray band) ──
  const tagH = 0.40;
  slide.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cY, w: cW, h: tagH,
    fill: { color: "EBEBEB" }, line: { color: "D5D8DC", width: 0 }
  });
  // Left colored accent strip on tag
  slide.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cY, w: 0.05, h: tagH,
    fill: { color: card.hc }, line: { color: card.hc }
  });
  slide.addText(card.analogy, {
    x: cx + 0.11, y: cY + 0.02, w: cW - 0.15, h: 0.18,
    fontSize: 8, bold: true, color: "555555", fontFace: FONT,
    valign: "middle", margin: 0
  });
  slide.addText(card.analogySub, {
    x: cx + 0.11, y: cY + 0.21, w: cW - 0.15, h: 0.17,
    fontSize: 7.5, italic: true, color: "888888", fontFace: FONT,
    valign: "middle", margin: 0
  });

  // ── Stage header bar ──
  const hY = cY + tagH;
  const hH = 0.50;
  slide.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: hY, w: cW, h: hH,
    fill: { color: card.hc }, line: { color: card.hc }
  });
  slide.addText(card.num + "  " + card.title, {
    x: cx + 0.12, y: hY + 0.03, w: cW - 0.20, h: hH - 0.06,
    fontSize: 17, bold: true, color: "FFFFFF", fontFace: FONT,
    valign: "middle", margin: 0
  });

  // ── Maturity badge + trigger ──
  const mY = hY + hH + 0.10;
  // Badge background
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: cx + 0.12, y: mY, w: 1.15, h: 0.27,
    fill: { color: "FFFFFF" }, line: { color: card.mc, width: 1.2 },
    rectRadius: 0.06
  });
  slide.addText(card.maturity, {
    x: cx + 0.12, y: mY, w: 1.15, h: 0.27,
    fontSize: 8.5, bold: true, color: card.mc, fontFace: FONT,
    align: "center", valign: "middle", margin: 0
  });
  slide.addText(card.trigger, {
    x: cx + 1.34, y: mY, w: cW - 1.46, h: 0.27,
    fontSize: 8.5, color: "555555", fontFace: FONT,
    valign: "middle", margin: 0
  });

  // ── Core question highlight box ──
  const qY = mY + 0.38;
  slide.addShape(pres.shapes.RECTANGLE, {
    x: cx + 0.12, y: qY, w: cW - 0.24, h: 0.36,
    fill: { color: card.qBg }, line: { color: card.hc, width: 0.75 }
  });
  slide.addText(card.question, {
    x: cx + 0.14, y: qY + 0.02, w: cW - 0.28, h: 0.32,
    fontSize: 12, bold: true, color: card.hc, fontFace: FONT,
    align: "center", valign: "middle", margin: 0
  });

  // ── Capability section ──
  const secY = qY + 0.46;
  // Section label
  slide.addText("▌ 关键能力", {
    x: cx + 0.12, y: secY, w: cW - 0.24, h: 0.24,
    fontSize: 8.5, bold: true, color: card.hc, fontFace: FONT,
    valign: "middle", margin: 0
  });
  // Divider
  slide.addShape(pres.shapes.LINE, {
    x: cx + 0.12, y: secY + 0.27, w: cW - 0.24, h: 0,
    line: { color: "CCCCCC", width: 0.5 }
  });

  // Capability bullets
  const capY = secY + 0.34;
  const capItems = card.caps.map(text => ({
    text,
    options: { bullet: true, breakLine: true, fontSize: 9.5, color: "333333" }
  }));
  slide.addText(capItems, {
    x: cx + 0.12, y: capY, w: cW - 0.24,
    h: cH - (capY - cY) - 0.10,
    fontFace: FONT, lineSpacingMultiple: 1.3, valign: "top",
    paraSpaceAfter: 4, margin: 0
  });
});

// ── Save ──
pres.writeFile({ fileName: "skill-agent-eval-landscape.pptx" })
  .then(() => console.log("✅  Generated: skill-agent-eval-landscape.pptx"))
  .catch(e => { console.error(e); process.exit(1); });
