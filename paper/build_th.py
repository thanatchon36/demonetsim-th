import os, re, sys, json
import markdown
from weasyprint import HTML
import figures

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
os.makedirs('pdf', exist_ok=True)
eqs = figures.write_all('figs_th')

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

body = markdown.markdown(open('paper_th.md', encoding='utf-8').read(),
                         extensions=['tables', 'fenced_code'])

K, COLW = 172 / 760, 172  # mm per SVG unit, column width in mm


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def fig_html(n):
    meta = json.load(open(f'figs_th/fig{n}.json', encoding='utf-8'))
    H = meta['h'] * K
    spans = []
    for x, y, s, size, w, anchor, fill in meta['texts']:
        fs = size * K
        st = f'top:{y * K - 0.875 * fs:.2f}mm;font-size:{fs * 2.8346:.2f}pt;font-weight:{w};color:{fill};'
        if anchor == 'start':
            st += f'left:{x * K:.2f}mm;'
        elif anchor == 'end':
            st += f'right:{(760 - x) * K:.2f}mm;'
        else:
            st += f'left:{x * K - 60:.2f}mm;width:120mm;text-align:center;'
        spans.append(f'<span class="ft" style="{st}">{esc(s)}</span>')
    return (f'<figure><div class="fig" style="height:{H:.2f}mm"><img src="figs_th/fig{n}.svg" alt="" '
            f'style="width:{COLW}mm;height:{H:.2f}mm">' + ''.join(spans) + '</div>'
            f'<figcaption><b>รูปที่ {n}</b> {CAPTIONS[n]}</figcaption></figure>')


body = re.sub(r'<p>\[\[FIG(\d+)\]\]</p>', lambda m: fig_html(int(m.group(1))), body)
body = re.sub(r'<p>\[\[EQ(\d+)\]\]</p>', lambda m: (
    '<div class="eq">' + ''.join(f'<img src="{f}" alt="">' for f in eqs[f'eq{m.group(1)}']) + '</div>'), body)
body = body.replace('<p>ตารางที่', '<p class="tcap">ตารางที่')


def _nw(m):
    tag, inner = m.group(1), m.group(2)
    return f'<{tag} class="nw">{inner}</{tag}>' if len(re.sub('<[^>]+>', '', inner)) <= 9 else m.group(0)


body = re.sub(r'<(td|th)>(.*?)</\1>', _nw, body)

toc = []


def add_id(m):
    i = len(toc) + 1
    toc.append((f'sec-{i}', re.sub('<[^>]+>', '', m.group(1))))
    return f'<h2 id="sec-{i}">{m.group(1)}</h2>'


body = re.sub(r'<h2>(.*?)</h2>', add_id, body)
toc_html = ''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc)

KEYS = [('0.38%', 'มูลค่าแบงก์พันเทียบรายได้ต่อหัว ราว 1 ใน 4 ของ €500'),
        ('~8%', 'เงินผิดกฎหมายที่แบบช็อกทำลายหรือยึดได้ (มัธยฐาน)'),
        ('~90%', 'สัดส่วนความปั่นป่วนที่ตกกับกลุ่มเปราะบาง'),
        ('5–7%', 'ผลสูงสุดเมื่อช่องฟอกเงินรับได้เกินสต็อกเงินดำ')]
keys_html = ''.join(f'<td><div class="kn">{n}</div><div class="kt">{t}</div></td>' for n, t in KEYS)

ABSTRACT = """
<p>งานนี้ประเมินข้อเสนอยกเลิกธนบัตร 1,000 บาทเพื่อปราบทุนเทา ทุนดำ การซื้อเสียง และคอร์รัปชัน โดยทบทวน 12 กรณีต่างประเทศ วัดมูลค่าแบงก์พันเทียบรายได้ และสร้างแบบจำลอง DemonetSim-TH ที่ปรับเทียบกับอินเดีย 2016 ด้วยวิธี ABC</p>
<p>แบงก์พันมีค่าเพียง 0.38% ของรายได้ต่อหัว ราวหนึ่งในสี่ของ €500 ในแบบจำลอง การยกเลิกแบบช็อกทำลายหรือยึดเงินผิดกฎหมายได้ราว 8% (มัธยฐาน) แต่ทำให้เศรษฐกิจสะดุดราว 1 ใน 6 ของอินเดีย และราว 90% ของภาระตกกับกลุ่มเปราะบาง เงินผิดกฎหมายส่วนใหญ่เข้าระบบโดยไม่ถูกตรวจพบ หรือย้ายไปอยู่ในทอง ดอลลาร์ และคริปโต</p>
<p>ตัวแปรชี้ขาดคือความจุของเครือข่ายฟอกเงิน ไม่ใช่ความเข้มงวดของการตรวจ การทยอยเลิกควบคู่ชุดมาตรการ AML ได้ผลราว 6% โดยไม่กระทบสภาพคล่อง งานนี้เสนอวาระวิจัย 15 หัวข้อ โดยมีหัวข้อเรือธง 3 เรื่องที่ทดสอบได้ว่าแบงก์พันเป็นสื่อหลักของเงินผิดกฎหมายจริงหรือไม่</p>
<p class="kw"><b>คำสำคัญ:</b> การยกเลิกธนบัตร · ทุนเทา · การฟอกเงิน · เงินสด · แบบจำลองตัวแทน · ประเทศไทย</p>
"""

CSS = """
@page { size: A4; margin: 21mm 19mm 20mm 19mm;
  @top-left { content: "การยกเลิกธนบัตร 1,000 บาทเพื่อปราบทุนเทา–ทุนดำ"; font-family: 'IBM Plex Sans Thai'; font-size: 7.5pt; color: #8a8f98; }
  @top-right { content: "Working Paper · พฤศจิกายน 2026"; font-family: 'IBM Plex Sans Thai'; font-size: 7.5pt; color: #8a8f98; }
  @bottom-center { content: counter(page); font-family: 'IBM Plex Sans Thai'; font-size: 8.5pt; color: #5f6368; } }
@page :first { @top-left { content: none } @top-right { content: none } @bottom-center { content: none } }
html { font-family: 'Sarabun', 'Loma', sans-serif; font-size: 10.5pt; line-height: 1.6; color: #1f2328; }
body { margin: 0; }
p { margin: 0 0 7pt; orphans: 2; widows: 2; }
a { color: inherit; text-decoration: none; }
h2 { font-family: 'IBM Plex Sans Thai'; font-weight: 600; font-size: 15pt; line-height: 1.35; margin: 20pt 0 8pt;
     padding-bottom: 4pt; border-bottom: 1.2pt solid #2f6db5; break-after: avoid; }
h3 { font-family: 'IBM Plex Sans Thai'; font-weight: 600; font-size: 11.5pt; color: #2f6db5; margin: 14pt 0 5pt; break-after: avoid; }
ol, ul { margin: 0 0 8pt; padding-left: 18pt; }
li { margin-bottom: 3pt; }
blockquote { margin: 10pt 0; padding: 8pt 12pt; background: #f4f7fb; border-left: 3pt solid #2f6db5; font-size: 9.5pt; color: #3c4043; }
blockquote p { margin: 0; }
table { width: 100%; border-collapse: collapse; margin: 4pt 0 12pt; font-size: 8.6pt; line-height: 1.45; }
thead th { font-family: 'IBM Plex Sans Thai'; font-weight: 600; text-align: left; background: #eef2f7;
           border-top: 1.2pt solid #1f2328; border-bottom: 0.8pt solid #1f2328; padding: 4pt 5pt; }
td { padding: 3.5pt 5pt; border-bottom: 0.4pt solid #dfe2e6; vertical-align: top; }
tbody tr:last-child td { border-bottom: 1.2pt solid #1f2328; }
tr { break-inside: avoid; }
.nw { white-space: nowrap; }
p.tcap { font-family: 'IBM Plex Sans Thai'; font-size: 9pt; font-weight: 600; margin: 12pt 0 3pt; break-after: avoid; }
figure { margin: 10pt 0 14pt; break-inside: avoid; }
.fig { position: relative; width: 172mm; }
.fig img { position: absolute; left: 0; top: 0; }
.ft { position: absolute; white-space: nowrap; line-height: 1; font-family: 'IBM Plex Sans Thai', 'Sarabun', sans-serif; }
figcaption { font-family: 'IBM Plex Sans Thai'; font-size: 8pt; line-height: 1.45; color: #5f6368; margin-top: 4pt;
             border-top: 0.5pt solid #e4e6e9; padding-top: 3pt; }
figcaption b { color: #1f2328; margin-right: 3pt; }
.eq { margin: 6pt 0 10pt; break-inside: avoid; }
.eq img { display: block; margin: 5pt auto; }
pre { background: #f6f8fa; border: 0.5pt solid #e1e4e8; padding: 7pt 9pt; font-size: 8.5pt; border-radius: 3pt; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.5pt; }
.cover { break-after: page; }
.label { font-family: 'IBM Plex Sans Thai'; font-size: 8.5pt; font-weight: 600; letter-spacing: 0.6pt; color: #2f6db5; }
.title { font-family: 'IBM Plex Sans Thai'; font-weight: 700; font-size: 20pt; line-height: 1.32; margin: 6pt 0 6pt; }
.sub { font-style: italic; font-size: 10.5pt; color: #5f6368; margin-bottom: 9pt; }
.meta { font-size: 8.8pt; color: #5f6368; border-top: 0.6pt solid #d0d4d9; border-bottom: 0.6pt solid #d0d4d9;
        padding: 4pt 0; margin-bottom: 12pt; }
table.keys { border-collapse: separate; border-spacing: 6pt 0; margin: 0 -6pt 12pt; font-size: 8.4pt; }
table.keys td { width: 25%; border: none; border-top: 2.5pt solid #2f6db5; background: #f4f7fb; padding: 6pt 8pt 7pt; }
table.keys tr:last-child td { border-bottom: none; }
.kn { font-family: 'IBM Plex Sans Thai'; font-weight: 700; font-size: 17pt; color: #2f6db5; line-height: 1.2; }
.kt { color: #3c4043; line-height: 1.35; margin-top: 2pt; }
.abstract { background: #f8f9fa; border: 0.5pt solid #e4e6e9; border-left: 3pt solid #1f2328; padding: 9pt 13pt 4pt; margin-bottom: 12pt; }
.abstract h4, .toc h4 { font-family: 'IBM Plex Sans Thai'; font-size: 10.5pt; margin: 0 0 5pt; }
.abstract p { font-size: 9.5pt; line-height: 1.55; }
.kw { font-size: 8.8pt; color: #3c4043; }
.toc ol { list-style: none; padding: 0; margin: 0; columns: 2; column-gap: 18pt; font-size: 9pt; }
.toc li { margin: 0 0 2.5pt; }
.toc a::after { content: leader('.') target-counter(attr(href), page); color: #5f6368; }
"""

HTML_DOC = f"""<!DOCTYPE html><html lang="th"><head><meta charset="utf-8">
<title>การยกเลิกธนบัตร 1,000 บาทเพื่อปราบทุนเทา–ทุนดำ</title>
<meta name="keywords" content="demonetization, Thailand, money laundering, cash, agent-based model">
<style>{CSS}</style></head><body>
<section class="cover">
<div class="label">เอกสารวิจัยฉบับร่าง · WORKING PAPER</div>
<div class="title">การยกเลิกธนบัตร 1,000 บาทเพื่อปราบทุนเทา–ทุนดำ: บทเรียนนานาชาติ แบบจำลองเชิงนโยบาย และวาระการวิจัยสำหรับประเทศไทย</div>
<div class="sub">Demonetizing the 1,000-Baht Note: International Evidence, a Policy Simulation, and a Research Agenda for Thailand</div>
<div class="meta">7 พฤศจิกายน 2026 · ร่างเพื่อการอภิปราย ตัวเลขทั้งหมดเป็นค่าประมาณที่ต้องตรวจทาน · โค้ดและข้อมูลจำลอง: demonet_sim_th.py</div>
<table class="keys"><tr>{keys_html}</tr></table>
<div class="abstract"><h4>บทคัดย่อ</h4>{ABSTRACT}</div>
<div class="toc"><h4>สารบัญ</h4><ol>{toc_html}</ol></div>
</section>
{body}
</body></html>"""

open(os.path.join('figs_th', 'paper_th.html'), 'w', encoding='utf-8').write(HTML_DOC)
HTML(string=HTML_DOC, base_url=HERE, encoding='utf-8').write_pdf(os.path.join('pdf', 'paper_th.pdf'))
print('ok', os.path.getsize(os.path.join('pdf', 'paper_th.pdf')), 'bytes')
