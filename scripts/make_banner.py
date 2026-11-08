"""README images: banner -> docs/assets/banner.png (1680x624, the thainowcast banner layout) and
preview -> docs/assets/preview.png (Figure 4 of the paper, rendered from its vector PDF on a white plate).

Left: a grid of 1,000 tiles, one per unit of illicit cash; the amber tiles are the share destroyed or seized by an
India-style shock (scenario S1 median bite, read from results/scenario_summary.csv). Right: name, tagline, methods.

Usage: python scripts/make_banner.py   (the preview needs pypdfium2, in the paper extra)
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BG, AMBER, INK, MUTED, TILE = "#03060d", "#f5a623", "#e8ecf4", "#8f9bb3", "#243049"


def main() -> Path:
    hit = float(pd.read_csv(ROOT / "results" / "scenario_summary.csv").set_index("scenario").loc["S1", "hit_med"])
    W, H, dpi = 1680, 624, 100
    fig = plt.figure(figsize=(W / dpi, H / dpi), dpi=dpi, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    ax.set_facecolor(BG)

    # 25 x 40 tiles shaped like banknotes (162 x 72 mm, the 1,000-baht note)
    cols, rows = 25, 40
    x0, y0, tw, th, gx, gy = 70, 40, 13.2, 5.9, 3.0, 8.7
    rng = np.random.default_rng(7)
    lit = set(rng.choice(cols * rows, size=round(hit * cols * rows), replace=False).tolist())
    for i in range(cols * rows):
        r, c = divmod(i, cols)
        on = i in lit
        ax.add_patch(FancyBboxPatch((x0 + c * (tw + gx), y0 + r * (th + gy)), tw, th,
                                    boxstyle="round,pad=0,rounding_size=1.2", lw=0,
                                    fc=AMBER if on else TILE, alpha=1 if on else 0.9))

    tx = 590
    ax.text(tx, 218, "demonetsim-th", color=AMBER, fontsize=58, fontweight="bold", va="center")
    ax.text(tx, 320, "Can demonetization defeat grey capital?", color=INK, fontsize=21, va="center")
    ax.text(tx, 357, "An agent-based model of retiring Thailand's 1,000-baht note", color=INK, fontsize=21,
            va="center")
    ax.text(tx, 452, "12 episodes · ABC calibration to India 2016 · Monte Carlo · PRCC sensitivity", color=MUTED,
            fontsize=15, va="center")
    ax.text(W - 25, 594, f"Each tile is 0.1% of the illicit cash stock; amber: destroyed or seized by an India-style "
            f"shock (median {hit:.1%}) · DemonetSim-TH, scenario S1, seed 7", color=MUTED, fontsize=10, ha="right",
            va="center")

    out = ROOT / "docs" / "assets" / "banner.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=dpi, facecolor=BG)
    plt.close(fig)
    return out


def preview() -> Path:
    import pypdfium2 as pdfium
    from PIL import Image

    page = pdfium.PdfDocument(str(ROOT / "paper" / "en" / "figs_en" / "bite.pdf"))[0]
    img = page.render(scale=3).to_pil().convert("RGB")
    pad = 48
    plate = Image.new("RGB", (img.width + 2 * pad, img.height + 2 * pad), "white")
    plate.paste(img, (pad, pad))
    out = ROOT / "docs" / "assets" / "preview.png"
    plate.save(out, optimize=True)
    return out


if __name__ == "__main__":
    print(main())
    print(preview())
