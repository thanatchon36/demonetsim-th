"""LinkedIn launch poster -> docs/assets/linkedin_poster.png (1440x1800, 4:5; the thainowcast poster layout).

The waffle shows where Thailand's illicit cash goes in an India-style shock: 1,000 tiles shaped like 1,000-baht
notes, coloured by fate (means over the 600 S1 draws, as in Figure 5 of the paper). Every number is read from
results/. Type: Sarabun (paper/fonts/).

Usage: python scripts/make_poster.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "paper" / "fonts"
BG, AMBER, CREAM, INK, MUTED, RULE = "#03060d", "#f5a623", "#ffe8a3", "#e8ecf4", "#8f9bb3", "#1c2740"
FATE = {  # key: (colour, label colour)
    "hit": ("#f5a623", "#f5a623"),
    "regularized": ("#9c7428", "#c9a25a"),
    "laundered": ("#4d6aa3", "#8fb0ec"),
    "displaced": ("#2b3448", "#a3adc2"),
}
DOI = "10.5281/zenodo.24050061"


def font(weight: str, size: float) -> dict:
    return {"fontproperties": FontProperties(fname=FONTS / f"Sarabun-{weight}.ttf", size=size)}


def main() -> Path:
    summ = pd.read_csv(ROOT / "results" / "scenario_summary.csv").set_index("scenario")
    dm = pd.read_csv(ROOT / "results" / "denominations.csv").set_index("note")
    curve = pd.read_csv(ROOT / "results" / "india_calibration_curve.csv")
    s1, s4 = summ.loc["S1"], summ.loc["S4"]
    share = {"hit": s1.extinguished_mean + s1.captured_mean, "regularized": s1.regularized_mean,
             "laundered": s1.laundered_mean, "displaced": s1.displaced_mean}
    total = sum(share.values())
    tiles = {k: round(1000 * v / total) for k, v in share.items()}
    tiles["laundered"] += 1000 - sum(tiles.values())  # rounding remainder
    fits = curve.loc[curve.accept_rate > 0, "illicit_mid"]

    W, H, dpi = 1440, 1800, 100
    fig = plt.figure(figsize=(W / dpi, H / dpi), dpi=dpi, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    # faint blue glow behind the waffle
    yy, xx = np.mgrid[0:H:4, 0:W:4]
    glow = np.exp(-(((xx - 1090) / 520) ** 2 + ((yy - 700) / 640) ** 2))
    ax.imshow(glow, extent=(0, W, H, 0), cmap=matplotlib.colors.LinearSegmentedColormap.from_list(
        "g", [BG, "#0d1a33"]), vmin=0, vmax=1, zorder=0, interpolation="bilinear")

    # header
    ax.text(94, 82, "DEMONETSIM-TH", color=AMBER, va="center", **font("Bold", 20))
    ax.text(368, 82, "can demonetization defeat grey capital?", color=MUTED, va="center", **font("Regular", 18))

    # hero
    ax.text(80, 268, "99.3%", color=AMBER, va="center", **font("Bold", 150))
    ax.text(100, 420, "came back.", color=CREAM, va="center", **font("Regular", 46))
    for i, line in enumerate(["India cancelled 86% of its cash", "overnight in 2016. Almost all of it",
                              "returned to the banks."]):
        ax.text(100, 500 + i * 46, line, color=INK, va="center", **font("Regular", 23))
    for i, line in enumerate(["Would retiring Thailand's", "1,000-baht note do better?"]):
        ax.text(100, 660 + i * 48, line, color=AMBER, va="center", **font("SemiBold", 25))

    # waffle: 20 x 50 tiles, filled row by row in order of fate
    cols, rows, x0, y0, pw, ph, tw, th = 20, 50, 846, 150, 25.5, 22.4, 21.0, 9.4
    order = [k for k in FATE for _ in range(tiles[k])]
    first_row = {}
    for i, k in enumerate(order):
        r, c = divmod(i, cols)
        first_row.setdefault(k, (r, c))
        ax.add_patch(FancyBboxPatch((x0 + c * pw, y0 + r * ph), tw, th, boxstyle="round,pad=0,rounding_size=1.6",
                                    lw=0, fc=FATE[k][0], zorder=2))
    last_row = {k: (sum(tiles[j] for j in list(FATE)[: list(FATE).index(k) + 1]) - 1) // cols for k in FATE}
    ax.text(x0 + cols * pw / 2, y0 + rows * ph + 22, "1,000 tiles = the illicit cash held in 1,000-baht notes",
            color=MUTED, ha="center", va="center", **font("Regular", 13))
    ax.text(x0 + cols * pw / 2, y0 + rows * ph + 46, "India-style shock in Thailand · mean of 600 simulations",
            color=MUTED, ha="center", va="center", **font("Regular", 13))

    labels = {
        "hit": ("Destroyed or seized", f"{share['hit']:.0%} of illicit cash"),
        "laundered": ("Enters banks undetected", f"{share['laundered']:.0%}, through mules and deposits"),
        "displaced": ("Moves into gold, FX, crypto", f"{share['displaced']:.0%}, or paid as laundering fees"),
    }
    label_y = {"hit": 810, "laundered": 1000, "displaced": 1150}
    for k, (head, sub) in labels.items():
        ly = label_y[k]
        ax.text(712, ly, head, color=FATE[k][1], ha="right", va="center", **font("SemiBold", 22))
        ax.text(712, ly + 36, sub, color=INK if k != "displaced" else MUTED, ha="right", va="center",
                **font("Regular", 16))
        ty = y0 + ((first_row[k][0] + last_row[k]) / 2) * ph + th / 2
        if k == "hit":  # the dim-amber tiles after the amber block
            ax.text(712, ly + 68, f"+{share['regularized']:.0%} kept after a penalty", color=FATE["regularized"][1],
                    ha="right", va="center", **font("Regular", 15))
        ax.plot([722, x0 - 8], [ly + 4, ty], color=FATE[k][1], lw=1.0, alpha=0.7, zorder=1)
        ax.plot([x0 - 8], [ty], marker="o", ms=4, mfc="none", mec=FATE[k][1], zorder=3)

    # stats row
    ax.plot([94, 1346], [1330, 1330], color=RULE, lw=1.5)
    thb = dm.loc["THB 1,000 (TH 2024)", "pct_of_gdp_pc"]
    stats = [
        (f"{thb:.2f}%", ["of GDP per capita: a", "mid-sized large note"]),
        (f"{s1.burden_vulnerable_informal_med:.0%}", ["of the disruption hits the", "vulnerable and informal"]),
        (f"{fits.min() * 100:.0f}–{fits.max():.0%}", ["illicit shares all fit", "India's 99.3% return"]),
        (f"{s4.hit_med:.1%}", ["bite of a phase-out + AML,", "with no cash crunch"]),
    ]
    for i, (num, lines) in enumerate(stats):
        x = 94 + i * 324
        ax.text(x, 1410, num, color=AMBER, va="center", **font("Bold", 44))
        for j, line in enumerate(lines):
            ax.text(x, 1476 + j * 30, line, color=MUTED, va="center", **font("Regular", 16))

    # links box
    ax.add_patch(FancyBboxPatch((86, 1548), 1268, 182, boxstyle="round,pad=0,rounding_size=14", lw=1.5,
                                ec=RULE, fc="#0a1222", zorder=1))
    ax.text(130, 1598, "Code + paper (English and Thai)", color=MUTED, va="center", **font("Regular", 15))
    ax.text(130, 1634, "github.com/thanatchon36/demonetsim-th", color=INK, va="center", **font("Regular", 20))
    ax.text(764, 1598, "Dataset", color=MUTED, va="center", **font("Regular", 15))
    ax.text(764, 1634, "hf.co/datasets/thanatchon36/demonetsim-th", color=INK, va="center", **font("Regular", 20))
    ax.text(130, 1686, "A thinking tool, not a forecast: Thai inputs are approximations and model parameters are "
            "assumptions.", color=MUTED, va="center", **font("Regular", 13))

    # footer
    ax.text(94, 1766, f"Thanatchon Chongmankhong  ·  views are my own  ·  DOI {DOI}", color=MUTED, va="center",
            **font("Regular", 14))
    ax.text(1346, 1766, "thanatchon36.github.io/demonetsim-th", color=MUTED, ha="right", va="center",
            **font("Regular", 12))

    out = ROOT / "docs" / "assets" / "linkedin_poster.png"
    fig.savefig(out, dpi=dpi, facecolor=BG)
    plt.close(fig)
    return out


if __name__ == "__main__":
    print(main())
