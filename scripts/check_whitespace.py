import sys, pypdfium2 as pdfium, numpy as np
DPI = 100
def gaps(path, verbose=True):
    pdf = pdfium.PdfDocument(path); out = []
    for i in range(len(pdf)):
        im = np.asarray(pdf[i].render(scale=DPI / 72).to_pil().convert('L'))
        H = im.shape[0]
        top, bot = int(1.0 * DPI), int(10.0 * DPI)            # text block of a letter page with 1in margins
        ink = (im[top:bot, int(1.0 * DPI):-int(1.0 * DPI)] < 200).any(axis=1)
        rows = np.where(ink)[0]
        if len(rows) == 0: out.append((i + 1, 9.0, 9.0)); continue
        bottom_gap = (bot - top - 1 - rows[-1]) / DPI
        d = np.diff(rows); inner = (d.max() - 1) / DPI if len(d) else 0
        out.append((i + 1, round(bottom_gap, 2), round(inner, 2)))
    if verbose:
        for p, b, g in out:
            flag = '  <-- ' + ('bottom gap' if b > 1.0 else '') + (' inner gap' if g > 0.8 else '') if (b > 1.0 or g > 0.8) else ''
            print(f'p{p:02d} bottom {b:4.2f} in  largest inner {g:4.2f} in{flag}')
    return out
if __name__ == '__main__':
    gaps(sys.argv[1])
