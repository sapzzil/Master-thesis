// 학위논문 초고 docx 생성 (A4, 한양대 작성방법 기준 여백·줄간격)
// 사용: node 05_논문작성/v4/gen/make_docx.js [출력.docx]   (기본 석사학위논문_초고_김승민.docx)
// 입력: v4 폴더의 01~13 장별 md 파일(순서는 ORDER). 지원 문법: #~### 제목, 문단, -/1. 목록, 표, 그림, > 인용, **굵게**, *기울임*
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun, TableOfContents, Footer, PageNumber, LevelFormat,
  VerticalAlign, TableLayoutType, HeightRule, Tab, TabStopType,
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
const OUT = path.join(V, PLAIN ? process.argv[3] : process.argv[2] || "석사학위논문_초고_김승민.docx");
const FILES = PLAIN ? process.argv.slice(4) : ORDER;

// 단위: DXA(1/20pt). 한양대 인공지능융합대학원 작성방법 'MS 워드 기준': A4, 여백 위아래 40mm·좌우 35mm, 머리말·꼬리말 15mm
const MM = 56.7;
// 요약본(--plain)은 학위논문 양식이 아니므로 일반 문서 여백(상하·좌우 25mm)
const PAGE = PLAIN
  ? { w: 11906, h: 16838, top: Math.round(25 * MM), bottom: Math.round(25 * MM), lr: Math.round(25 * MM), hf: Math.round(12 * MM) }
  : { w: 11906, h: 16838, top: Math.round(40 * MM), bottom: Math.round(40 * MM), lr: Math.round(35 * MM), hf: Math.round(15 * MM) };
const TEXT_W = PAGE.w - 2 * PAGE.lr;
const FONT = { ascii: "바탕", hAnsi: "바탕", eastAsia: "바탕", cs: "바탕" }; // 작성요령(한글 프로그램 기준 글씨체를 Word에 준용): 본문은 영문·숫자까지 바탕
const TFONT = { ascii: "굴림", hAnsi: "굴림", eastAsia: "굴림", cs: "굴림" }; // 표 안 글자는 굴림(본문과 구분)
const BODY_PT = PLAIN ? 10.5 : 11, LINE = 384; // 160%. 본문 11pt(작성요령: 10 또는 11pt). 요약본은 학위논문 양식 대상이 아니므로 10.5pt 유지
// 언어: 한글을 한국어(ko-KR)로 지정해야 Word가 한국어 줄바꿈 규칙(어절 단위)을 적용함.
// 지정이 없으면 동아시아 문자를 중국어·일본어처럼 글자 단위로 끊을 수 있음
const LANG = { value: "en-US", eastAsia: "ko-KR" };

// 인라인 서식: **굵게**, *기울임*, `코드`(백틱 제거, 고정폭), 아래첨자 x_{t+1}·x_t (기호 제거 후 실제 아래첨자)
const MONO = FONT; // 코드 표기도 같은 글꼴로 통일
function subRuns(text, opt) {
  // 아래첨자(_x, _{…})와 위첨자(^{…})를 찾아 조각으로 나눔. 중괄호 안의 중첩 표기(σ_{S_t})는 기호만 지우고 모두 아래첨자
  const out = [];
  const re = /_\{((?:[^{}]|\{[^{}]*\})*)\}|_([A-Za-z0-9ν]+)|\^\{((?:[^{}]|\{[^{}]*\})*)\}/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    const prev = text[m.index - 1] || "";
    const isSup = m[3] !== undefined;
    // 아래첨자는 앞 글자가 변수·기호일 때만 (파일명 등 일반 밑줄 제외)
    if (!isSup && !/[A-Za-zͰ-Ͽ²)\]∫Σ̂]/.test(prev)) continue;
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...opt }));
    if (isSup) out.push(new TextRun({ text: m[3].replace(/_\{?|\}/g, ""), superScript: true, ...opt }));
    else out.push(new TextRun({ text: (m[1] !== undefined ? m[1] : m[2]).replace(/_\{?|\}/g, ""), subScript: true, ...opt }));
    last = m.index + m[0].length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...opt }));
  return out;
}

function runs(text, base = {}) {
  const out = [];
  const re = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*\s][^*]*\*)/g;
  let last = 0, m;
  const plain = (t, extra = {}) => out.push(...subRuns(t, { font: FONT, language: LANG, ...base, ...extra }));
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) plain(text.slice(last, m.index));
    const t = m[0];
    if (t.startsWith("`")) out.push(new TextRun({ text: t.slice(1, -1), font: MONO, ...base, size: base.size ? base.size - 1 : undefined }));
    else if (t.startsWith("**")) plain(t.slice(2, -2), { bold: true });
    else plain(t.slice(1, -1), { italics: true });
    last = m.index + t.length;
  }
  if (last < text.length) plain(text.slice(last));
  return out;
}

// 제목처럼 줄을 지정해 나눠야 하는 곳: <br>에서 줄바꿈(같은 문단 안)
function brRuns(text, base = {}) {
  return text.split(/<br>/i).flatMap((sg, k) => (k ? [new TextRun({ break: 1 }), ...runs(sg, base)] : runs(sg, base)));
}

function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), data: b };
}

const thin = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const thick = { style: BorderStyle.SINGLE, size: 12, color: "000000" };
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };

// 표별 추가 설정(표 번호 기준): equal = 너비를 같게 맞출 열, wide = 남는 폭을 더 받을 열(0부터 셈)
const TABLE_OPTS = { "3-4": { equal: [1, 2] }, "3-7": { wide: [4] }, "4-4": { keep: [9] }, "7-1": { wide: [2] } }; // keep = 늘 한 줄로 둘 열
function makeTable(lines, keepLast = false, tno = "") {
  const topt = TABLE_OPTS[tno] || {};
  const parse = (l) => l.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
  // 긴 머리글은 괄호 앞에서 두 줄로 나눔(괄호 안에서 어색하게 끊기지 않도록)
  const header = parse(lines[0]).map((h) => (/<br>/i.test(h) || [...h].length <= 9 ? h : h.replace(/ ([(\[])/, "<br>$1")));
  const body = lines.slice(2).map(parse);
  // 구분선의 ':---'(왼쪽 맞춤)은 서술형 열 → 본문 칸을 왼쪽 정렬. 그 밖은 가운데 정렬
  // 정렬 규칙: 머리글은 가운데. 본문은 열 성격으로 정함
  //  - 숫자·기호 열(값, ○×△, 〃, →, 17/17 등)과 짧은 범주 값 열(판정·가설 번호 등, 평균 6자 이하)은 가운데
  //  - 그 밖의 글자 열(모델·조건·항목 같은 이름 열, 설명 열)은 왼쪽
  //  - 구분선에 ':---'는 왼쪽, ':---:'는 가운데로 강제
  const sepCells = parse(lines[1]);
  const symOnly = (t) => /^[\s○×△✕〃\-–·→/]*$/.test(t);
  const numLike = (t) => { const c = t.replace(/\*\*|<br>/gi, " ").replace(/\([^)]*\)/g, "").trim(); /* 괄호 속 보충 설명은 무시 */ return c === "" || symOnly(c) || (/\d/.test(c) && !/[\u3131-\uD79D]{2,}/.test(c) && !/[A-Za-z]{3,}/.test(c)); };
  const leftCol = sepCells.map((c, j) => {
    if (/^:-+$/.test(c)) return true;
    if (/^:-+:$/.test(c)) return false;
    const cells = body.map((r) => (r[j] || "").trim()).filter((x) => x && x !== "-");
    if (!cells.length) return false;
    const numShare = cells.filter(numLike).length / cells.length;
    if (numShare >= 0.6) return false;
    const avgLen = cells.reduce((a, x) => a + [...x.replace(/\*\*|<br>/gi, "")].length, 0) / cells.length;
    return j < 2 ? avgLen > 3 : avgLen > 6;
  });
  const n = header.length;
  // 열 너비 계산(근사 글자 폭: 한글 1em, 영문 대문자 0.76em, 그 밖 0.56em)
  // 원칙: ① 단어(어절)가 셀 안에서 쪼개지지 않게 각 열의 가장 긴 어절 폭을 확보
  //       ② 1·2열(모델·조건·항목 등), 숫자 셀, 짧은 셀은 내용 전체를 한 줄로(띄어쓰기를 줄바꿈 없는 공백으로 바꾸고 폭 확보)
  //       ③ 남는 폭은 내용 길이에 비례해 배분
  const clean = (s) => s.replace(/\*\*|`/g, "").replace(/_\{|\}/g, "").replace(/_/g, "");
  const vis = (s) => [...clean(s)].reduce((a, ch) => a + (/[ㄱ-힝]/.test(ch) ? 1.9 : /[A-Z]/.test(ch) ? 1.35 : 1), 0);
  const isNum = (t) => /^[-+−0-9.,%\[\]()→ ✕○~×e/]+$/.test(clean(t).trim()) && /\d/.test(t);
  const segs = (t) => t.split(/<br>/i);
  const cols = [...Array(n).keys()].map((j) => [header[j], ...body.map((r) => r[j] || "")]);
  // 한 줄 유지 우선순위: 0단계 = 1·2열 + 숫자 셀 + 머리글 각 줄, 1단계 = 머리글은 어절 단위 허용, 2단계 = 1·2열도 어절 단위 허용
  let lv = 0;
  const unitOf = (sz) => (sz / 2) * 20 * 0.56;
  const SZ0 = n <= 5 ? 18 : n <= 8 ? 17 : 16; // half-points
  // 1·2열은 내용이 짧은 경우(가장 긴 셀이 본문 폭의 30% 이하)에만 한 줄 고정 대상
  const shortCol = cols.map((c, j) => j < 2 && Math.max(...c.slice(1).map(vis)) * unitOf(SZ0) + 140 <= 0.3 * TEXT_W);
  const keepWhole = (t, j, i) => ((topt.keep || []).includes(j) && i > 0) || (i === 0 ? lv === 0 || (shortCol[j] && lv < 2) : (shortCol[j] ? lv < 2 : isNum(t) || (lv < 2 && vis(t) <= 16)));
  const tight = n >= 9;
  const PAD = tight ? 90 : 140;
  const need = () => cols.map((c, j) => Math.max(2, ...c.flatMap((t, i) => segs(t).flatMap((sg) =>
    (keepWhole(sg, j, i) ? [sg] : sg.split(/\s+/)).map((w) => vis(w) * (i === 0 ? 1.05 : 1))))));
  let minNeed, size;
  const fits = () => minNeed.reduce((a, b) => a + b * unitOf(size) + PAD, 0) <= TEXT_W;
  for (lv = 0; lv <= 2; lv++) {
    minNeed = need(); size = SZ0;
    while (!fits() && size > (lv < 2 ? 16 : 15)) size -= 1;
    if (fits()) break;
  }
  if (lv > 2) { lv = 2; minNeed = need(); while (!fits() && size > 14) size -= 1; }
  const unit = () => unitOf(size);
  const fullNeed = cols.map((c, j) => Math.max(...c.slice(1).flatMap((t) => segs(t).map(vis)), ...segs(c[0]).map((x) => vis(x) * 1.05), minNeed[j]));
  const base = minNeed.map((x) => x * unit() + PAD);
  const extra = Math.max(TEXT_W - base.reduce((a, b) => a + b, 0), 0);
  const want = fullNeed.map((x, j) => Math.max(x * unit() + PAD - base[j], 0) * ((topt.wide || []).includes(j) ? 2.5 : 1));
  const wsum = want.reduce((a, b) => a + b, 0) || 1;
  let widths = base.map((b, j) => Math.round(b + (extra * (want[j] > 0 ? want[j] : 0)) / wsum + (wsum === 1 ? extra / n : 0)));
  const adj = TEXT_W - widths.reduce((a, b) => a + b, 0);
  widths[widths.indexOf(Math.max(...widths))] += adj;
  if (topt.equal) { const av = Math.round(topt.equal.reduce((a, j) => a + widths[j], 0) / topt.equal.length); topt.equal.forEach((j) => (widths[j] = av)); widths[0] += TEXT_W - widths.reduce((a, b) => a + b, 0); }
  const nb = (t, j, i) => (keepWhole(t, j, i) ? t.replace(/ /g, "\u00A0") : t);
  const mkCell = (txt, j, isHead, isLast) =>
    new TableCell({
      width: { size: widths[j], type: WidthType.DXA },
      margins: { top: 40, bottom: 40, left: tight ? 28 : 50, right: tight ? 28 : 50 },
      verticalAlign: VerticalAlign.CENTER,
      shading: isHead ? { fill: "F2F2F2", type: ShadingType.CLEAR, color: "auto" } : undefined,
      borders: {
        top: isHead ? thick : thin,
        bottom: isHead ? thin : isLast ? thick : thin,
        left: none, right: none,
      },
      children: segs(txt).map((sg) => new Paragraph({
        alignment: !isHead && leftCol[j] ? AlignmentType.LEFT : AlignmentType.CENTER,
        spacing: { line: 240, before: 0, after: 0 },
        keepNext: !isLast || keepLast, keepLines: true, wordWrap: true,
        children: runs(nb(sg, j, isHead ? 0 : 1), { size, bold: isHead || undefined, font: TFONT }),
      })),
    });
  // 본문 행 높이 통일: 칸마다 필요한 줄 수를 추정해 가장 많은 줄 수에 모든 행을 맞춤(atLeast라 더 필요하면 늘어남)
  const mar = tight ? 56 : 100;
  const cellLines = (t, j) => segs(t).reduce((a, sg) => a + Math.max(1, Math.ceil((vis(sg) * unit() * 1.02) / Math.max(widths[j] - mar, 200))), 0);
  const maxLines = Math.max(1, ...body.map((r) => Math.max(...header.map((_, j) => cellLines(r[j] || "", j)))));
  const rowH = Math.round(maxLines * size * 12 + 80);
  const rows = [
    new TableRow({ tableHeader: true, cantSplit: true, children: header.map((h, j) => mkCell(h, j, true, false)) }),
    ...body.map((r, i) => new TableRow({
      cantSplit: true, height: { value: rowH, rule: "atLeast" },
      children: header.map((_, j) => mkCell(r[j] || "", j, false, i === body.length - 1)),
    })),
  ];
  return new Table({ width: { size: TEXT_W, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED, rows });
}

function bodyPara(text, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: LINE, before: 0, after: opts.compact ? 0 : 120 },
    indent: opts.noIndent ? undefined : { firstLine: Math.round(BODY_PT * 20) }, // 문단 시작 2칸(공백 2개 ≈ 한 글자 폭)
    keepNext: opts.keepNext, widowControl: true,
    children: runs(text, { size: BODY_PT * 2 }),
  });
}

// 구역: 표지(쪽 번호 없음) → 앞부분(차례·국문요지, 로마 숫자) → 본문(아라비아 숫자). --plain은 한 구역
const titleKids = [], frontKids = [], bodyKids = [];
let children = PLAIN ? bodyKids : titleKids;

// 부제 앞뒤의 줄표(- … -)가 줄 끝·줄 머리에 홀로 떨어지지 않게 붙임
const nbDash = (t) => t.replace(/^- /, "-\u00A0").replace(/ -$/, "\u00A0-");
function addTitlePage(lines) {
  // 양식 1(표지, 제본 후 B5 기준 치수): 위에서 2cm 석사학위논문(16pt) → 3cm → 국문 제목·부제, 영문 제목·부제(20pt 내외)
  // … 성명(16pt) → 3.5cm → 대학원(16pt) → 3cm → 학위수여 연월(16pt) → 아래 2cm.
  // A4 편집 시 위·아래 여백(4cm)이 B5의 2cm에 해당하므로, 첫 줄은 본문 영역 맨 위, 연월은 본문 영역 맨 아래에 둔다.
  // 아래 묶음(성명~연월)은 위 묶음 길이와 무관하게 바닥에 붙도록, 테두리 없는 2행 표의 둘째 행에 넣는다.
  const CM = 567;
  const para = (t, size, o = {}) => new Paragraph({ alignment: AlignmentType.CENTER,
    spacing: { before: o.before || 0, after: 0, line: Math.round(size * 10 * 1.5), lineRule: "exact" }, children: brRuns(t, { size, bold: o.bold }) });
  const L = lines.filter((l) => l.trim() && l.trim() !== "---");
  const top = [], bottom = [];
  let stage = 0;
  for (const l of L) {
    let m;
    if ((m = l.match(/^# (.*)/))) top.push(para(m[1], 36, { bold: true, before: 3 * CM })); // 국문 제목 18pt(양식: 20pt 내외), 콜론 뒤에서 줄바꿈
    else if ((m = l.match(/^## (.*)/))) top.push(para(nbDash(m[1]), 28, { before: 120 })); // 국문 부제 14pt
    else if ((m = l.match(/^### (.*)/))) top.push(para(m[1], 28, { bold: true, before: 600 })); // 영문 제목 14pt(바탕 영문 폭이 넓어 아래 묶음과 겹치지 않게)
    else if ((m = l.match(/^#### (.*)/))) top.push(para(nbDash(m[1]), 22, { before: 120 }));
    else if (stage === 0) { top.push(para(l.trim(), 32)); stage++; } // 석사학위논문
    else { bottom.push(para(l.trim(), 32, { before: stage === 1 ? 0 : stage === 2 ? Math.round(3.5 * CM) - 160 : 3 * CM - 160 })); stage++; }
  }
  const textH = PAGE.h - PAGE.top - PAGE.bottom;
  const bottomH = 3 * 480 + Math.round(3.5 * CM) - 160 + 3 * CM - 160;
  const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const nb = { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
  const cell = (kids) => new TableCell({ children: kids, borders: { top: none, bottom: none, left: none, right: none },
    margins: { top: 0, bottom: 0, left: 0, right: 0 }, width: { size: TEXT_W, type: WidthType.DXA } });
  titleKids.push(new Table({ width: { size: TEXT_W, type: WidthType.DXA }, columnWidths: [TEXT_W], borders: nb, layout: TableLayoutType.FIXED,
    rows: [new TableRow({ height: { value: textH - bottomH - 200, rule: HeightRule.ATLEAST }, cantSplit: true, children: [cell(top)] }),
           new TableRow({ cantSplit: true, children: [cell(bottom)] })] }));
  titleKids.push(new Paragraph({ spacing: { before: 0, after: 0, line: 20, lineRule: "exact" }, children: [new TextRun({ text: "", size: 2 })] })); // 표 뒤 필수 문단(빈 쪽 방지)
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
  // 국문요지·ABSTRACT는 각 2쪽 이내 규정 → 문단 뒤 간격을 줄여 한 쪽 안에 여유 있게
  const compact = !PLAIN && (file.startsWith("01_") || isAbs);
  let lastTab = "";
  // 쪽 끝에서 잘림 방지: 다음에 오는 덩어리 종류를 미리 보고, 도입 문장·목록·표 주석이 뒤 내용과 떨어지지 않게 함
  const kindAt = (j) => {
    while (j < lines.length && (!lines[j].trim() || lines[j].trim() === "---")) j++;
    if (j >= lines.length) return "end";
    const t = lines[j];
    if (/^#{1,6} /.test(t)) return "heading";
    if (t.startsWith("|")) return "table";
    if (/^!\[/.test(t)) return "image";
    if (/^\*\*(표|그림) [A-Z0-9]+-\d+\./.test(t)) return "caption";
    if (t.startsWith("주:")) return "note";
    if (/^(\s*)- /.test(t) || /^\d+\. /.test(t)) return "list";
    return "para";
  };
  const attach = (k) => ["list", "table", "caption", "image"].includes(k);
  let i = 0;
  while (i < lines.length) {
    const l = lines[i];
    if (!l.trim() || l.trim() === "---") { i++; continue; }
    let m;
    if ((m = l.match(/^(#{1,3}) (.*)$/))) {
      const lvl = m[1].length;
      if (isAbs && lvl === 3) {
        // 양식 7: ABSTRACT 아래 영문 제목(13pt, 진하게)
        children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360, line: 300 }, children: brRuns(m[2], { size: 26, bold: true }) }));
        i++; continue;
      }
      if (lvl === 2 && !PLAIN && /^[A-Z]\.\d/.test(m[2])) {
        // 부록 A.1 등: 본문 모양은 절 제목과 같게, 차례에서는 한 단계 더 들여쓰도록 제목 3 수준으로 둠
        children.push(new Paragraph({ heading: HeadingLevel.HEADING_3, keepNext: true, spacing: { before: 360, after: 160 }, children: brRuns(m[2], { size: 26, bold: true }) }));
        i++; continue;
      }
      const h = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][lvl - 1];
      children.push(new Paragraph({ heading: h, pageBreakBefore: lvl === 1 && !PLAIN && children.length > 0, keepNext: true, children: runs(m[2]) }));
      i++; continue;
    }
    if ((m = l.match(/^\$\$\s*(.+?)\s*\$\$\s*(\(\d+\.\d+\))?\s*$/))) {
      // 수식 줄: 가운데 정렬, 수식 번호는 오른쪽 끝
      const kids = [new TextRun({ children: [new Tab()], font: FONT }), ...subRuns(m[1], { font: FONT, language: LANG, size: BODY_PT * 2 })];
      if (m[2]) kids.push(new TextRun({ children: [new Tab(), m[2]], font: FONT, size: BODY_PT * 2 }));
      children.push(new Paragraph({ tabStops: [{ type: TabStopType.CENTER, position: Math.round(TEXT_W / 2) }, { type: TabStopType.RIGHT, position: TEXT_W }],
        spacing: { before: 120, after: 120, line: 300 }, keepLines: true, children: kids }));
      i++; continue;
    }
    if (l.startsWith("|")) {
      const tl = [];
      while (i < lines.length && lines[i].startsWith("|")) tl.push(lines[i++]);
      children.push(makeTable(tl, kindAt(i) === "note", lastTab));
      children.push(new Paragraph({ spacing: { after: 60 }, children: [] }));
      continue;
    }
    if ((m = l.match(/^!\[[^\]]*\]\(([^)]+)\)/))) {
      const f = path.join(V, m[1]);
      const { w, h, data } = pngSize(f);
      const fullPx = Math.round((TEXT_W / 1440) * 96);
      // 요약본: 여백을 자른 그림을 본문 폭에 맞추되, 세로로 긴 그림은 높이를 본문 폭의 0.62배로 제한
      const wPx = PLAIN ? Math.min(fullPx, Math.round((fullPx * 0.62 * w) / h)) : fullPx;
      children.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: kindAt(i + 1) === "caption", spacing: { before: 120, after: 60 },
        children: [new ImageRun({ type: "png", data, transformation: { width: wPx, height: Math.round((wPx * h) / w) } })] }));
      i++; continue;
    }
    if ((m = l.match(/^\*\*(표|그림) ([A-Z0-9]+-\d+)\./))) {
      const isTab = m[1] === "표";
      if (isTab) lastTab = m[2];
      // 캡션은 제목(첫 문장)만 캡션 스타일로 두어 표·그림 차례에 제목만 실리게 하고, 뒤 설명은 별도 문단
      const full = l.trim().replace(/\*\*/g, "");
      const pre = full.match(/^(표|그림) [A-Z0-9]+-\d+\. /)[0];
      const k = full.indexOf(". ", pre.length);
      const title = k > 0 ? full.slice(0, k) : full.replace(/\.$/, "");
      const desc = k > 0 ? full.slice(k + 2).trim() : "";
      children.push(new Paragraph({ style: isTab ? "TableCaption" : "FigureCaption", alignment: AlignmentType.CENTER, keepNext: isTab || !!desc, spacing: { before: isTab ? 200 : 0, after: desc ? 40 : isTab ? 80 : 240, line: 276 },
        children: runs(title, { size: 19 }) }));
      if (desc) children.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: isTab, spacing: { after: isTab ? 80 : 240, line: 276 }, children: runs(desc, { size: 17 }) }));
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
    // 목록: 짧으면 한 덩어리로 같은 쪽에 둠
    let listKeep = false;
    if (/^(\s*)- /.test(l) || /^\d+\. /.test(l)) {
      let a = i, b = i;
      while (a > 0 && (/^(\s*)- /.test(lines[a - 1]) || /^\d+\. /.test(lines[a - 1]) || (!lines[a - 1].trim() && a > 1 && (/^(\s*)- /.test(lines[a - 2]) || /^\d+\. /.test(lines[a - 2]))))) a--;
      while (b + 1 < lines.length && kindAt(b + 1) === "list" && (lines[b + 1].trim() ? true : true)) { let c = b + 1; while (c < lines.length && !lines[c].trim()) c++; if (!(/^(\s*)- /.test(lines[c]) || /^\d+\. /.test(lines[c]))) break; b = c; }
      const items = lines.slice(a, b + 1).filter((x) => x.trim());
      const chars = items.reduce((t, x) => t + x.length, 0);
      const last = kindAt(i + 1) !== "list";
      // 짧은 목록(8항목·600자 이하)은 통째로, 긴 목록은 첫 항목만 앞 문장과 붙이고 나머지는 자연스럽게 넘김
      listKeep = last ? attach(kindAt(i + 1)) : (items.length <= 8 && chars <= 900) || i === a;
    }
    if ((m = l.match(/^(\s*)- (.*)$/))) {
      children.push(new Paragraph({ numbering: { reference: "bullets", level: m[1].length >= 2 ? 1 : 0 }, alignment: AlignmentType.JUSTIFIED,
        keepNext: listKeep, keepLines: true, widowControl: true, spacing: { line: LINE, after: 60 }, children: runs(m[2], { size: BODY_PT * 2 }) }));
      i++; continue;
    }
    if ((m = l.match(/^(\d+)\. (.*)$/))) {
      children.push(new Paragraph({ indent: { left: 360, hanging: 360 }, alignment: AlignmentType.JUSTIFIED, keepNext: listKeep, keepLines: true, widowControl: true, spacing: { line: LINE, after: 60 },
        children: runs(`${m[1]}. ${m[2]}`, { size: BODY_PT * 2 }) }));
      i++; continue;
    }
    if (isRef) {
      children.push(new Paragraph({ indent: { left: 480, hanging: 480 }, alignment: AlignmentType.LEFT, spacing: { line: 300, after: 120 },
        children: runs(l.trim(), { size: 20 }) }));
      i++; continue;
    }
    // 문단: 뒤에 목록·표·그림이 오거나 ':'로 끝나는 도입 문장이면 다음 덩어리와 같은 쪽에 둠
    // 주제어·Keywords 줄은 바로 앞 문단과 같은 쪽에
    const nextLine = (lines.slice(i + 1).find((x) => x.trim()) || "").trim();
    children.push(bodyPara(l.trim(), { compact, keepNext: attach(kindAt(i + 1)) || /[:：]$/.test(l.trim()) || (compact && /^(주제어|Keywords)/.test(nextLine)) }));
    i++;
  }
}

FILES.forEach(processFile);

const doc = new Document({
  creator: "김승민", lastModifiedBy: "김승민",
  title: PLAIN ? "석사학위논문 초고 요약" : "사전학습 시계열 모델의 금융 수익률 예측구간: 오차의 출처와 재학습 없는 사후보정",
  features: { updateFields: !PLAIN },
  styles: {
    default: { document: { run: { font: FONT, size: BODY_PT * 2, language: LANG }, paragraph: { wordWrap: true, widowControl: true } } }, // 줄바꿈 단위 속성. 라이브러리는 0(단어 중간 끊기 허용)만 쓰므로 gen/postfix.py가 1(어절 단위)로 바꿈
    paragraphStyles: [
      { id: "TableCaption", name: "TableCaption", basedOn: "Normal", next: "Normal", run: { size: 19, bold: true, font: FONT } },
      { id: "FigureCaption", name: "FigureCaption", basedOn: "Normal", next: "Normal", run: { size: 19, bold: true, font: FONT } },
      { id: "TOC1", name: "toc 1", basedOn: "Normal", next: "Normal", paragraph: { spacing: { before: 160, after: 40 } }, run: { size: 21 } },
      { id: "TOC2", name: "toc 2", basedOn: "Normal", next: "Normal", paragraph: { spacing: { before: 0, after: 40 }, indent: { left: 300 } }, run: { size: 21 } },
      { id: "TOC3", name: "toc 3", basedOn: "Normal", next: "Normal", paragraph: { spacing: { before: 0, after: 40 }, indent: { left: 600 } }, run: { size: 21 } },
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
