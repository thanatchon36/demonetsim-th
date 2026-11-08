"""Static SVG versions of the paper's 11 figures (print palette) + equation images."""
import math, os, re

INK, QUIET, MUTED, GRID, AXIS = '#1f2328', '#5f6368', '#b3b7bd', '#e4e6e9', '#8a8f98'
ACC, REF, TINT, GOOD, BAD = '#2f6db5', '#9aa0a6', '#f1f3f5', '#2e8b57', '#c0392b'
FONT = "'IBM Plex Sans Thai','Sarabun','Loma',sans-serif"


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


TEXTS = []  # labels are kept apart from the shapes and set by XeTeX (build_th.py), which shapes the Thai marks


def T(x, y, s, size=12, w=400, anchor='start', fill=INK):
    TEXTS.append([x, y, str(s), size, w, anchor, fill])
    return ''


def R(x, y, w, h, fill='none', stroke='none', sw=1, rx=0, op=1):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.2f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"/>')


def L(x1, y1, x2, y2, stroke=GRID, sw=1, dash=None, op=1, cap='butt'):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-opacity="{op}" stroke-linecap="{cap}"{d}/>')


def C(cx, cy, r, fill=ACC, stroke='none', sw=1.5, op=1):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" fill-opacity="{op}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def P(d, fill='none', stroke=AXIS, sw=1.25, op=1, sop=1):
    return (f'<path d="{d}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-opacity="{sop}"/>')


def SVG(h, body, w=760):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="{FONT}">' + ''.join(body) + '</svg>')


def head(title, sub=None):
    out = [T(24, 30, title, 15, 600)]
    if sub:
        out.append(T(24, 50, sub, 11.5, fill=QUIET))
    return out


# ---------------------------------------------------------------- figure 1
def fig1():
    b = head('ไตรลักษณ์ของการยกเลิกธนบัตร: ทุกรูปแบบได้ไม่เกินสองในสามเป้าหมาย',
             'แต่ละด้านของสามเหลี่ยม = รูปแบบที่ได้สองเป้าหมายที่ปลายด้าน และเสียเป้าหมายที่มุมตรงข้าม')
    b += [P('M300 148L200 330'), P('M460 148L560 330'), P('M276 368H484')]

    def box(x, y, name, l1, l2):
        cx = x + 118
        return [R(x, y, 236, 76, stroke=AXIS, sw=1.25, rx=8), T(cx, y + 24, name, 13, 600, 'middle'),
                T(cx, y + 44, l1, 11.5, anchor='middle'), T(cx, y + 62, l2, 11.5, anchor='middle', fill=QUIET)]
    b += box(262, 72, 'กัด (Bite)', 'ทำลายหรือยึดสต็อกเงินผิดกฎหมายได้มาก', 'ต้องกะทันหัน ให้เวลาแลกสั้น')
    b += box(40, 330, 'นุ่ม (Smooth)', 'ต้นทุนต่ำต่อคนสุจริตและเศรษฐกิจ', 'ต้องประกาศล่วงหน้า ให้เวลานาน')
    b += box(484, 330, 'สะอาด (Clean)', 'ไม่กลายเป็นช่องฟอกเงินขนาดใหญ่', 'ต้องตรวจสอบได้ทุกยอดที่นำมาแลก')
    b += [T(228, 226, 'ไม่มีตัวอย่างจริง', 11.5, 600, 'end'),
          T(228, 242, 'ต้องรู้ก่อนว่าใครถือเงินดำ', 11.5, anchor='end', fill=QUIET),
          T(536, 222, 'ช็อก + ตรวจเข้มทุกยอด', 11.5, 600),
          T(536, 238, 'กัดและสะอาด แต่ภาระ', 11.5, fill=QUIET),
          T(536, 254, 'ต่อคนสุจริตสูงที่สุด', 11.5, fill=QUIET),
          T(380, 392, 'ทยอยเลิก', 11.5, 600, 'middle'),
          T(380, 408, 'นุ่มและสะอาด แต่ไม่กัด', 11.5, anchor='middle', fill=QUIET),
          T(380, 424, 'ยูโร แคนาดา สิงคโปร์', 11.5, anchor='middle', fill=QUIET),
          C(380, 204, 4, AXIS), T(380, 228, 'อินเดีย 2016', 11.5, 600, 'middle'),
          T(380, 244, 'มุ่ง ‘กัด’ แต่ได้ธนบัตรคืน 99.3%', 11.5, anchor='middle', fill=QUIET),
          T(380, 260, 'และเสียทั้ง ‘นุ่ม’ และ ‘สะอาด’', 11.5, anchor='middle', fill=QUIET)]
    return SVG(452, b)


# ---------------------------------------------------------------- figure 2
NOTES = [('S$10,000 สิงคโปร์ (2014)', 13.89, 'w', 0), ('RM1,000 มาเลเซีย (1999)', 7.63, 'w', 0),
         ('C$1,000 แคนาดา (2000)', 2.79, 'w', 0), ('€500 ยูโร (2016)', 1.58, 'w', 1),
         ('CHF 1,000 สวิตเซอร์แลนด์', 1.10, 'c', 0), ('₹2,000 อินเดีย (2023)', 1.05, 'w', 0),
         ('₹1,000 อินเดีย (2016)', 0.86, 'w', 1), ('S$1,000 สิงคโปร์', 0.83, 'c', 0),
         ('€200 ยูโร', 0.47, 'c', 0), ('500,000 ด่ง เวียดนาม', 0.44, 'c', 0),
         ('₱1,000 ฟิลิปปินส์', 0.43, 'c', 0), ('฿1,000 ไทย', 0.377, 't', 1),
         ('10,000 เยน ญี่ปุ่น', 0.20, 'c', 0), ('฿500 ไทย', 0.19, 'c', 0), ('RM100 มาเลเซีย', 0.18, 'c', 0),
         ('Rp100,000 อินโดนีเซีย', 0.13, 'c', 0), ('US$100 สหรัฐฯ', 0.12, 'c', 1),
         ('100 หยวน จีน', 0.10, 'c', 0), ('50,000 วอน เกาหลีใต้', 0.10, 'c', 0)]


def fig2():
    left, right, y0, step = 252, 700, 100, 22
    lo, hi = math.log10(0.05), math.log10(20)
    X = lambda v: left + (math.log10(v) - lo) / (hi - lo) * (right - left)
    Y = lambda i: y0 + i * step
    last = Y(len(NOTES) - 1)
    fmt = lambda v: f'{v:.1f}%' if v >= 1 else f'{v:.2f}%'
    b = head('แบงก์พันมีค่าเพียง 0.38% ของรายได้ต่อหัว ราวหนึ่งในสี่ของ €500 ที่ยุโรปเลิกพิมพ์',
             'มูลค่าธนบัตร 1 ใบ เทียบ GDP ต่อหัวของปีที่ระบุ (สเกล log) · ค่าประมาณ ต้องตรวจทาน')
    b += [C(30, 72, 5, MUTED, MUTED), T(42, 76, 'เลิกใช้หรือหยุดพิมพ์แล้ว', 11.5, fill=QUIET),
          C(206, 72, 5, 'none', MUTED), T(218, 76, 'ยังใช้อยู่', 11.5, fill=QUIET),
          C(300, 72, 5, ACC, ACC), T(312, 76, 'แบงก์พันของไทย', 11.5, fill=QUIET)]
    for t in [0.1, 0.2, 0.5, 1, 2, 5, 10]:
        b += [L(X(t), y0 - 12, X(t), last + 10), T(X(t), last + 28, f'{t:g}%', 11, anchor='middle', fill=QUIET)]
    b.append(L(X(0.377), y0 - 12, X(0.377), last + 10, REF, 1, '4 4'))
    for i, (n, v, k, lab) in enumerate(NOTES):
        y, th = Y(i), k == 't'
        b.append(T(left - 12, y + 4, n, 12, 600 if th else 400, 'end', INK if th else QUIET))
        b.append(C(X(v), y, 5, ACC if th else (MUTED if k == 'w' else 'none'), ACC if th else MUTED))
        if lab:
            b.append(T(X(v) + 10, y + 4, fmt(v), 11.5, 600 if th else 400, fill=INK if th else QUIET))
    return SVG(548, b)


# ---------------------------------------------------------------- figure 3
BULK = [('แบงก์ 100 บาท', 90.0, 118.8, 0), ('แบงก์ 500 บาท', 19.0, 24.7, 1), ('แบงก์ 1,000 บาท', 10.0, 12.8, 0),
        ('ธนบัตร 100 ดอลลาร์', 3.0, 3.4, 0), ('ทองคำ', 2.4, 0.12, 0), ('ธนบัตร 200 ยูโร', 1.4, 1.7, 0),
        ('USDT (คริปโต)', 0, 0, 0)]


def fig3():
    left, right, y0, step, bh = 200, 590, 92, 34, 18
    peak = max(r[1] for r in BULK)
    W = lambda v: v / peak * (right - left)
    b = head('ไม่มีแบงก์พัน เงินสด 10 ล้านบาทหนักขึ้นจาก 10 เป็น 19 กก. ขณะที่ทองคำมูลค่าเท่ากันหนัก 2.4 กก.',
             'น้ำหนักและปริมาตรโดยประมาณของมูลค่า 10 ล้านบาท · สมมติ 33 บาทต่อดอลลาร์ ทองคำ 4,000 ดอลลาร์ต่อออนซ์')
    b += [T(24, 70, 'แถบสีน้ำเงิน = สภาพหลังยกเลิกแบงก์พัน', 11.5, fill=QUIET),
          L(left, y0 - 8, left, y0 + len(BULK) * step - 8, AXIS)]
    for i, (n, kg, lit, hot) in enumerate(BULK):
        y = y0 + i * step
        b += [T(left - 10, y + 13, n, 12, 600 if hot else 400, 'end', INK if hot else QUIET),
              R(left, y, W(kg), bh, ACC if hot else MUTED),
              T(left + W(kg) + 8, y + 13, f'{kg:g} กก. · {lit:g} ลิตร', 12, 600 if hot else 400,
                fill=INK if hot else QUIET)]
    return SVG(346, b)


# ---------------------------------------------------------------- figure 4
SC = [('อินเดีย 2016 (ปรับเทียบ)', 96.8, 85.4, 113.2, 8.5, 6.2, 12.0, 0),
      ('S1 ช็อกแบบอินเดีย', 17.2, 13.2, 23.9, 7.7, 5.5, 15.4, 0),
      ('S2 ประกาศล่วงหน้า 90 วัน', 0.4, 0, 3.8, 3.4, 2.7, 4.1, 0),
      ('S3 ทยอยเลิก 5 ปี', 0, 0, 0, 1.0, 0.9, 1.2, 0),
      ('S4 ทยอยเลิก + AML', 0, 0, 0, 6.1, 4.8, 7.5, 1)]


def fig4():
    y0, step, labX, aL, aR, bL, bR = 132, 40, 204, 222, 452, 500, 730
    XA = lambda v: aL + v / 130 * (aR - aL)
    XB = lambda v: bL + v / 18 * (bR - bL)
    last = y0 + 4 * step
    fa = lambda v: f'{v:.1f}' if 0 < v < 1 else f'{v:.0f}'
    b = head('ทยอยเลิก + AML ได้ผลใกล้แบบช็อก (6% เทียบ 8%) โดยเศรษฐกิจไม่สะดุด',
             'จุด = ค่ามัธยฐาน · แถบ = ช่วงควอร์ไทล์ 25–75% · Monte Carlo 600 รอบต่อสถานการณ์ · สีน้ำเงิน = S4')
    b += [T(aL, 86, 'เศรษฐกิจสะดุด', 13, 600), T(aL, 104, 'ดัชนี อินเดีย 2016 = 100', 11.5, fill=QUIET),
          T(bL, 86, 'เงินผิดกฎหมายที่ถูกทำลายหรือยึด', 13, 600),
          T(bL, 104, '% ของสต็อกเงินผิดกฎหมาย', 11.5, fill=QUIET)]
    for t in (0, 50, 100):
        b += [L(XA(t), y0 - 16, XA(t), last + 16), T(XA(t), last + 34, str(t), 11, anchor='middle', fill=QUIET)]
    for t in (0, 5, 10, 15):
        b += [L(XB(t), y0 - 16, XB(t), last + 16), T(XB(t), last + 34, f'{t}%', 11, anchor='middle', fill=QUIET)]
    for i, (n, lq, llo, lhi, h, hlo, hhi, hot) in enumerate(SC):
        y = y0 + i * step
        c, tc, w = (ACC, INK, 600) if hot else (MUTED, QUIET, 400)
        b += [T(labX, y + 4, n, 12, w, 'end', tc),
              L(XA(llo), y, XA(lhi), y, c, 7, op=0.35, cap='round'), C(XA(lq), y, 5.5, c),
              T(XA(lhi) + 10, y + 4, fa(lq), 11.5, w, fill=tc),
              L(XB(hlo), y, XB(hhi), y, c, 7, op=0.35, cap='round'), C(XB(h), y, 5.5, c),
              T(XB(hhi) + 10, y + 4, f'{h:.1f}%', 11.5, w, fill=tc)]
    return SVG(348, b)


# ---------------------------------------------------------------- figure 5
FATE = [('อินเดีย 2016', [0.67, 8.90, 2.44, 60.23, 27.76]), ('S1 ช็อก', [2.64, 8.70, 2.61, 60.91, 25.15]),
        ('S2 ประกาศ 90 วัน', [0.22, 3.62, 0.71, 29.98, 65.47]), ('S3 ทยอยเลิก', [0.00, 1.06, 0.19, 52.91, 45.84]),
        ('S4 ทยอยเลิก + AML', [0.46, 6.35, 1.14, 67.37, 24.68])]
PARTS = ['ถูกทำลาย', 'ถูกยึด/ภาษี/ค่าปรับ', 'เหลือหลังจ่ายค่าปรับ', 'เข้าระบบโดยไม่ถูกตรวจพบ',
         'ย้ายที่ซ่อน หรือเป็นค่าฟอกเงิน']


def fig5():
    left, wide, y0, step, bh = 200, 440, 134, 40, 24
    tone, shade = [ACC, ACC, ACC, MUTED, MUTED], [1, 0.62, 0.3, 0.95, 0.45]
    lx, ly = [24, 150, 330, 24, 250], [78, 78, 78, 98, 98]
    b = head('เงินผิดกฎหมายส่วนใหญ่รอด: ถูกทำลายหรือยึดได้เพียง 1–11% ในทุกสถานการณ์',
             'สีน้ำเงิน = รัฐได้ผล · สีเทา = เงินผิดกฎหมายรอด · ค่าเฉลี่ยจาก Monte Carlo จึงสูงกว่าค่ามัธยฐานในรูปที่ 4')
    for k, p in enumerate(PARTS):
        b += [R(lx[k], ly[k] - 10, 12, 12, tone[k], rx=2, op=shade[k]), T(lx[k] + 18, ly[k], p, 11.5)]
    b.append(T(left + wide + 14, y0 - 12, 'ทำลาย + ยึด', 11.5, 600))
    for i, (n, v) in enumerate(FATE):
        y, tot, acc = y0 + i * step, sum(v), 0.0
        b.append(T(left - 12, y + bh / 2 + 4, n, 12, anchor='end'))
        for k, p in enumerate(v):
            x, w = left + acc / tot * wide, p / tot * wide
            acc += p
            b.append(R(x, y, w, bh, tone[k], op=shade[k]))
            if p >= 8:
                b.append(T(x + w / 2, y + bh / 2 + 4, f'{round(p)}%', 11, anchor='middle'))
        b.append(T(left + wide + 14, y + bh / 2 + 4, f'{v[0] + v[1]:.1f}%', 12, 600))
    return SVG(340, b)


# ---------------------------------------------------------------- figure 6
CAL = [(3.0, 99.64, 99.44, 99.76), (5.0, 99.64, 99.47, 99.77), (7.1, 99.63, 99.47, 99.78), (9.0, 99.63, 99.42, 99.78),
       (11.0, 99.64, 99.42, 99.79), (13.0, 99.63, 99.23, 99.79), (15.0, 99.64, 98.50, 99.79), (17.0, 99.60, 98.38, 99.79),
       (19.0, 99.56, 97.77, 99.78), (21.1, 99.49, 97.21, 99.78), (23.0, 99.34, 97.05, 99.78), (25.1, 99.20, 96.55, 99.76),
       (26.9, 99.17, 96.14, 99.77), (29.0, 98.48, 95.56, 99.74)]


def fig6():
    left, right, y0, bottom = 80, 680, 92, 312
    X = lambda v: left + v / 30 * (right - left)
    Y = lambda v: bottom - (v - 95) / 5 * (bottom - y0)
    b = head('อัตราคืน 99.3% ของอินเดียเข้ากันได้กับเงินดำตั้งแต่ 3% ถึง 29% จึงบอกขนาดเงินดำไม่ได้',
             'เส้น = มัธยฐานของการจำลอง · แถบฟ้า = เปอร์เซ็นไทล์ 10–90 · แถบเทา = เกณฑ์ยอมรับ ABC (99.3 ± 0.3%)')
    b.append(T(left, y0 - 16, 'อัตราคืนธนบัตรจำลอง', 11.5, fill=QUIET))
    for t in range(95, 101):
        b += [L(left, Y(t), right, Y(t)), T(left - 8, Y(t) + 4, f'{t}%', 11, anchor='end', fill=QUIET)]
    b.append(R(left, Y(99.6), right - left, Y(99.0) - Y(99.6), TINT))
    pts = ' '.join(f'{X(a):.1f},{Y(c):.1f}' for a, _, _, c in CAL) + ' ' + \
          ' '.join(f'{X(a):.1f},{Y(lo):.1f}' for a, _, lo, _ in reversed(CAL))
    b.append(f'<polygon points="{pts}" fill="{ACC}" fill-opacity="0.16"/>')
    b += [L(left, Y(99.3), right, Y(99.3), REF, 1, '4 4'), T(left + 8, Y(99.3) + 13, 'RBI: คืน 99.3%', 10.5, fill=QUIET)]
    b.append(P('M' + ' L'.join(f'{X(a):.1f} {Y(m):.1f}' for a, m, _, _ in CAL), 'none', ACC, 2.25))
    b += [C(X(a), Y(m), 3, ACC) for a, m, _, _ in CAL]
    b.append(T(X(29.0) + 10, Y(98.48) + 4, 'มัธยฐาน', 11.5, 600))
    b.append(L(left, bottom, right, bottom, AXIS))
    b += [T(X(t), bottom + 20, f'{t}%', 11, anchor='middle', fill=QUIET) for t in range(0, 31, 5)]
    b.append(T((left + right) / 2, bottom + 44, 'สัดส่วนเงินดำในธนบัตรที่ถูกยกเลิก (สมมติ)', 11.5,
               anchor='middle', fill=QUIET))
    return SVG(370, b)


# ---------------------------------------------------------------- figure 7
CAPS = [1, 2.5, 5, 7.5, 10, 15, 20]
SENS = [('ตรวจผ่อน (0.3)', 0.4, [17.7, 12.2, 7.9, 6.2, 6.0, 5.8, 6.0]),
        ('ตรวจปานกลาง (0.5)', 0.7, [31.1, 23.3, 11.6, 6.1, 5.5, 5.1, 5.4]),
        ('ตรวจเข้ม (0.8)', 1.0, [41.4, 32.2, 17.6, 6.8, 6.2, 6.1, 5.6])]


def fig7():
    left, right, y0, bottom = 80, 680, 92, 312
    X = lambda v: left + v / 20 * (right - left)
    Y = lambda v: bottom - v / 45 * (bottom - y0)
    b = head('เมื่อช่องฟอกเงินรับได้เกินสต็อกเงินดำ ตรวจเข้มแค่ไหนผลก็เหลือเพียง 5–7%',
             'สถานการณ์ S1 (ช็อก) · สมมติเงินผิดกฎหมาย 10% ของแบงก์พัน · ค่ามัธยฐาน 80 รอบต่อจุด')
    b.append(T(left, y0 - 16, '% ของเงินผิดกฎหมายที่ถูกทำลายหรือยึด', 11.5, fill=QUIET))
    for t in range(0, 41, 10):
        b += [L(left, Y(t), right, Y(t)), T(left - 8, Y(t) + 4, f'{t}%', 11, anchor='end', fill=QUIET)]
    b += [L(X(10), y0, X(10), bottom, REF, 1, '4 4'),
          T(X(10) + 8, y0 + 12, 'ความจุ = สต็อกเงินผิดกฎหมายทั้งหมด', 11.5, fill=QUIET),
          T(X(10) + 8, y0 + 28, '(เมื่อเงินผิดกฎหมายเป็น 10% ของแบงก์พัน)', 11.5, fill=QUIET)]
    for j, (name, op, vals) in enumerate(SENS):
        b.append(P('M' + ' L'.join(f'{X(c):.1f} {Y(v):.1f}' for c, v in zip(CAPS, vals)), 'none', ACC, 2.25, sop=op))
        b += [C(X(c), Y(v), 3.5, ACC, op=op) for c, v in zip(CAPS, vals)]
        b += [L(470, 160 + j * 20, 496, 160 + j * 20, ACC, 2.25, op=op), T(504, 164 + j * 20, name, 11.5)]
    b.append(T(X(15), Y(6) - 14, 'ผลคงที่ราว 5–7%', 11.5, 600, 'middle'))
    b.append(L(left, bottom, right, bottom, AXIS))
    b += [T(X(t), bottom + 20, f'{t}%', 11, anchor='middle', fill=QUIET) for t in range(0, 21, 5)]
    b.append(T((left + right) / 2, bottom + 44, 'ความจุของเครือข่ายฟอกเงินตลอดช่วงแลก (% ของแบงก์พันทั้งหมด)', 11.5,
               anchor='middle', fill=QUIET))
    return SVG(372, b)


# ---------------------------------------------------------------- figure 8
def fig8():
    gx0, cw, gy0, rh = 136, 200, 104, 112
    cx = lambda c: gx0 + c * cw
    ry = lambda r: gy0 + r * rh
    b = head('ข้อเสียที่หนักที่สุดมีหลักฐานแน่น ส่วนข้อดีทุกข้อผลเล็กหรือหลักฐานยังอ่อน',
             'จัดตำแหน่งตามการประเมินของผู้เขียนในตารางที่ 8 · พื้นจาง = มุมที่ควรกังวลที่สุด (ผลใหญ่ หลักฐานแน่น)')
    b += [R(24, 64, 52, 20, GOOD, GOOD, 1.25, 10, 0.14), T(50, 78, 'ข้อดี', 11.5, anchor='middle'),
          R(86, 64, 60, 20, BAD, BAD, 1.25, 10, 0.14), T(116, 78, 'ข้อเสีย', 11.5, anchor='middle'),
          R(cx(2), ry(0), cw, rh, TINT)]
    for k in range(4):
        b += [L(cx(0), ry(k), cx(3), ry(k)), L(cx(k), ry(0), cx(k), ry(3))]
    for r, s in enumerate(['ผลกระทบใหญ่', 'ผลกระทบกลาง', 'ผลกระทบเล็ก']):
        b.append(T(gx0 - 12, ry(r) + rh / 2 + 4, s, 12, 600, 'end'))
    for c, s in enumerate(['หลักฐานอ่อน', 'หลักฐานปานกลาง', 'หลักฐานแน่น']):
        b.append(T(cx(c) + cw / 2, ry(3) + 22, s, 12, 600, 'middle'))
    b.append(T(cx(1) + cw / 2, ry(3) + 42, 'ความแข็งแรงของหลักฐาน →', 11.5, anchor='middle', fill=QUIET))
    chips = [(2, 0, 0, 0, 'เศรษฐกิจนอกระบบสะดุด'), (2, 0, 1, 0, 'ภาระตกที่กลุ่มเปราะบาง'),
             (1, 0, 0, 0, 'ความเชื่อมั่นและการเมือง'), (1, 1, 0, 0, 'ช่องฟอกเงินช่วงแลก'),
             (1, 1, 1, 0, 'เงินย้ายไปทอง/ดอลลาร์/คริปโต'), (1, 1, 2, 0, 'ความเสี่ยงทางกฎหมาย'),
             (0, 1, 0, 1, 'ขยายฐานภาษี'), (0, 1, 1, 1, 'ข้อมูลจากการแลกเงิน'),
             (2, 2, 0, 1, 'ทำลาย/ยึดเงินผิดกฎหมาย'), (1, 2, 0, 1, 'ขนเงินสดก้อนใหญ่ยากขึ้น'),
             (1, 2, 1, 1, 'ผลักสู่ธนาคารและดิจิทัล'), (1, 2, 2, 0, 'ต้นทุนพิมพ์และ seigniorage'),
             (0, 2, 0, 1, 'สัญญาณป้องปราม'), (0, 2, 1, 1, 'ลดการซื้อเสียง'), (0, 2, 2, 0, 'ผู้ถือเงินบาทข้ามแดน')]
    for c, r, i, pro, s in chips:
        col, y = (GOOD if pro else BAD), ry(r) + 8 + i * 33
        b += [R(cx(c) + 6, y, cw - 12, 26, col, col, 1.25, 13, 0.14), T(cx(c) + cw / 2, y + 17, s, 12, anchor='middle')]
    return SVG(500, b)


# ---------------------------------------------------------------- figure 9
OPTS = [('ก. ช็อก (S1)', [3, 3, 1, 1, 1, 2, 1]), ('ข. ประกาศ 90 วัน (S2)', [2, 3, 3, 3, 3, 2, 2]),
        ('ค. ทยอยเลิก (S3)', [1, 3, 5, 5, 5, 3, 4]), ('ค+. ทยอยเลิก+AML (S4)', [3, 4, 4, 4, 4, 3, 4]),
        ('ง. AML + เพดานเงินสด', [1, 4, 4, 5, 4, 4, 5])]
CRITS = [('กัดเงิน', 'ผิดกฎหมาย'), ('สกัดการใช้', 'ในอนาคต'), ('เศรษฐกิจ', 'สะดุดน้อย'), ('ไม่เปิดช่อง', 'ฟอกเงิน'),
         ('เสี่ยงทาง', 'การเมืองต่ำ'), ('ค่าดำเนิน', 'การต่ำ'), ('ถอยกลับ', 'ได้ง่าย')]


def fig9():
    gx0, cw, gy0, rh, ch = 172, 74, 128, 40, 36
    cx = lambda j: gx0 + j * cw
    ry = lambda i: gy0 + i * rh
    ax = gx0 + 7 * cw + 32
    col = lambda s: {5: (GOOD, 0.42), 4: (GOOD, 0.24), 3: (MUTED, 0.35), 2: (BAD, 0.22), 1: (BAD, 0.42)}[s]
    avgs = [sum(v) / 7 for _, v in OPTS]
    b = head('แบบช็อกได้คะแนนต่ำสุด (1.7 จาก 5) ทางเลือกที่ผูกกับ AML ได้ 3.7–3.9',
             '5 ทางเลือก × 7 เกณฑ์ · ค และ ค+ คือการทยอยเลิกแบงก์พัน ส่วน ง ไม่ยกเลิกธนบัตร')
    for j, (a, c) in enumerate(CRITS):
        b += [T(cx(j) + cw / 2, 98, a, 11, anchor='middle'), T(cx(j) + cw / 2, 113, c, 11, anchor='middle')]
    b.append(T(ax, 113, 'เฉลี่ย', 11, 600, 'middle'))
    for i, (n, v) in enumerate(OPTS):
        b.append(T(gx0 - 10, ry(i) + ch / 2 + 4, n, 12, anchor='end'))
        for j, s in enumerate(v):
            f, o = col(s)
            b += [R(cx(j) + 2, ry(i), cw - 4, ch, f, rx=4, op=o), T(cx(j) + cw / 2, ry(i) + ch / 2 + 5, s, 13, 600, 'middle')]
        a = avgs[i]
        b.append(T(ax, ry(i) + ch / 2 + 5, f'{a:.1f}', 13, 700 if a in (max(avgs), min(avgs)) else 400, 'middle'))
    b.append(T(24, ry(5) + 18, 'คะแนน 1–5 จากการประเมินของผู้เขียน (5 = ดีที่สุด) · เขียว = ดี · แดง = แย่ · '
                               'ค่าเฉลี่ยให้น้ำหนักทุกเกณฑ์เท่ากัน', 11.5, fill=QUIET))
    return SVG(368, b)


# ---------------------------------------------------------------- figure 10
def fig10():
    left, w, gap, by, bh = 24, 166, 16, 84, 108
    bx = lambda i: left + i * (w + gap)
    gx = lambda i: bx(i) + w + gap / 2
    b = head('เส้นทางที่ปลอดภัยกว่า: ทยอยเลิก 5 ปี โดยมี 3 ด่านให้หยุดหรือถอยได้',
             'ไม่ได้ย่อส่วนตามเวลาจริง · กรอบสีน้ำเงิน = เริ่มได้ทันที · รูปเพชร = ด่านตัดสินใจ ไม่ผ่านให้หยุดหรือถอย')
    phases = [('0 เตรียมการ', 'เดือนที่ 0–12', 'ทำวิจัยเรือธงในหมวด 8', 'ออก พ.ร.บ. และชุด AML'),
              ('1 หยุดพิมพ์แบงก์พัน', 'ปีที่ 1–2', 'ATM จ่ายแบงก์ 500 แทน', 'เพดานเงินสดเริ่มใช้'),
              ('2 ทยอยถอน', 'ปีที่ 2–5', 'ธนาคารไม่นำกลับมาจ่าย', 'แลกง่ายสำหรับผู้สูงอายุ'),
              ('3 ยุติสภาพชำระหนี้', 'หลังปีที่ 5', 'แลกที่ ธปท. ได้ตลอดไป', 'ยอดใหญ่ต้องแสดงที่มา')]
    for i, (n, t, a, c) in enumerate(phases):
        hot = i == 0
        b += [R(bx(i), by, w, bh, ACC if hot else 'none', ACC if hot else AXIS, 2 if hot else 1.25, 8,
                0.12 if hot else 1),
              T(bx(i) + 12, by + 24, n, 13, 600), T(bx(i) + 12, by + 42, t, 11.5, fill=QUIET),
              T(bx(i) + 12, by + 66, a, 11.5), T(bx(i) + 12, by + 84, c, 11.5)]
    gates = [('ด่าน 1: หลักฐานยืนยันว่า', 'แบงก์พันคือปัญหาจริงหรือไม่'),
             ('ด่าน 2: สภาพคล่องปกติ', 'และแบงก์พันลดลงจริง'),
             ('ด่าน 3: แบงก์พันเหลือ', 'ต่ำกว่า 10% ของที่เคยมี')]
    for i, (a, c) in enumerate(gates):
        x, y = gx(i), by + bh / 2
        b += [P(f'M{x} {y - 10}l10 10l-10 10l-10 -10z', TINT, AXIS, 1.25),
              T(x, by + bh + 24, a, 11.5, 600, 'middle'), T(x, by + bh + 40, c, 11.5, anchor='middle', fill=QUIET)]
    b += [R(24, 258, 712, 36, TINT, AXIS, 1.25, 8),
          T(380, 281, 'ตลอดทุกระยะ: ประเมินผลอิสระทุกปี และเปิดข้อมูลธนบัตรรายชนิดราคาเป็นรายเดือน', 11.5,
            anchor='middle')]
    return SVG(318, b)


# ---------------------------------------------------------------- figure 11
def fig11():
    gx0, cw, gy0, rh = 176, 186, 100, 190
    cx = lambda c: gx0 + c * cw
    ry = lambda r: gy0 + r * rh
    b = head('หัวข้อเรือธง 3 เรื่อง (★) ให้คุณค่าเชิงนโยบายสูง และสองเรื่องใช้ข้อมูลเปิดได้ทันที',
             '15 หัวข้อ จัดตามคุณค่าเชิงนโยบาย × ความเป็นไปได้ด้านข้อมูล · ประเมินโดยผู้เขียน · พื้นจาง = เริ่มได้ก่อน')
    b.append(R(cx(2), ry(0), cw, rh, TINT))
    b += [L(cx(0), ry(k), cx(3), ry(k)) for k in range(3)] + [L(cx(k), ry(0), cx(k), ry(2)) for k in range(4)]
    b += [T(gx0 - 12, ry(0) + rh / 2 + 4, 'คุณค่าสูง', 12, 600, 'end'),
          T(gx0 - 12, ry(1) + rh / 2 + 4, 'คุณค่าปานกลาง', 12, 600, 'end')]
    for c, s in enumerate(['ข้อมูลเข้าถึงยาก', 'ต้องขอความร่วมมือ', 'ข้อมูลเปิด ทำได้ทันที']):
        b.append(T(cx(c) + cw / 2, ry(2) + 22, s, 12, 600, 'middle'))
    b.append(T(cx(1) + cw / 2, ry(2) + 42, 'ความเป็นไปได้ด้านข้อมูล →', 11.5, anchor='middle', fill=QUIET))
    chips = [(2, 0, 0, 1, 'A3 เงินสดก่อนเลือกตั้ง ★'), (2, 0, 1, 1, 'D1 แบงก์พันในของกลาง ★'),
             (1, 0, 0, 0, 'A1 ใครถือแบงก์พัน'), (1, 0, 1, 0, 'C1 ผลต่อกลุ่มเปราะบาง'),
             (1, 0, 2, 0, 'D2 รูปแบบการซื้อเสียง'), (1, 0, 3, 0, 'E2 เพดานเงินสด vs ยกเลิก'),
             (1, 0, 4, 1, 'F1 หนีเกณฑ์อี-เพย์เมนต์ ★'), (0, 0, 0, 0, 'D3 เงินย้ายที่และบัญชีม้า'),
             (2, 1, 0, 0, 'A2 ขนาดเศรษฐกิจนอกระบบ'), (2, 1, 1, 0, 'B1 เทียบนโยบายข้ามประเทศ'),
             (2, 1, 2, 0, 'B2 การเมืองเชิงสัญลักษณ์'), (2, 1, 3, 0, 'C2 การยอมรับของประชาชน'),
             (2, 1, 4, 0, 'E1 อำนาจตาม พ.ร.บ.เงินตรา'), (1, 1, 0, 0, 'C3 เงินบาทข้ามพรมแดน'),
             (1, 1, 1, 0, 'F2 ต่อยอดแบบจำลอง')]
    for c, r, i, star, s in chips:
        y = ry(r) + 10 + i * 34
        b += [R(cx(c) + 4, y, cw - 8, 26, ACC if star else 'none', ACC if star else AXIS, 2 if star else 1.25, 13,
                0.12 if star else 1),
              T(cx(c) + cw / 2, y + 17, s, 11.5, 600 if star else 400, 'middle')]
    return SVG(540, b)


# ---------------------------------------------------------------- equations
EQS = {
    'eq1': [r'$c_h = 1-\exp\left(-\frac{a_h^{\mathrm{eff}}\,W}{\tau}\right),\qquad '
            r'a_h^{\mathrm{eff}} = a_h\left[1-\frac{1}{2}\,\kappa_b\,(1-a_h)\right]$'],
    'eq2': [r'$G = \frac{(1-R_0)^2}{2r},\qquad L = s\sum_h w_h\,d_h\,(1-g_h)\,G,\qquad '
            r'\mathrm{Index} = 100\,\frac{L}{\bar{L}_{\mathrm{IN16}}}$'],
    'eq3': [r'$V^{\mathrm{dep}}_i = 1-p^{\mathrm{dep}}_i\,\pi_i,\qquad p^{\mathrm{dep}}_i = \kappa_b\,(1-e^{-x_i})\,\rho_i$',
            r'$V^{\mathrm{str}}_i = (1-f^{s}_i)\,(1-p^{\mathrm{str}}_i\,\pi_i),\qquad p^{\mathrm{str}}_i = \kappa_b\,q_s\,\rho_i$',
            r'$V^{\mathrm{cnv}}_i = (1-f^{c}_i)\,(1-p^{\mathrm{cnv}}_i\,\pi_i),\qquad p^{\mathrm{cnv}}_i = \kappa_d\,q_c\,\rho_i$',
            r'$V^{\mathrm{amn}}_i = 1-t_a\ \ (\mathrm{grey\ only}),\qquad V^{\mathrm{abn}}_i = 0$'],
    'eq4': [r'$k_i^{*} = \arg\max_{k\in\mathcal{A}_i}\left(V^{k}_i+\varepsilon_{ik}\right),\qquad '
            r'\varepsilon_{ik}\sim\mathrm{Gumbel}(0,\,0.02)$'],
}


def render_equations(outdir):
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import mathtext, rcParams
    from matplotlib.font_manager import FontProperties
    rcParams['mathtext.fontset'] = 'cm'
    rcParams['svg.fonttype'] = 'path'
    files = {}
    for key, lines in EQS.items():
        files[key] = []
        for k, s in enumerate(lines):
            fn = os.path.join(outdir, f'{key}_{k}.svg')
            mathtext.math_to_image(s, fn, prop=FontProperties(size=12.5), format='svg')
            files[key].append(fn)
    return files


def write_all(outdir):
    import json
    os.makedirs(outdir, exist_ok=True)
    for i, fn in enumerate([fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11], start=1):
        TEXTS.clear()
        svg = fn()
        h = float(re.search(r'viewBox="0 0 760 ([0-9.]+)"', svg).group(1))
        with open(os.path.join(outdir, f'fig{i}.svg'), 'w', encoding='utf-8') as fh:
            fh.write(svg)
        with open(os.path.join(outdir, f'fig{i}.json'), 'w', encoding='utf-8') as fh:
            json.dump({'h': h, 'texts': TEXTS}, fh, ensure_ascii=False)
    return render_equations(outdir)


if __name__ == '__main__':
    print(write_all('figs'))
