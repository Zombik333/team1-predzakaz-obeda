// Строит docx сметы из smeta_blocks.json (его пишет smeta_doc.py).
// Запуск: NODE_PATH=/opt/node-tools/node_modules node smeta_docx.js <blocks.json> <out.docx>
const fs = require('fs');
const D = require('docx');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType,
  HeadingLevel, ExternalHyperlink, Footer, PageNumber, LevelFormat, BorderStyle } = D;

const [, , inFile, outFile] = process.argv;
const B = JSON.parse(fs.readFileSync(inFile, 'utf8'));
const FONT = 'Arial', MONO = 'Consolas', WP = 9355;
const HEAD_FILL = 'DCE5EF', SUB_FILL = 'F2F5F9', NAVY = '0F2E57';

// **bold**, [text](url), `code` -> runs
function runs(text, o = {}) {
  const size = o.size || 22;
  const out = [];
  const re = /(\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\)|`[^`]+`)/g;
  let last = 0, m;
  const plain = (t, bold) => { if (t) out.push(new TextRun({ text: t, bold: bold || o.bold, size, font: FONT })); };
  while ((m = re.exec(text))) {
    plain(text.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith('**')) plain(tok.slice(2, -2), true);
    else if (tok.startsWith('`')) out.push(new TextRun({ text: tok.slice(1, -1), size, font: MONO }));
    else {
      const mm = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(tok);
      if (/^https?:/.test(mm[2])) {
        out.push(new ExternalHyperlink({ link: mm[2], children: [new TextRun({ text: mm[1], size, font: FONT, color: '1F4E99', underline: {} })] }));
      } else plain(mm[1]);
    }
    last = m.index + tok.length;
  }
  plain(text.slice(last));
  return out;
}

const para = (text, o = {}) => new Paragraph({ children: runs(text, o), spacing: { after: o.after ?? 120, line: 276 }, alignment: o.align, keepNext: o.keepNext });

function table(bl) {
  const n = bl.head.length;
  const w = bl.widths || Array(n).fill(100 / n);
  const sum = w.reduce((a, b) => a + b, 0);
  const cols = w.map(x => Math.floor(x / sum * WP));
  cols[cols.length - 1] += WP - cols.reduce((a, b) => a + b, 0);
  const size = n >= 7 ? 15 : 17;
  const border = { style: BorderStyle.SINGLE, size: 4, color: 'A6B4C8' };
  const borders = { top: border, bottom: border, left: border, right: border };
  const cell = (t, i, fill, bold) => new TableCell({
    width: { size: cols[i], type: WidthType.DXA }, borders,
    shading: fill ? { type: ShadingType.CLEAR, color: 'auto', fill } : undefined,
    margins: { top: 40, bottom: 40, left: 70, right: 70 },
    children: [new Paragraph({ children: runs(String(t), { size, bold }), spacing: { after: 0, line: 240 } })],
  });
  const rows = [new TableRow({ tableHeader: true, children: bl.head.map((t, i) => cell(t, i, HEAD_FILL, true)) })];
  bl.rows.forEach(r => {
    const sub = String(r[0]).startsWith('**') || String(r[1] || '').startsWith('**Итого');
    rows.push(new TableRow({ cantSplit: true, children: r.map((t, i) => cell(t, i, sub ? SUB_FILL : null, false)) }));
  });
  return [
    new Paragraph({ children: runs(bl.title, { size: 20, bold: true }), spacing: { before: 120, after: 80 }, keepNext: true }),
    new Table({ width: { size: WP, type: WidthType.DXA }, columnWidths: cols, rows }),
    new Paragraph({ children: [], spacing: { after: 120 } }),
  ];
}

const children = [];
let first = true, olCount = 0;
for (const bl of B) {
  if (bl.t === 'h1') {
    children.push(new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun({ text: bl.text, font: FONT, size: 34, bold: true, color: NAVY })], spacing: { after: 120 } }));
    children.push(para('Команда 1 · Software Engineering · проект «Предзаказ обеда» · версия 1, 04.11.2026', { size: 20, after: 240 }));
  } else if (bl.t === 'h2') {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: bl.text, font: FONT, size: 28, bold: true, color: NAVY })], spacing: { before: 240, after: 120 }, keepNext: true }));
    first = false;
  } else if (bl.t === 'h3') {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: bl.text, font: FONT, size: 24, bold: true, color: NAVY })], spacing: { before: 180, after: 80 }, keepNext: true }));
  } else if (bl.t === 'p') children.push(para(bl.text));
  else if (bl.t === 'ul' || bl.t === 'ol') {
    const ref = bl.t === 'ul' ? 'bul' : 'num' + (++olCount);
    bl.items.forEach(it => children.push(new Paragraph({ numbering: { reference: ref, level: 0 }, children: runs(it), spacing: { after: 80, line: 276 } })));
  } else if (bl.t === 'code') {
    const lines = bl.text.split('\n');
    lines.forEach((ln, k) => children.push(new Paragraph({
      children: [new TextRun({ text: ln, font: MONO, size: 16 })],
      shading: { type: ShadingType.CLEAR, color: 'auto', fill: SUB_FILL },
      spacing: { after: k === lines.length - 1 ? 160 : 0, line: 240 }, keepLines: true, keepNext: k < lines.length - 1,
    })));
  } else if (bl.t === 'table') children.push(...table(bl));
}

// нумерация: один маркированный список и свой нумерованный для каждого списка ol
const numConfigs = [{ reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '\u2022', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 500, hanging: 280 } } } }] }];
for (let k = 1; k <= olCount; k++) numConfigs.push({ reference: 'num' + k, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 500, hanging: 360 } } } }] });

const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: 'Title', name: 'Title', basedOn: 'Normal', run: { font: FONT, size: 34, bold: true, color: NAVY }, paragraph: { spacing: { before: 0, after: 120 }, keepNext: true } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', run: { font: FONT, size: 28, bold: true, color: NAVY }, paragraph: { spacing: { before: 240, after: 120 }, keepNext: true, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', run: { font: FONT, size: 24, bold: true, color: NAVY }, paragraph: { spacing: { before: 180, after: 80 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: numConfigs },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1701, right: 850 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, font: FONT })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(outFile, buf); console.log('docx ok', outFile); });
