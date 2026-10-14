// 학위논문 초고 docx 생성 (A4, 한양대 작성방법 기준 여백·줄간격)
// 사용: node 05_논문작성/v4/gen/make_docx.js   → 05_논문작성/v4/00_학위논문_초고_통합본_v4.docx
// 입력: v4 폴더의 01~13 장별 md 파일(순서는 ORDER). 지원 문법: #~### 제목, 문단, -/1. 목록, 표, 그림, > 인용, **굵게**, *기울임*
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun, TableOfContents, Footer, PageNumber, LevelFormat,
  VerticalAlign, TableLayoutType,
} = require("docx");

const V = path.resolve(__dirname, "..");
const ORDER = [
  "01_표지_차례_국문요지_v4.md", "02_제1장_서론_v4.md", "03_제2장_관련연구_v4.md", "04_제3장_연구설계_v4.md",
  "05_제4장_금융특성의_영향_v4.md", "06_제5장_실증평가_v4.md", "07_제6장_사후보정_v4.md", "08_제7장_결론_v4.md",
  "09_참고문헌_v4.md", "10_부록A_실험절차이력_v4.md", "11_부록B_특성강도비교_v4.md", "12_부록C_종목별커버리지_v4.md",
  "13_ABSTRACT_v4.md",
];
// 일반 모드: node make_docx.js  → 통합본. 요약본 등: node make_docx.js --plain 출력.docx 입력.md
const PLAIN = process.argv[2] === "--plain";
const OUT = path.join(V, PLAIN ? process.argv[3] : "00_학위논문_초고_통합본_v4.docx");
const FILES = PLAIN ? process.argv.slice(4) : ORDER;

// 단위: DXA(1/20pt). 한양대 인공지능융합대학원 작성방법 'MS 워드 기준': A4, 여백 위아래 40mm·좌우 35mm, 머리말·꼬리말 15mm
const MM = 56.7;
const PAGE = { w: 11906, h: 16838, top: Math.round(40 * MM), bottom: Math.round(40 * MM), lr: Math.round(35 * MM), hf: Math.round(15 * MM) };
const TEXT_W = PAGE.w - 2 * PAGE.lr;
const FONT = { ascii: "Times New Roman", hAnsi: "Times New Roman", eastAsia: "바탕", cs: "Times New Roman" };
const BODY_PT = 10.5, LINE = 384; // 160%

function runs(text, base = {}) {
  // **굵게**, *기울임* 처리
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*\s][^*]*\*)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, font: FONT, ...base }));
    else out.push(new TextRun({ text: t.slice(1, -1), italics: true, font: FONT, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, ...base }));
  return out;
}

function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), data: b };
}

const thin = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const thick = { style: BorderStyle.SINGLE, size: 12, color: "000000" };
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };

function makeTable(lines) {
  const parse = (l) => l.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
  const header = parse(lines[0]);
  const body = lines.slice(2).map(parse);
  const n = header.length;
  // 열 너비: 단어가 줄 중간에서 끊기지 않도록 각 열의 최소 폭(가장 긴 단어)을 먼저 확보하고, 남는 폭을 내용 길이에 비례해 배분
  const vis = (s) => [...s.replace(/\*\*/g, "")].reduce((a, ch) => a + (/[\u3131-\uD79D]/.test(ch) ? 1.8 : /[A-Z]/.test(ch) ? 1.35 : 1), 0);
  const cols = [...Array(n).keys()].map((j) => [header[j], ...body.map((r) => r[j] || "")]);
  // \uBA38\uB9AC\uAE00\uC740 \uAD75\uC740 \uAE00\uC528\uB77C 10% \uB354 \uB113\uAC8C \uC7A1\uC74C
  const minNeed = cols.map((c) => Math.max(...c.flatMap((t, i) => t.split(/\s+/).map((w) => vis(w) * (i === 0 ? 1.05 : 1))), 2));
  const fullNeed = cols.map((c, j) => Math.max(...c.slice(1).map(vis), Math.min(vis(c[0]), 14), minNeed[j]));
  let size = n <= 5 ? 18 : n <= 8 ? 17 : 15; // half-points
  const tight = n >= 10; // 열이 많은 표는 셀 여백을 줄임
  const PAD = tight ? 80 : 140;
  let unit = () => (size / 2) * 20 * 0.56;
  while (size > 13 && minNeed.reduce((a, b) => a + b * unit() + PAD, 0) > TEXT_W) size -= 1;
  const base = minNeed.map((x) => x * unit() + PAD);
  const extra = Math.max(TEXT_W - base.reduce((a, b) => a + b, 0), 0);
  const want = fullNeed.map((x, j) => Math.max(x * unit() + PAD - base[j], 0));
  const wsum = want.reduce((a, b) => a + b, 0) || 1;
  let widths = base.map((b, j) => Math.round(b + (extra * (want[j] > 0 ? want[j] : 0)) / wsum + (wsum === 1 ? extra / n : 0)));
  const adj = TEXT_W - widths.reduce((a, b) => a + b, 0);
  widths[widths.indexOf(Math.max(...widths))] += adj;
  const mkCell = (txt, j, isHead, isLast) =>
    new TableCell({
      width: { size: widths[j], type: WidthType.DXA },
      margins: { top: 40, bottom: 40, left: tight ? 30 : 60, right: tight ? 30 : 60 },
      verticalAlign: VerticalAlign.CENTER,
      shading: isHead ? { fill: "F2F2F2", type: ShadingType.CLEAR, color: "auto" } : undefined,
      borders: {
        top: isHead ? thick : thin,
        bottom: isHead ? thin : isLast ? thick : thin,
        left: none, right: none,
      },
      children: [new Paragraph({
        alignment: j < 2 || isHead ? AlignmentType.CENTER : AlignmentType.CENTER,
        spacing: { line: 240, before: 0, after: 0 },
        keepNext: !isLast, keepLines: true,
        children: runs(txt, { size, bold: isHead || undefined }),
      })],
    });
  const rows = [
    new TableRow({ tableHeader: true, cantSplit: true, children: header.map((h, j) => mkCell(h, j, true, false)) }),
    ...body.map((r, i) => new TableRow({
      cantSplit: true,
      children: header.map((_, j) => mkCell(r[j] || "", j, false, i === body.length - 1)),
    })),
  ];
  return new Table({ width: { size: TEXT_W, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED, rows });
}

function bodyPara(text, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: LINE, before: 0, after: 120 },
    indent: opts.noIndent ? undefined : { firstLine: 200 },
    keepNext: opts.keepNext,
    children: runs(text, { size: BODY_PT * 2 }),
  });
}

// 구역: 표지(쪽 번호 없음) → 앞부분(차례·국문요지, 로마 숫자) → 본문(아라비아 숫자). --plain은 한 구역
const titleKids = [], frontKids = [], bodyKids = [];
let children = PLAIN ? bodyKids : titleKids;

function addTitlePage(lines) {
  // 양식 1(표지): 석사학위논문 16pt / 국문 제목·부제 / 영문 제목·부제 (20pt 내외) / 성명 16pt / 대학원 16pt / 학위수여 연월 16pt
  const P = (t, size, o = {}) => titleKids.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: o.before || 0, after: o.after || 120, line: Math.round(size * 10 * 1.5), lineRule: "atLeast" }, children: runs(t, { size, bold: o.bold }) }));
  const L = lines.filter((l) => l.trim() && l.trim() !== "---");
  let stage = 0;
  for (const l of L) {
    let m;
    if ((m = l.match(/^# (.*)/))) P(m[1], 40, { bold: true, before: 1700, after: 160 });
    else if ((m = l.match(/^## (.*)/))) P(m[1], 30, { after: 600 });
    else if ((m = l.match(/^### (.*)/))) P(m[1], 30, { bold: true, after: 160 });
    else if ((m = l.match(/^#### (.*)/))) P(m[1], 24, { after: 2200 });
    else { P(l.trim(), 32, { bold: stage === 0, before: stage === 0 ? 600 : 0, after: stage === 0 ? 0 : 480 }); stage++; }
  }
  // 차례(양식 4: 그림·표 차례 포함). 쪽 번호는 Word에서 열 때 필드 갱신으로 채워짐
  const tocHead = (t) => frontKids.push(new Paragraph({ pageBreakBefore: frontKids.length > 0, alignment: AlignmentType.CENTER, spacing: { after: 480 }, children: runs(t, { size: 32, bold: true }) }));
  tocHead("차 례");
  frontKids.push(new TableOfContents("차례", { hyperlink: true, headingStyleRange: "1-3" }));
  tocHead("표 차례");
  frontKids.push(new TableOfContents("표 차례", { hyperlink: true, stylesWithLevels: [{ styleName: "TableCaption", level: 1 }] }));
  tocHead("그림 차례");
  frontKids.push(new TableOfContents("그림 차례", { hyperlink: true, stylesWithLevels: [{ styleName: "FigureCaption", level: 1 }] }));
}

function processFile(file) {
  const text = fs.readFileSync(path.join(V, file), "utf8").replace(/\r/g, "");
  let lines = text.split("\n");
  if (!PLAIN && file.startsWith("01_")) {
    // 표지(첫 '---' 전까지) → 차례(md의 '# 차례' 목록은 건너뜀, 필드로 생성) → '# 국문요지'는 앞부분 구역
    const d = lines.findIndex((l) => l.trim() === "---");
    addTitlePage(lines.slice(0, d));
    lines = lines.slice(lines.findIndex((l) => l.startsWith("# 국문요지")));
    children = frontKids;
  } else if (!PLAIN && children !== bodyKids && !file.startsWith("01_")) children = bodyKids;
  const isRef = file.startsWith("09_");
  const isAbs = file.startsWith("13_");
  let i = 0;
  while (i < lines.length) {
    const l = lines[i];
    if (!l.trim() || l.trim() === "---") { i++; continue; }
    let m;
    if ((m = l.match(/^(#{1,3}) (.*)$/))) {
      const lvl = m[1].length;
      if (isAbs && lvl === 3) {
        // 양식 7: ABSTRACT 아래 영문 제목(13pt, 진하게)
        children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360, line: 300 }, children: runs(m[2], { size: 26, bold: true }) }));
        i++; continue;
      }
      const h = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][lvl - 1];
      children.push(new Paragraph({ heading: h, pageBreakBefore: lvl === 1 && !PLAIN && children.length > 0, keepNext: true, children: runs(m[2]) }));
      i++; continue;
    }
    if (l.startsWith("|")) {
      const tl = [];
      while (i < lines.length && lines[i].startsWith("|")) tl.push(lines[i++]);
      children.push(makeTable(tl));
      children.push(new Paragraph({ spacing: { after: 60 }, children: [] }));
      continue;
    }
    if ((m = l.match(/^!\[[^\]]*\]\(([^)]+)\)/))) {
      const f = path.join(V, m[1]);
      const { w, h, data } = pngSize(f);
      const wPx = Math.round((TEXT_W / 1440) * 96);
      children.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
        children: [new ImageRun({ type: "png", data, transformation: { width: wPx, height: Math.round((wPx * h) / w) } })] }));
      i++; continue;
    }
    if ((m = l.match(/^\*\*(표|그림) [A-Z0-9]+-\d+\./))) {
      const isTab = m[1] === "표";
      children.push(new Paragraph({ style: isTab ? "TableCaption" : "FigureCaption", alignment: AlignmentType.CENTER, keepNext: isTab, spacing: { before: isTab ? 200 : 0, after: isTab ? 80 : 240, line: 276 },
        children: runs(l.trim(), { size: 19 }) }));
      i++; continue;
    }
    if (l.startsWith("주:")) {
      children.push(new Paragraph({ spacing: { after: 200, line: 276 }, alignment: AlignmentType.JUSTIFIED, children: runs(l.trim(), { size: 17 }) }));
      i++; continue;
    }
    if (isAbs && l.startsWith("> ")) {
      // 양식 7: 성명·학과·대학원 (오른쪽 정렬)
      const blk = [];
      while (i < lines.length && lines[i].startsWith("> ")) blk.push(lines[i++].slice(2).trim());
      blk.forEach((t, j) => children.push(new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: j === blk.length - 1 ? 480 : 0, line: 300 }, children: runs(t, { size: 21 }) })));
      continue;
    }
    if (l.startsWith("> ")) {
      children.push(new Paragraph({ indent: { left: 400, right: 400 }, spacing: { after: 160, line: 300 },
        border: { left: { style: BorderStyle.SINGLE, size: 8, color: "999999", space: 8 } },
        children: runs(l.slice(2).trim(), { size: 19 }) }));
      i++; continue;
    }
    if ((m = l.match(/^(\s*)- (.*)$/))) {
      children.push(new Paragraph({ numbering: { reference: "bullets", level: m[1].length >= 2 ? 1 : 0 }, alignment: AlignmentType.JUSTIFIED,
        spacing: { line: LINE, after: 60 }, children: runs(m[2], { size: BODY_PT * 2 }) }));
      i++; continue;
    }
    if ((m = l.match(/^(\d+)\. (.*)$/))) {
      children.push(new Paragraph({ indent: { left: 360, hanging: 360 }, alignment: AlignmentType.JUSTIFIED, spacing: { line: LINE, after: 60 },
        children: runs(`${m[1]}. ${m[2]}`, { size: BODY_PT * 2 }) }));
      i++; continue;
    }
    if (isRef) {
      children.push(new Paragraph({ indent: { left: 480, hanging: 480 }, alignment: AlignmentType.LEFT, spacing: { line: 300, after: 120 },
        children: runs(l.trim(), { size: 20 }) }));
      i++; continue;
    }
    // 문단: 다음 줄이 표/그림 캡션이면 붙여 둠
    children.push(bodyPara(l.trim()));
    i++;
  }
}

FILES.forEach(processFile);

const doc = new Document({
  features: { updateFields: !PLAIN },
  styles: {
    default: { document: { run: { font: FONT, size: BODY_PT * 2 } } },
    paragraphStyles: [
      { id: "TableCaption", name: "TableCaption", basedOn: "Normal", next: "Normal", run: { size: 19, font: FONT } },
      { id: "FigureCaption", name: "FigureCaption", basedOn: "Normal", next: "Normal", run: { size: 19, font: FONT } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: FONT }, paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 0, after: 480 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: FONT }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: FONT }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [{ reference: "bullets", levels: [
    { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 240 } } } },
    { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 240 } } } },
  ] }] },
  sections: (PLAIN ? [[bodyKids, "decimal"]] : [[titleKids, null], [frontKids, "lowerRoman"], [bodyKids, "decimal"]]).map(([kids, fmt]) => ({
    properties: {
      page: { size: { width: PAGE.w, height: PAGE.h }, margin: { top: PAGE.top, bottom: PAGE.bottom, left: PAGE.lr, right: PAGE.lr, header: PAGE.hf, footer: PAGE.hf },
        pageNumbers: fmt ? { start: 1, formatType: fmt } : undefined },
    },
    footers: { default: new Footer({ children: fmt ? [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18 })] })] : [] }) },
    children: kids,
  })),
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT); });
