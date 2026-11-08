"""English vector figures for the PhD-level paper (SVG -> PDF via WeasyPrint)."""
import math, os, re, json
from figures import R, L, C, P, esc, INK, QUIET, MUTED, GRID, AXIS, ACC, REF, TINT, GOOD, BAD

FONT = "Inter,'IBM Plex Sans Thai','DejaVu Sans',sans-serif"


TEXTS = []


def T(x, y, s, size=12, w=400, anchor='start', fill=INK, within=None):
    TEXTS.append((x, y, str(s), size, w, anchor, within))
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{w}" '
            f'text-anchor="{anchor}" fill="{fill}">{esc(s)}</text>')


def SVG(h, body, w=760, top=0):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {top} {w} {h - top}" width="{w}" height="{h - top}" '
            f'font-family="{FONT}">' + ''.join(body) + '</svg>')


def head(title, sub=None):
    return []  # titles and notes live in the LaTeX captions


NOTES = [('SGD 10,000 Singapore (2014)', 13.89, 'w', 0), ('MYR 1,000 Malaysia (1999)', 7.63, 'w', 0),
         ('CAD 1,000 Canada (2000)', 2.79, 'w', 0), ('EUR 500 euro area (2016)', 1.58, 'w', 1),
         ('CHF 1,000 Switzerland', 1.10, 'c', 0), ('INR 2,000 India (2023)', 1.05, 'w', 0),
         ('INR 1,000 India (2016)', 0.86, 'w', 1), ('SGD 1,000 Singapore', 0.83, 'c', 0),
         ('EUR 200 euro area', 0.47, 'c', 0), ('VND 500,000 Vietnam', 0.44, 'c', 0),
         ('PHP 1,000 Philippines', 0.43, 'c', 0), ('THB 1,000 Thailand', 0.377, 't', 1),
         ('JPY 10,000 Japan', 0.20, 'c', 0), ('THB 500 Thailand', 0.19, 'c', 0), ('MYR 100 Malaysia', 0.18, 'c', 0),
         ('IDR 100,000 Indonesia', 0.13, 'c', 0), ('USD 100 United States', 0.12, 'c', 1),
         ('CNY 100 China', 0.10, 'c', 0), ('KRW 50,000 Korea', 0.10, 'c', 0)]


def f_relvalue():
    left, right, y0, step = 252, 700, 100, 22
    lo, hi = math.log10(0.05), math.log10(20)
    X = lambda v: left + (math.log10(v) - lo) / (hi - lo) * (right - left)
    Y = lambda i: y0 + i * step
    last = Y(len(NOTES) - 1)
    fmt = lambda v: f'{v:.1f}%' if v >= 1 else f'{v:.2f}%'
    b = head('The THB 1,000 note is worth 0.38% of GDP per capita, a quarter of the EUR 500',
             'One note relative to GDP per capita in the year shown (log scale); approximate, to be verified')
    b += [C(30, 72, 5, MUTED, MUTED), T(42, 76, 'withdrawn or no longer issued', 11.5, fill=QUIET),
          C(236, 72, 5, 'none', MUTED), T(248, 76, 'in circulation', 11.5, fill=QUIET),
          C(340, 72, 5, ACC, ACC), T(352, 76, "Thailand's THB 1,000", 11.5, fill=QUIET)]
    for t in [0.1, 0.2, 0.5, 1, 2, 5, 10]:
        b += [L(X(t), y0 - 12, X(t), last + 10), T(X(t), last + 28, f'{t:g}%', 11.5, anchor='middle', fill=QUIET)]
    b.append(L(X(0.377), y0 - 12, X(0.377), last + 10, REF, 1, '4 4'))
    for i, (n, v, k, lab) in enumerate(NOTES):
        y, th = Y(i), k == 't'
        b.append(T(left - 12, y + 4, n, 12, 600 if th else 400, 'end', INK if th else QUIET))
        b.append(C(X(v), y, 5, ACC if th else (MUTED if k == 'w' else 'none'), ACC if th else MUTED))
        if lab:
            b.append(T(X(v) + 10, y + 4, fmt(v), 11.5, 600 if th else 400, fill=INK if th else QUIET))
    return SVG(548, b, top=58)


BULK = [('THB 500 notes', 19.0, 24.7, 1), ('THB 1,000 notes', 10.0, 12.8, 0), ('USD 100 notes', 3.0, 3.4, 0),
        ('Gold', 2.4, 0.12, 0), ('EUR 200 notes', 1.4, 1.7, 0), ('USDT (stablecoin)', 0, 0, 0)]


def f_bulk():
    y0, step, bh = 112, 28, 16
    aL, aR, bL, bR = 184, 420, 484, 690
    XA = lambda v: aL + v / 20 * (aR - aL)
    XB = lambda v: bL + v / 26 * (bR - bL)
    last = y0 + (len(BULK) - 1) * step
    b = [T(aL, 86, '(a) Weight', 13, 600), T(aL + 74, 86, 'kg', 11.5, fill=QUIET),
         T(bL, 86, '(b) Volume', 13, 600), T(bL + 76, 86, 'litres', 11.5, fill=QUIET)]
    for i in range(len(BULK)):
        if i % 2 == 0:
            b.append(R(24, y0 + i * step - step / 2, 712, step, '#f4f5f7'))
    b += [L(aL, y0 - 14, aL, last + 14, AXIS), L(bL, y0 - 14, bL, last + 14, AXIS)]
    for i, (n, kg, lit, hot) in enumerate(BULK):
        y = y0 + i * step
        c, tc, w = (ACC, INK, 600) if hot else (MUTED, QUIET, 400)
        b += [T(170, y + 4, n, 12, w, 'end', INK if hot else QUIET),
              R(aL, y - bh / 2, XA(kg) - aL, bh, c), T(XA(kg) + 6, y + 4, f'{kg:g}', 11.5, w, fill=tc),
              R(bL, y - bh / 2, XB(lit) - bL, bh, c), T(XB(lit) + 6, y + 4, f'{lit:g}', 11.5, w, fill=tc)]
    return SVG(last + 28, b, top=70)


def f_trilemma():
    b = head('The demonetization trilemma: no design secures more than two of three goals',
             'Each side is a design that secures the goals at its two ends and sacrifices the goal at the opposite vertex')
    b += [P('M300 148L200 330'), P('M460 148L560 330'), P('M276 368H484')]

    def box(x, y, name, l1, l2):
        cx = x + 118
        return [R(x, y, 236, 76, stroke=AXIS, sw=1.25, rx=8), T(cx, y + 24, name, 13, 600, 'middle', within=(x, x + 236)),
                T(cx, y + 44, l1, 11.5, anchor='middle', within=(x, x + 236)),
                T(cx, y + 62, l2, 11.5, anchor='middle', fill=QUIET, within=(x, x + 236))]
    b += box(262, 72, 'Bite', 'Destroys or seizes illicit cash', 'needs surprise, short window')
    b += box(40, 330, 'Smoothness', 'Low cost to honest holders', 'needs notice, long window')
    b += box(484, 330, 'Integrity', 'No laundering via the exchange', 'needs scrutiny of every deposit')
    b += [T(228, 226, 'No real-world example', 11.5, 600, 'end'),
          T(228, 242, 'requires knowing who holds it', 11.5, anchor='end', fill=QUIET),
          T(536, 222, 'Shock + full scrutiny', 11.5, 600),
          T(536, 238, 'bite and integrity, but the', 11.5, fill=QUIET),
          T(536, 254, 'highest burden on the honest', 11.5, fill=QUIET),
          T(380, 392, 'Gradual phase-out', 11.5, 600, 'middle'),
          T(380, 408, 'smooth and clean, no bite', 11.5, anchor='middle', fill=QUIET),
          T(380, 424, 'euro area, Canada, Singapore', 11.5, anchor='middle', fill=QUIET),
          C(380, 204, 4, AXIS), T(380, 228, 'India 2016', 11.5, 600, 'middle'),
          T(380, 244, 'aimed to bite; 99.3% returned', 11.5, anchor='middle', fill=QUIET),
          T(380, 260, 'and lost smoothness and integrity', 11.5, anchor='middle', fill=QUIET)]
    return SVG(440, b, top=60)


SC = [('India 2016 (calibrated)', 96.8, 85.4, 113.2, 8.5, 6.2, 12.0, 0),
      ('S1 Shock (India-style)', 17.2, 13.2, 23.9, 7.7, 5.5, 15.4, 0),
      ('S2 Announced, 90 days', 0.4, 0, 3.8, 3.4, 2.7, 4.1, 0),
      ('S3 Phase-out, 5 years', 0, 0, 0, 1.0, 0.9, 1.2, 0),
      ('S4 Phase-out + AML', 0, 0, 0, 6.1, 4.8, 7.5, 1)]


def f_bite():
    y0, step, labX, aL, aR, bL, bR = 130, 34, 204, 222, 452, 500, 730
    XA = lambda v: aL + v / 130 * (aR - aL)
    XB = lambda v: bL + v / 18 * (bR - bL)
    last = y0 + 4 * step
    fa = lambda v: f'{v:.1f}' if 0 < v < 1 else f'{v:.0f}'
    b = head('Phase-out + AML bites nearly as hard as a shock (6% vs 8%) at no liquidity cost',
             'Dot = median · bar = interquartile range · 600 Monte Carlo draws per scenario · blue = S4')
    b += [T(aL, 86, '(a) Economic disruption', 13, 600), T(aL, 104, 'index, India 2016 = 100', 11.5, fill=QUIET),
          T(bL, 86, '(b) Bite on illicit cash', 13, 600), T(bL, 104, '% of illicit stock destroyed or seized', 11.5, fill=QUIET)]
    for i in range(len(SC)):
        if i % 2 == 0:
            b.append(R(24, y0 + i * step - step / 2, 712, step, '#f4f5f7'))
    for t in (0, 50, 100):
        b += [L(XA(t), y0 - 16, XA(t), last + 16), T(XA(t), last + 34, str(t), 11.5, anchor='middle', fill=QUIET)]
    for t in (0, 5, 10, 15):
        b += [L(XB(t), y0 - 16, XB(t), last + 16), T(XB(t), last + 34, f'{t}%', 11.5, anchor='middle', fill=QUIET)]
    for i, (n, lq, llo, lhi, h, hlo, hhi, hot) in enumerate(SC):
        y = y0 + i * step
        c, tc, w = (ACC, INK, 600) if hot else (MUTED, QUIET, 400)
        b += [T(labX, y + 4, n, 12, w, 'end', tc),
              L(XA(llo), y, XA(lhi), y, c, 7, op=0.35, cap='round'), C(XA(lq), y, 5.5, c),
              T(XA(lhi) + 10, y + 4, fa(lq), 11.5, w, fill=tc),
              L(XB(hlo), y, XB(hhi), y, c, 7, op=0.35, cap='round'), C(XB(h), y, 5.5, c),
              T(XB(hhi) + 10, y + 4, f'{h:.1f}%', 11.5, w, fill=tc)]
    return SVG(last + 46, b, top=66)


FATE = [('India 2016', [0.67, 8.90, 2.44, 60.23, 27.76]), ('S1 Shock', [2.64, 8.70, 2.61, 60.91, 25.15]),
        ('S2 Announced', [0.22, 3.62, 0.71, 29.98, 65.47]), ('S3 Phase-out', [0.00, 1.06, 0.19, 52.91, 45.84]),
        ('S4 Phase-out + AML', [0.46, 6.35, 1.14, 67.37, 24.68])]
PARTS = ['Extinguished', 'Seized, taxed or fined', 'Kept after penalty', 'Entered banks undetected',
         'Displaced (gold, FX, crypto) or paid as fees']


def f_fate():
    left, wide, y0, step, bh = 200, 440, 134, 40, 24
    tone, shade = [ACC, ACC, ACC, MUTED, MUTED], [1, 0.62, 0.3, 0.95, 0.45]
    lx, ly = [24, 150, 330, 24, 250], [78, 78, 78, 98, 98]
    b = head('Most illicit cash survives: only 1–11% is destroyed or seized in any scenario',
             'Blue = state gains · grey = illicit cash survives · means across draws (hence above the medians in Figure 4)')
    for k, p in enumerate(PARTS):
        b += [R(lx[k], ly[k] - 10, 12, 12, tone[k], rx=2, op=shade[k]), T(lx[k] + 18, ly[k], p, 11.5)]
    b.append(T(left + wide + 14, y0 - 12, 'Bite', 11.5, 600))
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
    return SVG(334, b, top=58)


CAL = [(3.0, 99.64, 99.44, 99.76), (5.0, 99.64, 99.47, 99.77), (7.1, 99.63, 99.47, 99.78), (9.0, 99.63, 99.42, 99.78),
       (11.0, 99.64, 99.42, 99.79), (13.0, 99.63, 99.23, 99.79), (15.0, 99.64, 98.50, 99.79), (17.0, 99.60, 98.38, 99.79),
       (19.0, 99.56, 97.77, 99.78), (21.1, 99.49, 97.21, 99.78), (23.0, 99.34, 97.05, 99.78), (25.1, 99.20, 96.55, 99.76),
       (26.9, 99.17, 96.14, 99.77), (29.0, 98.48, 95.56, 99.74)]


def f_calib():
    left, right, y0, bottom = 80, 680, 92, 312
    X = lambda v: left + v / 30 * (right - left)
    Y = lambda v: bottom - (v - 95) / 5 * (bottom - y0)
    b = head("India's 99.3% return rate fits any illicit share from 3% to 29%",
             'Line = median · blue band = 10th–90th percentile · grey band = ABC acceptance region (99.3 ± 0.3%)')
    b.append(T(left, y0 - 16, 'Simulated return rate', 11.5, fill=QUIET))
    for t in range(95, 101):
        b += [L(left, Y(t), right, Y(t)), T(left - 8, Y(t) + 4, f'{t}%', 11.5, anchor='end', fill=QUIET)]
    b.append(R(left, Y(99.6), right - left, Y(99.0) - Y(99.6), TINT))
    pts = ' '.join(f'{X(a):.1f},{Y(c):.1f}' for a, _, _, c in CAL) + ' ' + \
          ' '.join(f'{X(a):.1f},{Y(lo):.1f}' for a, _, lo, _ in reversed(CAL))
    b.append(f'<polygon points="{pts}" fill="{ACC}" fill-opacity="0.16"/>')
    b += [L(left, Y(99.3), right, Y(99.3), REF, 1, '4 4'), T(left + 8, Y(99.3) + 13, 'RBI: 99.3% returned', 11, fill=QUIET)]
    b.append(P('M' + ' L'.join(f'{X(a):.1f} {Y(m):.1f}' for a, m, _, _ in CAL), 'none', ACC, 2.25))
    b += [C(X(a), Y(m), 3, ACC) for a, m, _, _ in CAL]
    b.append(T(X(29.0) + 10, Y(98.48) + 4, 'median', 11.5, 600))
    b.append(L(left, bottom, right, bottom, AXIS))
    b += [T(X(t), bottom + 20, f'{t}%', 11.5, anchor='middle', fill=QUIET) for t in range(0, 31, 5)]
    b.append(T((left + right) / 2, bottom + 44, 'Assumed illicit share of demonetized cash', 11.5, anchor='middle', fill=QUIET))
    return SVG(370, b, top=58)


CAPS = [1, 2.5, 5, 7.5, 10, 15, 20]
SENS = [('Lenient scrutiny (0.3)', 0.4, [17.7, 12.2, 7.9, 6.2, 6.0, 5.8, 6.0]),
        ('Moderate scrutiny (0.5)', 0.7, [31.1, 23.3, 11.6, 6.1, 5.5, 5.1, 5.4]),
        ('Strict scrutiny (0.8)', 1.0, [41.4, 32.2, 17.6, 6.8, 6.2, 6.1, 5.6])]


def f_capacity():
    left, right, y0, bottom = 80, 680, 92, 312
    X = lambda v: left + v / 20 * (right - left)
    Y = lambda v: bottom - v / 45 * (bottom - y0)
    b = head('Once laundering capacity exceeds the illicit stock, scrutiny barely matters',
             'Scenario S1 (shock) · illicit share fixed at 10% · median of 80 draws per point')
    b.append(T(left, y0 - 16, '% of illicit cash destroyed or seized', 11.5, fill=QUIET))
    for t in range(0, 41, 10):
        b += [L(left, Y(t), right, Y(t)), T(left - 8, Y(t) + 4, f'{t}%', 11.5, anchor='end', fill=QUIET)]
    b += [L(X(10), y0, X(10), bottom, REF, 1, '4 4'),
          T(X(10) + 8, y0 + 12, 'Capacity = entire illicit stock', 11.5, fill=QUIET),
          T(X(10) + 8, y0 + 28, '(illicit share fixed at 10%)', 11.5, fill=QUIET)]
    for j, (name, op, vals) in enumerate(SENS):
        b.append(P('M' + ' L'.join(f'{X(c):.1f} {Y(v):.1f}' for c, v in zip(CAPS, vals)), 'none', ACC, 2.25, sop=op))
        b += [C(X(c), Y(v), 3.5, ACC, op=op) for c, v in zip(CAPS, vals)]
        b += [L(470, 160 + j * 20, 496, 160 + j * 20, ACC, 2.25, op=op), T(504, 164 + j * 20, name, 11.5)]
    b.append(T(X(15), Y(6) - 14, 'plateau at 5–7%', 11.5, 600, 'middle'))
    b.append(L(left, bottom, right, bottom, AXIS))
    b += [T(X(t), bottom + 20, f'{t}%', 11.5, anchor='middle', fill=QUIET) for t in range(0, 21, 5)]
    b.append(T((left + right) / 2, bottom + 44, 'Laundering capacity over the window (% of all demonetized cash)', 11.5,
               anchor='middle', fill=QUIET))
    return SVG(372, b, top=58)


PRCC_ROWS = [('Illicit share of stock', 'illicit_share'), ('Structuring (mule) capacity', 'cap_struct_total'),
             ('Detectability of structuring', 'q_struct'), ('Structuring fee', 'fee_struct'),
             ('Conversion premium', 'fee_conv'), ('Conversion capacity', 'cap_conv_total'),
             ('Bank scrutiny intensity', 'kyc_bank'), ('Amnesty tax rate', 'amnesty_tax'),
             ('Criminal (black) share', 'black_frac'), ('Detectability at dealers', 'q_conv'),
             ('Replacement ready on day 0', 'pre_supply'), ('Replacement supply rate', 'r_day'),
             ('Dealer scrutiny intensity', 'kyc_dealer')]


def f_prcc(prcc):
    panels = [('(a) Bite', 'hit'), ('(b) Laundered undetected', 'laund'), ('(c) Economic disruption', 'liq')]
    x0s, pw, y0, step = [206, 388, 570], 166, 112, 21
    last = y0 + (len(PRCC_ROWS) - 1) * step
    b = head('Bite hinges on laundering capacity; disruption hinges on replacement logistics',
             'Partial rank correlation coefficients (PRCC), scenario S1, 600 draws · |PRCC| < 0.15 is within sampling noise')
    for i, (lab, _) in enumerate(PRCC_ROWS):
        b.append(T(194, y0 + i * step + 4, lab, 11.5, anchor='end', fill=QUIET))
    for x0, (title, key) in zip(x0s, panels):
        mid = x0 + pw / 2
        X = lambda v, x0=x0: x0 + (v + 1) / 2 * pw
        b += [T(mid, 88, title, 12.5, 600, 'middle')]
        for t in (-1, -0.5, 0, 0.5, 1):
            b.append(L(X(t), y0 - 12, X(t), last + 12, AXIS if t == 0 else GRID))
            if t in (-1, 0, 1):
                b.append(T(X(t), last + 30, f'{t:g}'.replace('-', '−'), 11, anchor='middle', fill=QUIET))
        for i, (_, p) in enumerate(PRCC_ROWS):
            v, y = prcc[key][p], y0 + i * step
            strong = abs(v) >= 0.3
            x1, x2 = sorted([X(0), X(v)])
            b.append(R(x1, y - 7, x2 - x1, 14, ACC if strong else MUTED, op=1 if strong else 0.8))
            if abs(v) >= 0.15:
                lab = f'{v:+.2f}'.replace('-', '−')
                if v < 0 and X(v) - 37 < x0:
                    b.append(T(X(v) + 4, y + 4, lab, 11, 600, 'start', '#ffffff'))
                else:
                    tx, an = (X(v) + 5, 'start') if v > 0 else (X(v) - 5, 'end')
                    b.append(T(tx, y + 4, lab, 11, 600 if strong else 400, an, INK if strong else QUIET))
    return SVG(last + 44, b, top=70)


def f_evidence():
    gx0, cw, gy0, rh = 136, 200, 104, 112
    cx = lambda c: gx0 + c * cw
    ry = lambda r: gy0 + r * rh
    b = head('The largest costs are well evidenced; every benefit is small or weakly evidenced',
             "Author's qualitative assessment (Table 8) · shaded cell = the most worrying corner (large impact, strong evidence)")
    b += [R(24, 64, 60, 20, GOOD, GOOD, 1.25, 10, 0.14), T(54, 78, 'Benefit', 11.5, anchor='middle'),
          R(94, 64, 50, 20, BAD, BAD, 1.25, 10, 0.14), T(119, 78, 'Cost', 11.5, anchor='middle'),
          R(cx(2), ry(0), cw, rh, TINT)]
    for k in range(4):
        b += [L(cx(0), ry(k), cx(3), ry(k)), L(cx(k), ry(0), cx(k), ry(3))]
    for r, s in enumerate(['Large impact', 'Medium impact', 'Small impact']):
        b.append(T(gx0 - 12, ry(r) + rh / 2 + 4, s, 12, 600, 'end'))
    for c, s in enumerate(['Weak evidence', 'Moderate evidence', 'Strong evidence']):
        b.append(T(cx(c) + cw / 2, ry(3) + 22, s, 12, 600, 'middle'))
    b.append(T(cx(1) + cw / 2, ry(3) + 42, 'Strength of evidence →', 11.5, anchor='middle', fill=QUIET))
    chips = [(2, 0, 0, 0, 'Informal economy disrupted'), (2, 0, 1, 0, 'Burden on the vulnerable'),
             (1, 0, 0, 0, 'Trust and political risk'), (1, 1, 0, 0, 'Laundering via the exchange'),
             (1, 1, 1, 0, 'Shift to gold, FX, crypto'), (1, 1, 2, 0, 'Legal risk'),
             (0, 1, 0, 1, 'Broader tax base'), (0, 1, 1, 1, 'Intelligence from exchanges'),
             (2, 2, 0, 1, 'Bite on illicit cash'), (1, 2, 0, 1, 'Bulk cash harder to move'),
             (1, 2, 1, 1, 'Push to banks and digital'), (1, 2, 2, 0, 'Printing/seigniorage cost'),
             (0, 2, 0, 1, 'Deterrence signal'), (0, 2, 1, 1, 'Less vote buying'), (0, 2, 2, 0, 'Cross-border baht holders')]
    for c, r, i, pro, s in chips:
        col, y = (GOOD if pro else BAD), ry(r) + 8 + i * 33
        b += [R(cx(c) + 6, y, cw - 12, 26, col, col, 1.25, 13, 0.14), T(cx(c) + cw / 2, y + 17, s, 11.5, anchor='middle', within=(cx(c) + 6, cx(c) + cw - 6))]
    return SVG(492, b, top=54)


OPTS = [('A. Shock (S1)', [3, 3, 1, 1, 1, 2, 1]), ('B. Announced, 90 days (S2)', [2, 3, 3, 3, 3, 2, 2]),
        ('C. Phase-out (S3)', [1, 3, 5, 5, 5, 3, 4]), ('C+. Phase-out + AML (S4)', [3, 4, 4, 4, 4, 3, 4]),
        ('D. AML + cash limit (S5)', [1, 4, 4, 5, 4, 4, 5])]
CRITS = [('Bite on', 'stock'), ('Curbs', 'future use'), ('Low', 'disruption'), ('Low', 'laundering'),
         ('Low', 'legal risk'), ('Low', 'admin. cost'), ('Easy to', 'reverse')]


def f_scorecard():
    gx0, cw, gy0, rh, ch = 200, 72, 128, 40, 36
    cx = lambda j: gx0 + j * cw
    ry = lambda i: gy0 + i * rh
    ax = gx0 + 7 * cw + 30
    col = lambda s: {5: (GOOD, 0.42), 4: (GOOD, 0.24), 3: (MUTED, 0.35), 2: (BAD, 0.22), 1: (BAD, 0.42)}[s]
    avgs = [sum(v) / 7 for _, v in OPTS]
    b = head('The shock design scores lowest (1.7 of 5); AML-based options score 3.7–3.9',
             '5 options × 7 criteria · C and C+ phase out the 1,000-baht note; D keeps it')
    for j, (a, c) in enumerate(CRITS):
        b += [T(cx(j) + cw / 2, 98, a, 11, anchor='middle', within=(cx(j), cx(j) + cw)), T(cx(j) + cw / 2, 113, c, 11, anchor='middle', within=(cx(j), cx(j) + cw))]
    b.append(T(ax, 113, 'Mean', 10.5, 600, 'middle'))
    for i, (n, v) in enumerate(OPTS):
        b.append(T(gx0 - 10, ry(i) + ch / 2 + 4, n, 11.5, anchor='end'))
        for j, s in enumerate(v):
            f, o = col(s)
            b += [R(cx(j) + 2, ry(i), cw - 4, ch, f, rx=4, op=o), T(cx(j) + cw / 2, ry(i) + ch / 2 + 5, s, 13, 600, 'middle')]
        a = avgs[i]
        b.append(T(ax, ry(i) + ch / 2 + 5, f'{a:.1f}', 13, 700 if a in (max(avgs), min(avgs)) else 400, 'middle'))
    return SVG(336, b, top=80)


def f_roadmap():
    left, w, gap, by, bh = 24, 170, 10, 84, 108
    bx = lambda i: left + i * (w + gap)
    gx = lambda i: bx(i) + w + gap / 2
    b = head('A safer path: a five-year phase-out with three gates to pause or reverse',
             'Not to scale · blue frame = can start now · diamond = decision gate; failing it means pause or reverse')
    phases = [('0 Prepare', 'Months 0–12', 'Run flagship studies', 'Enact law; AML package'),
              ('1 Stop printing', 'Years 1–2', 'ATMs switch to THB 500', 'Cash-payment cap starts'),
              ('2 Withdraw', 'Years 2–5', 'Banks stop reissuing', 'Help desks for elderly'),
              ('3 End legal tender', 'After year 5', 'Redeemable at the BOT', 'Source of funds checked')]
    for i, (n, t, a, c) in enumerate(phases):
        hot = i == 0
        b += [R(bx(i), by, w, bh, ACC if hot else 'none', ACC if hot else AXIS, 2 if hot else 1.25, 8, 0.12 if hot else 1),
              T(bx(i) + 12, by + 24, n, 13, 600, within=(bx(i), bx(i) + w)),
              T(bx(i) + 12, by + 42, t, 11.5, fill=QUIET, within=(bx(i), bx(i) + w)),
              T(bx(i) + 12, by + 66, a, 11.5, within=(bx(i), bx(i) + w)),
              T(bx(i) + 12, by + 84, c, 11.5, within=(bx(i), bx(i) + w))]
    gates = [('Gate 1: evidence shows', 'the note is the problem'), ('Gate 2: liquidity normal', 'and 1,000s falling'),
             ('Gate 3: under 10% of', '1,000s remain')]
    for i, (a, c) in enumerate(gates):
        x, y = gx(i), by + bh / 2
        b += [P(f'M{x} {y - 10}l10 10l-10 10l-10 -10z', TINT, AXIS, 1.25),
              T(x, by + bh + 24, a, 11.5, 600, 'middle'), T(x, by + bh + 40, c, 11.5, anchor='middle', fill=QUIET)]
    b += [R(24, 258, 710, 36, TINT, AXIS, 1.25, 8),
          T(379, 281, 'Throughout: independent annual evaluation and monthly open data on banknotes by denomination', 11.5,
            anchor='middle')]
    return SVG(306, b, top=70)


def f_agenda():
    gx0, cw, gy0, rh = 176, 186, 100, 190
    cx = lambda c: gx0 + c * cw
    ry = lambda r: gy0 + r * rh
    b = head('Three flagship studies (★) offer high policy value; two can start with open data',
             "15 topics by policy value and data feasibility · author's assessment (Table 9) · shaded cell = start here")
    b.append(R(cx(2), ry(0), cw, rh, TINT))
    b += [L(cx(0), ry(k), cx(3), ry(k)) for k in range(3)] + [L(cx(k), ry(0), cx(k), ry(2)) for k in range(4)]
    b += [T(gx0 - 12, ry(0) + rh / 2 + 4, 'High policy value', 12, 600, 'end'),
          T(gx0 - 12, ry(1) + rh / 2 + 4, 'Moderate value', 12, 600, 'end')]
    for c, s in enumerate(['Hard-to-access data', 'Needs data partners', 'Open data, start now']):
        b.append(T(cx(c) + cw / 2, ry(2) + 22, s, 12, 600, 'middle'))
    b.append(T(cx(1) + cw / 2, ry(2) + 42, 'Data feasibility →', 11.5, anchor='middle', fill=QUIET))
    chips = [(2, 0, 0, 1, 'A3 Pre-election cash ★'), (2, 0, 1, 1, 'D1 Seized-cash premium ★'),
             (1, 0, 0, 0, 'A1 Who holds 1,000s?'), (1, 0, 1, 0, 'C1 Distributional costs'),
             (1, 0, 2, 0, 'D2 Vote-buying modes'), (1, 0, 3, 0, 'E2 Cash-payment caps'),
             (1, 0, 4, 1, 'F1 E-payment bunching ★'), (0, 0, 0, 0, 'D3 Displacement, mules'),
             (2, 1, 0, 0, 'A2 Shadow economy size'), (2, 1, 1, 0, 'B1 Cross-country (fsQCA)'),
             (2, 1, 2, 0, 'B2 Symbolic politics'), (2, 1, 3, 0, 'C2 Public acceptance'),
             (2, 1, 4, 0, 'E1 Legal authority'), (1, 1, 0, 0, 'C3 Cross-border baht'), (1, 1, 1, 0, 'F2 Model extensions')]
    for c, r, i, star, s in chips:
        y = ry(r) + 10 + i * 34
        b += [R(cx(c) + 4, y, cw - 8, 26, ACC if star else 'none', ACC if star else AXIS, 2 if star else 1.25, 13,
                0.12 if star else 1),
              T(cx(c) + cw / 2, y + 17, s, 11.5, 600 if star else 400, 'middle', within=(cx(c) + 4, cx(c) + cw - 4))]
    return SVG(532, b, top=88)


def _inter(weight):
    name = {400: 'Inter-Regular.otf', 600: 'Inter-SemiBold.otf', 700: 'Inter-Bold.otf'}.get(weight, 'Inter-Regular.otf')
    for d in ('/usr/share/fonts/opentype/inter', '/usr/local/share/fonts', os.path.expanduser('~/.fonts'),
              os.path.expanduser('~/.local/share/fonts'), os.path.expanduser('~/Library/Fonts'), '/Library/Fonts',
              'C:/Windows/Fonts'):
        if os.path.exists(os.path.join(d, name)):
            return os.path.join(d, name)
    return None


def check(name, top, h):
    """Measure every label with the real Inter metrics; report overlaps, clipping and box overflow."""
    from PIL import ImageFont
    if _inter(400) is None:
        print('note: Inter font files not found; skipping the text-overlap check')
        return []
    cache, boxes, issues = {}, [], []
    for (x, y, s, size, w, anchor, within) in TEXTS:
        key = (w, size)
        if key not in cache:
            cache[key] = ImageFont.truetype(_inter(w) or _inter(400), size=int(round(size * 8)))
        fnt = cache[key]
        wd = fnt.getlength(s) / 8
        l, t, r, bt = [v / 8 for v in fnt.getbbox(s, anchor='ls')]
        x0 = x if anchor == 'start' else (x - wd / 2 if anchor == 'middle' else x - wd)
        box = (x0 + l, y + t, x0 + r, y + bt)
        boxes.append((box, s))
        if box[0] < 2 or box[2] > 758 or box[1] < top + 1 or box[3] > h - 1:
            issues.append(f'clipped: {s!r} {tuple(round(v) for v in box)}')
        if within and (box[0] < within[0] + 4 or box[2] > within[1] - 4):
            issues.append(f'overflows box: {s!r} needs {box[2] - box[0]:.0f}px, has {within[1] - within[0] - 8:.0f}px')
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (a, sa), (b, sb) = boxes[i], boxes[j]
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 0.5 and oy > 0.5:
                issues.append(f'overlap: {sa!r} x {sb!r}')
    return issues


def to_pdf(svg_path, pdf_path):
    from weasyprint import HTML
    svg = open(svg_path, encoding='utf-8').read()
    h = float(re.search(r'viewBox="0 [0-9.]+ 760 ([0-9.]+)"', svg).group(1))
    html = (f'<html><head><meta charset="utf-8"><style>@page{{size:760px {h}px;margin:0}}body{{margin:0}}'
            f'img{{display:block;width:760px;height:{h}px}}</style></head><body><img src="{os.path.abspath(svg_path)}"></body></html>')
    HTML(string=html, base_url='/').write_pdf(pdf_path)


HERE = os.path.dirname(os.path.abspath(__file__))


def build(outdir=os.path.join(HERE, 'en', 'figs_en'), prcc_path=os.path.join(HERE, '..', 'results', 'prcc_s1.json')):
    os.makedirs(outdir, exist_ok=True)
    prcc = json.load(open(prcc_path))
    figs = [('relvalue', f_relvalue), ('bulk', f_bulk), ('trilemma', f_trilemma), ('bite', f_bite), ('fate', f_fate),
            ('calib', f_calib), ('capacity', f_capacity), ('prcc', lambda: f_prcc(prcc)), ('evidence', f_evidence),
            ('scorecard', f_scorecard), ('roadmap', f_roadmap), ('agenda', f_agenda)]
    report = {}
    for name, fn in figs:
        TEXTS.clear()
        svg = fn()
        m = re.search(r'viewBox="0 ([0-9.]+) 760 ([0-9.]+)"', svg)
        top, hh = float(m.group(1)), float(m.group(2))
        report[name] = check(name, top, top + hh)
        sp = os.path.join(outdir, f'{name}.svg')
        open(sp, 'w', encoding='utf-8').write(svg)
        to_pdf(sp, os.path.join(outdir, f'{name}.pdf'))
    return report


if __name__ == '__main__':
    for name, issues in build().items():
        print(f'{name:10s}', 'OK' if not issues else '; '.join(issues))
