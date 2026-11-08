"""Build the Thai paper in arXiv preprint layout -> paper/pdf/paper_th.pdf.

paper_th.md is the manuscript. Its body is converted to LaTeX by pandoc and set in paper/template_th.tex, the
same page, title block and headings as the English paper (paper/en/main.tex); tectonic (XeTeX) compiles it with
Times for Latin text and Sarabun (paper/fonts/) for Thai. The 11 figures come from figures.py: their shapes are
converted from SVG to PDF by svglib and their labels are set by XeTeX on top. Build files go to paper/figs_th/
(paper_th.tex is the generated source).

Requires pandoc, tectonic and svglib (in the paper extra). Usage: python paper/build_th.py
"""
import json
import os
import re
import shutil
import subprocess

import figures

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
BUILD = 'figs_th'
os.makedirs('pdf', exist_ok=True)
figures.write_all(BUILD)

AUTHOR = 'ธนัชชนม์ จงมั่นคง'
DATE = '7 พฤศจิกายน 2026'
TITLE = 'การยกเลิกธนบัตร 1,000 บาทเพื่อปราบทุนเทา–ทุนดำ'
SUBTITLE = 'บทเรียนนานาชาติ แบบจำลองเชิงนโยบาย และวาระการวิจัยสำหรับประเทศไทย'
RUNNING_HEAD = 'การยกเลิกธนบัตร 1,000 บาทเพื่อปราบทุนเทา–ทุนดำ'
THANKS = ('ร่างเพื่อการอภิปราย ตัวเลขทั้งหมดเป็นค่าประมาณที่ต้องตรวจทานกับแหล่งปฐมภูมิ โดยเฉพาะสถิติธนบัตรออกใช้ของ'
          'ธนาคารแห่งประเทศไทย พารามิเตอร์ของแบบจำลองเป็นสมมติฐาน และไม่ได้ใช้แหล่งข้อมูลออนไลน์ '
          'รายการอ้างอิงรวบรวมโดยไม่ได้ค้นฐานข้อมูลและต้องตรวจสอบรายละเอียดบรรณานุกรม ผู้เขียนใช้ AI (Claude, '
          'Anthropic) ช่วยร่าง เขียนโค้ด และออกแบบภาพ ฉบับภาษาอังกฤษ: \\textit{Can Demonetization Defeat Grey '
          'Capital?} โค้ดสำหรับทำซ้ำ: \\texttt{demonet\\_sim\\_th.py} (seed 7), '
          '\\url{https://github.com/thanatchon36/demonetsim-th}')
ABSTRACT = [
    'งานนี้ประเมินข้อเสนอยกเลิกธนบัตร 1,000 บาทเพื่อปราบทุนเทา ทุนดำ การซื้อเสียง และคอร์รัปชัน โดยทบทวน 12 '
    'กรณีต่างประเทศ วัดมูลค่าแบงก์พันเทียบรายได้ และสร้างแบบจำลอง \\textit{DemonetSim-TH} ที่ปรับเทียบกับอินเดีย 2016 '
    'ด้วยวิธี ABC',
    'แบงก์พันมีค่าเพียง 0.38\\% ของรายได้ต่อหัว ราวหนึ่งในสี่ของ €500 ในแบบจำลอง การยกเลิกแบบช็อกทำลายหรือยึด'
    'เงินผิดกฎหมายได้ราว 8\\% (มัธยฐาน) แต่ทำให้เศรษฐกิจสะดุดราว 1 ใน 6 ของอินเดีย และราว 90\\% ของภาระตกกับ'
    'กลุ่มเปราะบาง เงินผิดกฎหมายส่วนใหญ่เข้าระบบโดยไม่ถูกตรวจพบ หรือย้ายไปอยู่ในทอง ดอลลาร์ และคริปโต',
    'ตัวแปรชี้ขาดคือความจุของเครือข่ายฟอกเงิน ไม่ใช่ความเข้มงวดของการตรวจ การทยอยเลิกควบคู่ชุดมาตรการ AML '
    'ได้ผลราว 6\\% โดยไม่กระทบสภาพคล่อง งานนี้เสนอวาระวิจัย 15 หัวข้อ โดยมีหัวข้อเรือธง 3 เรื่องที่ทดสอบได้ว่า'
    'แบงก์พันเป็นสื่อหลักของเงินผิดกฎหมายจริงหรือไม่',
]
KEYWORDS = ['การยกเลิกธนบัตร', 'ทุนเทา', 'การฟอกเงิน', 'เงินสด', 'แบบจำลองตัวแทน', 'ประเทศไทย']
JEL = ['E41', 'E42', 'E58', 'H26', 'K42', 'O17', 'C63']

CAPTIONS = {
    1: 'ข้อเสนอเชิงแนวคิดของงานนี้: 3 เป้าหมายที่ขัดกันเอง และ 3 รูปแบบนโยบาย',
    2: 'มูลค่าธนบัตรใบใหญ่เทียบ GDP ต่อหัว · ที่มา: denomination_metrics() ใน demonet_sim_th.py · GDP ต่อหัวและอัตราแลกเปลี่ยนเป็นค่าประมาณ',
    3: 'น้ำหนักและปริมาตรของเงิน 10 ล้านบาท · ที่มา: bulk_table() · ธนบัตรหนักราว 1 กรัมต่อใบ หนา 0.11 มม.',
    4: 'ต้นทุนทางเศรษฐกิจเทียบผลต่อเงินผิดกฎหมาย · ที่มา: DemonetSim-TH (scenario_summary.csv) · seed 7, 600 รอบต่อสถานการณ์ · ผลจากสมมติฐาน ไม่ใช่การพยากรณ์',
    5: 'ชะตากรรมของเงินผิดกฎหมายแยกตามสถานการณ์ · ที่มา: DemonetSim-TH (mc_results.csv) · อินเดียใช้เฉพาะรอบที่ผ่าน ABC',
    6: 'การปรับเทียบกับอินเดีย 2016 · ที่มา: DemonetSim-TH (india_calibration_curve.csv) · 4,000 รอบ · ตัวเลข 99.3% จาก RBI Annual Report 2017–18',
    7: 'ความไวของผลต่อความจุของเครือข่ายฟอกเงิน · ที่มา: DemonetSim-TH (sensitivity_s1.csv) · 80 รอบต่อจุด',
    8: 'ข้อดีและข้อเสียตามขนาดผลกระทบและความแข็งแรงของหลักฐาน · การประเมินเชิงคุณภาพของผู้เขียน (ตารางที่ 8)',
    9: 'Scorecard ทางเลือกนโยบาย · การให้คะแนนของผู้เขียน · ง = AML และเพดานเงินสดโดยไม่ยกเลิกธนบัตร',
    10: 'Roadmap หากจะยกเลิกแบงก์พัน · ข้อเสนอของผู้เขียน · 4 ระยะ 3 ด่าน',
    11: 'แผนที่วาระการวิจัย · การประเมินของผู้เขียน (ตารางที่ 9) · 15 หัวข้อ',
}

# ---------------------------------------------------------------------------------------------- figures
# figures.py draws each figure as SVG shapes plus a list of text labels in SVG units (760 wide). svglib turns the
# shapes into figN_shapes.pdf; the labels are set by XeTeX in a picture environment on top, so Thai is shaped by
# the same engine and font as the text.
TEXTWIDTH_PT = 469.755  # 6.5 in: letter paper with 1 in margins
UNIT = TEXTWIDTH_PT / 760


def figure_shapes(n):
    from reportlab.graphics import renderPDF
    from svglib.svglib import svg2rlg

    renderPDF.drawToFile(svg2rlg(f'{BUILD}/fig{n}.svg'), f'{BUILD}/fig{n}_shapes.pdf')


def figure_overlay(n):
    meta = json.load(open(f'{BUILD}/fig{n}.json', encoding='utf-8'))
    H = meta['h']
    box = {'start': '[l]', 'end': '[r]', 'middle': ''}
    puts = []
    for x, y, s, size, w, anchor, fill in meta['texts']:
        fs = size * UNIT
        weight = '\\bfseries' if w >= 600 else ''
        puts.append(f'\\put({x:g},{H - y:g}){{\\makebox[0pt]{box[anchor]}{{\\fontsize{{{fs:.2f}}}{{{fs:.2f}}}'
                    f'\\selectfont{weight}\\color[HTML]{{{fill.lstrip("#").upper()}}}{tex_escape(s)}}}}}')
    return (f'{{\\figfont\\XeTeXinterchartokenstate=0\\setlength{{\\unitlength}}{{{UNIT:.5f}pt}}%\n'
            f'\\begin{{picture}}(760,{H:g})\n\\put(0,0){{\\includegraphics[width=760\\unitlength]{{fig{n}_shapes.pdf}}}}\n'
            + '\n'.join(puts) + '\n\\end{picture}}')


# ---------------------------------------------------------------------------------------------- manuscript -> LaTeX
def tex_escape(s):
    return (s.replace('\\', '\\textbackslash{}').replace('&', '\\&').replace('%', '\\%').replace('$', '\\$')
            .replace('#', '\\#').replace('_', '\\_').replace('{', '\\{').replace('}', '\\}'))


def figure_tex(n):
    return (f'```{{=latex}}\n\\begin{{figure}}[!htbp]\\centering\n{figure_overlay(n)}\n'
            f'\\caption{{{tex_escape(CAPTIONS[n])}}}\\label{{fig:{n}}}\n\\end{{figure}}\n```')


def equation_tex(n):
    lines = [s.strip('$') for s in figures.EQS[f'eq{n}']]
    return '```{=latex}\n\\begin{equation}\\begin{gathered}\n' + ' \\\\\n'.join(lines) + '\n\\end{gathered}\\end{equation}\n```'


def prepare(md):
    md = re.sub(r'<sub>(.*?)</sub>', r'~\1~', md)
    # Headings: LaTeX numbers sections; the manuscript's own numbers must agree with it.
    sec = sub = 0

    def heading(m):
        nonlocal sec, sub
        level, text = len(m.group(1)), m.group(2).strip()
        num = re.match(r'(\d+)(?:\.(\d+))?\.?\s+(.*)', text)
        if not num:
            return f'{m.group(1)} {text} {{.unnumbered}}'
        if level == 2:
            sec, sub = sec + 1, 0
            expect = (str(sec), None)
        else:
            sub += 1
            expect = (str(sec), str(sub))
        if (num.group(1), num.group(2)) != expect:
            raise RuntimeError(f'heading number {text!r} does not match LaTeX numbering {expect}')
        return f'{m.group(1)} {num.group(3)}'

    md = re.sub(r'^(#{2,3}) (.*)$', heading, md, flags=re.M)
    # "ตารางที่ N ..." directly above a table becomes its pandoc caption; LaTeX numbers it N.
    count = 0

    def caption(m):
        nonlocal count
        count += 1
        if int(m.group(1)) != count:
            raise RuntimeError(f'table caption {m.group(1)} out of order (expected {count})')
        return f': {m.group(2)}\n\n|'

    md = re.sub(r'^ตารางที่ (\d+) (.*)\n\n\|', caption, md, flags=re.M)
    md = re.sub(r'^\[\[FIG(\d+)\]\]$', lambda m: figure_tex(int(m.group(1))), md, flags=re.M)
    md = re.sub(r'^\[\[EQ(\d+)\]\]$', lambda m: equation_tex(int(m.group(1))), md, flags=re.M)
    return md


def to_latex(md):
    tex = subprocess.run(['pandoc', '--from=markdown-auto_identifiers', '--to=latex', '--wrap=preserve', '--shift-heading-level-by=-1',
                          '--syntax-highlighting=none'],
                         input=md, capture_output=True, text=True, check=True).stdout
    # The reference list: a hanging-indent list like the English paper's bibliography.
    head, sep, tail = tex.partition('\\section*{เอกสารอ้างอิงและอ่านเพิ่มเติม}')
    if not sep:
        raise RuntimeError('reference section not found')
    tail = tail.replace('\\begin{itemize}', '\\begin{refs}', 1).replace('\\end{itemize}', '\\end{refs}', 1)
    return head + sep + tail


body = to_latex(prepare(open('paper_th.md', encoding='utf-8').read()))
template = open('template_th.tex', encoding='utf-8').read()
fill = {
    'pdftitle': f'{TITLE}: {SUBTITLE}', 'author': AUTHOR, 'runninghead': RUNNING_HEAD, 'date': DATE,
    'title': TITLE, 'subtitle': SUBTITLE, 'thanks': THANKS, 'abstract': '\n\n'.join(ABSTRACT),
    'keywords': ' $\\cdot$ '.join(KEYWORDS), 'jel': ' $\\cdot$ '.join(JEL), 'body': body,
}
for key, value in fill.items():
    template = template.replace(f'@@{key}@@', value)
if '@@' in template:
    raise RuntimeError(f'unfilled placeholders: {set(re.findall(r"@@(\w+)@@", template))}')

for n in CAPTIONS:
    figure_shapes(n)
with open(f'{BUILD}/paper_th.tex', 'w', encoding='utf-8') as fh:
    fh.write(template)
subprocess.run(['tectonic', '--chatter', 'minimal', '--keep-logs', 'paper_th.tex'], cwd=BUILD, check=True)
shutil.copyfile(f'{BUILD}/paper_th.pdf', os.path.join('pdf', 'paper_th.pdf'))
print('ok', os.path.getsize(os.path.join('pdf', 'paper_th.pdf')), 'bytes')
