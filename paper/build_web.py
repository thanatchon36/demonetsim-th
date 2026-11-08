"""Build the web reader docs/paper/ from paper/en/main.tex (same text and numbers as the PDF).

pandoc renders the LaTeX body with paper/reader.html (the thainowcast reader format): masthead, abstract, a results
strip whose numbers are read from results/, contents, numbered sections and the appendices. LaTeX that pandoc cannot
read faithfully is rewritten first: natbib citations become author-year text from the thebibliography labels,
\\ref is resolved to the numbers the PDF prints, tabularx becomes tabular, and figures point at the SVG sources.
The PDFs and the figures are copied next to the page; GitHub Pages serves docs/ at
https://thanatchon36.github.io/demonetsim-th/. Requires pandoc on PATH.

Usage: python paper/build_web.py
"""
from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
TEX = PAPER / "en" / "main.tex"
RESULTS = ROOT / "results"
OUT = ROOT / "docs" / "paper"
REPO_URL = "https://github.com/thanatchon36/demonetsim-th"
PAPER_URL = "https://thanatchon36.github.io/demonetsim-th/paper/"

TITLE = "Can Demonetization Defeat Grey Capital?"
SUBTITLE = "Evidence, a Calibrated Agent-Based Model, and a Research Agenda for Retiring Thailand's 1,000-Baht Note"
THM_COUNTERS = ("assumption", "lemma", "proposition", "hypothesis")


# --------------------------------------------------------------------------- LaTeX -> pandoc-friendly LaTeX
def env_block(tex: str, name: str, start: int = 0) -> tuple[int, int, str]:
    a = tex.index(f"\\begin{{{name}}}", start)
    b = tex.index(f"\\end{{{name}}}", a)
    return a, b + len(f"\\end{{{name}}}"), tex[a + len(f"\\begin{{{name}}}"):b]


def bibliography(tex: str) -> dict[str, tuple[str, str]]:
    """key -> (authors, year) from \\bibitem[Authors(Year)]{key}."""
    refs = {}
    for label, key in re.findall(r"\\bibitem\[(.*?)\]\{(.*?)\}", tex):
        m = re.match(r"(.*)\((.*?)\)$", label)
        refs[key] = (m.group(1).replace("~", " ").replace("\\`a", "à").strip(), m.group(2))
    return refs


def replace_citations(tex: str, refs: dict[str, tuple[str, str]]) -> str:
    def anchor(key: str, text: str) -> str:
        return f"\\hyperref[ref-{key}]{{{text}}}"

    def citep(m: re.Match) -> str:
        pre, post, keys = m.group(1), m.group(2), m.group(3).split(",")
        if post is None and pre is not None:  # \citep[p.~5]{x}: a single optional argument is the postnote
            pre, post = None, pre
        body = "; ".join(anchor(k.strip(), f"{refs[k.strip()][0]}, {refs[k.strip()][1]}") for k in keys)
        return "(" + (f"{pre} " if pre else "") + body + (f", {post}" if post else "") + ")"

    def citet(m: re.Match) -> str:
        return "; ".join(anchor(k.strip(), f"{refs[k.strip()][0]} ({refs[k.strip()][1]})") for k in m.group(1).split(","))

    tex = re.sub(r"\\citep(?:\[([^\]]*)\])?(?:\[([^\]]*)\])?\{([^}]*)\}", citep, tex)
    return re.sub(r"\\citet\{([^}]*)\}", citet, tex)


def numbering(body: str) -> dict[str, str]:
    """label -> the number LaTeX prints, walking the body in document order."""
    nums: dict[str, str] = {}
    count = dict.fromkeys(("section", "subsection", "table", "figure", "equation", *THM_COUNTERS), 0)
    appendix = False
    current = ""
    token = re.compile(
        r"\\appendix\b|\\(section|subsection)\*?\{|\\begin\{(table|figure|equation|" + "|".join(THM_COUNTERS) + r")\}"
        r"|\\label\{([^}]*)\}"
    )
    for m in token.finditer(body):
        if m.group(0) == "\\appendix":
            appendix, count["section"] = True, 0
        elif m.group(1):
            if "*" in m.group(0):
                continue
            count[m.group(1)] += 1
            if m.group(1) == "section":
                count["subsection"] = 0
                current = chr(64 + count["section"]) if appendix else str(count["section"])
            else:
                current = f"{nums_section(count, appendix)}.{count['subsection']}"
        elif m.group(2):
            count[m.group(2)] += 1
            current = str(count[m.group(2)])
        else:
            nums[m.group(3)] = current
    return nums


def nums_section(count: dict, appendix: bool) -> str:
    return chr(64 + count["section"]) if appendix else str(count["section"])


def tabular_spec(spec: str) -> str:
    """tabularx/p{} column specs -> plain l/c/r columns pandoc can read."""
    spec = re.sub(r"@\{[^}]*\}", "", spec)
    spec = re.sub(r">\{[^}]*\}", "", spec)
    spec = re.sub(r"[pmb]\{[^}]*\}", "l", spec)
    return re.sub(r"[XY]", "l", spec)


def prepare(tex: str) -> tuple[str, dict]:
    refs = bibliography(tex)
    preamble = tex[: tex.index("\\begin{document}")]
    keep = [l for l in preamble.splitlines() if l.startswith(("\\newtheorem", "\\theoremstyle", "\\newcommand{\\figw}"))]
    a, _, abstract = env_block(tex, "quote", tex.index("Abstract"))
    keywords = re.search(r"\\textbf\{Keywords\}(.*?)\\\\", tex, re.DOTALL).group(1)
    jel = re.search(r"\\textbf\{JEL codes\}(.*?)\n\\end\{quote\}", tex, re.DOTALL).group(1)
    thanks = re.search(r"\\footnotetext\[1\]\{(.*?)\}\}\n", tex, re.DOTALL).group(1)
    body = tex[tex.index("\\section{Introduction}"): tex.index("\\end{document}")]

    nums = numbering(body)
    body = replace_citations(body, refs)
    abstract = replace_citations(abstract.replace("\\small", ""), refs)
    # Appendices: unnumbered headings that carry their letter, so pandoc's arabic numbering stops at the conclusion.
    head, _, tail = body.partition("\\appendix")
    tail = re.sub(r"\\section\{([^}]*)\}\\label\{([^}]*)\}",
                  lambda m: f"\\section*{{Appendix {nums[m.group(2)]}. {m.group(1)}}}\\label{{{m.group(2)}}}", tail)
    body = head + tail
    body = re.sub(r"\\ref\{([^}]*)\}", lambda m: f"\\hyperref[{m.group(1)}]{{{nums[m.group(1)]}}}", body)
    # Numbered display equations: pandoc drops LaTeX's automatic equation numbers.
    eq = iter(range(1, 1000))
    body = re.sub(r"\\end\{equation\}", lambda m: f"\\end{{equation}}EQNUM{next(eq)}EQNUM", body)
    # Theorem-like environments: pandoc numbers them itself, from the \newtheorem lines in the preamble.
    body = re.sub(r"\\begin\{tabularx\}\{[^}]*\}\{((?:[^{}]|\{[^{}]*\})*)\}",
                  lambda m: f"\\begin{{tabular}}{{{tabular_spec(m.group(1))}}}", body)
    body = body.replace("\\end{tabularx}", "\\end{tabular}")
    body = re.sub(r"\\multicolumn\{(\d+)\}\{((?:[^{}]|\{[^{}]*\})*)\}",
                  lambda m: f"\\multicolumn{{{m.group(1)}}}{{{tabular_spec(m.group(2))}}}", body)
    body = body.replace("\\addlinespace", "")
    body = re.sub(r"\\begin\{tabular\}\{((?:[^{}]|\{[^{}]*\})*)\}",
                  lambda m: f"\\begin{{tabular}}{{{tabular_spec(m.group(1))}}}", body)
    body = re.sub(r"\\begin\{tablenotes\}(\\\w+)?", "", body).replace("\\end{tablenotes}", "")
    body = re.sub(r"\\(begin|end)\{threeparttable\}", "", body)
    body = re.sub(r"\\makecell(\[[^\]]*\])?\{([^}]*)\}", lambda m: m.group(2).replace("\\\\", " "), body)
    body = body.replace("\\item \\textit{Notes:}", "\\textit{Notes:}")
    body = re.sub(r"(figs_en/[\w-]+)\.pdf", r"\1.svg", body)
    # thebibliography -> a References section with anchors that the author-year links point at.
    a, b, bib = env_block(body, "thebibliography")
    items = re.split(r"\\bibitem\[[^\]]*\]\{([^}]*)\}", bib)[1:]
    entries = "\n\n".join(f"\\hypertarget{{ref-{k}}}{{}}{t.strip()}" for k, t in zip(items[::2], items[1::2]))
    body = body[:a] + "\\section*{References}\\label{references}\n\n" + entries + "\n\n" + body[b:]

    meta = {
        "title": TITLE, "subtitle": SUBTITLE, "author": ["Thanatchon Chongmankhong"], "date": "November 7, 2026",
        "keywords": [k.strip() for k in re.split(r"\$\\cdot\$", keywords) if k.strip()],
        "jel": ", ".join(k.strip() for k in re.split(r"\$\\cdot\$", jel) if k.strip()),
        "abstract": to_markdown(abstract), "thanks": to_markdown(thanks.replace("\n", " ")),
    }
    return "\n".join(keep) + "\n\\begin{document}\n" + body + "\\end{document}\n", meta


def to_markdown(latex: str) -> str:
    return subprocess.run(["pandoc", "--from=latex", "--to=markdown", "--wrap=none"],
                          input=latex, capture_output=True, text=True, check=True).stdout.strip()


# --------------------------------------------------------------------------- results strip
def results_strip() -> list[tuple[str, str, str, str]]:
    """(label, style, finding, detail), every number read from results/; style ref = model result, null = pending."""
    summ = pd.read_csv(RESULTS / "scenario_summary.csv").set_index("scenario")
    dm = pd.read_csv(RESULTS / "denominations.csv").set_index("note")
    prcc = json.loads((RESULTS / "prcc_s1.json").read_text())
    prior = pd.read_csv(RESULTS / "india_prior_draws.csv")
    acc = pd.read_csv(RESULTS / "india_abc_accepted.csv")
    thb = dm.loc["THB 1,000 (TH 2024)", "pct_of_gdp_pc"]
    eur = dm.loc["EUR 500 (EA 2016)", "pct_of_gdp_pc"]
    s1, s4, ind = summ.loc["S1"], summ.loc["S4"], summ.loc["IN16"]
    curve = pd.read_csv(RESULTS / "india_calibration_curve.csv")
    fits = curve.loc[curve.accept_rate > 0, "illicit_mid"]  # illicit-share bins where 99.3% is reproduced
    lo, hi = fits.min(), fits.max()
    return [
        ("Note size", "ref", f"The 1,000-baht note is worth {thb:.2f}% of GDP per capita",
         f"about {thb / eur:.0%} of the EUR 500 at its withdrawal ({eur:.2f}%); a mid-sized large note"),
        ("Shock · bite", "ref", f"An India-style shock destroys or seizes a median {s1.hit_med:.1%} of illicit cash",
         f"interquartile range {s1.hit_p25:.1%} to {s1.hit_p75:.1%}; scenario S1, 600 draws, seed 7"),
        ("Shock · disruption", "ref",
         f"Liquidity disruption {s1.liq_index_med:.0f} on an India 2016 = 100 scale",
         f"{s1.burden_vulnerable_informal_med:.0%} of it borne by vulnerable households and informal businesses"),
        ("India 2016", "ref", f"A 99.3% return rate fits illicit shares from {lo:.0%} to {hi:.0%}",
         f"ABC keeps {len(acc):,} of {len(prior):,} draws; the return rate does not identify the illicit stock"),
        ("Sensitivity", "ref",
         f"Laundering capacity drives the bite (PRCC {prcc['hit']['cap_struct_total']:+.2f})",
         f"replacement speed drives disruption (PRCC {prcc['liq']['r_day']:+.2f}); scenario S1"),
        ("Phase-out + AML", "ref", f"Bites {s4.hit_med:.1%} at a disruption index of {s4.liq_index_med:.0f}",
         f"against {ind.hit_med:.1%} and {ind.liq_index_med:.0f} for India 2016 (calibrated draws)"),
        ("Thai data", "null", "Verified Thai inputs pending",
         "statistics are approximations and parameters assumptions; Bank of Thailand banknote data replace them"),
    ]


# --------------------------------------------------------------------------- page
def number_captions(page: str) -> str:
    count = {"caption": 0, "figcaption": 0}

    def caption(m: re.Match) -> str:
        tag, attrs, para = m.group(1), m.group(2), m.group(3) or ""
        count[tag] += 1
        word = "Table" if tag == "caption" else "Figure"
        return f"<{tag}{attrs}>{para}<b>{word} {count[tag]}.</b> "

    return re.sub(r"<(caption|figcaption)(\b[^>]*)>(\s*<p>)?", caption, page)


def build() -> Path:
    if shutil.which("pandoc") is None:
        raise RuntimeError("pandoc not found; install pandoc to build the web reader")
    tex, meta = prepare(TEX.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    meta_file = OUT / ".meta.json"
    meta_file.write_text(json.dumps(meta), encoding="utf-8")
    try:
        page = subprocess.run(
            [
                "pandoc", "--from=latex", "--to=html5", "--mathml", "--wrap=none", "--standalone",
                f"--template={PAPER / 'reader.html'}", "--number-sections", "--toc", "--toc-depth=1",
                f"--metadata-file={meta_file}", "--metadata=pagetitle:DemonetSim-TH",
                "--metadata=description:Preprint: can demonetization defeat grey capital? Evidence, a calibrated "
                "agent-based model and a research agenda for retiring Thailand's 1,000-baht note.",
            ],
            input=tex, capture_output=True, text=True, check=True, cwd=str(PAPER / "en"),
        ).stdout
    finally:
        meta_file.unlink()

    page = number_captions(page)
    page = re.sub(r'(<math display="block"(?:(?!</math>).)*</math>)\s*EQNUM(\d+)EQNUM',
                  r'<span class="eq">\1<span class="eqn">(\2)</span></span>', page, flags=re.DOTALL)
    if "EQNUM" in page:
        raise RuntimeError("an equation number was not attached to its display equation")
    page = re.sub(r'<img\b([^>]*?)\s(?:style|width|height)="[^"]*"', r"<img\1", page)
    page = page.replace("<img ", '<img loading="lazy" ')
    page = re.sub(r"<table\b[^>]*>\s*<caption>(.*?)</caption>(.*?)</table>",
                  r'<div class="tbl"><p class="tcap">\1</p><div class="tscroll"><table>\2</table></div></div>',
                  page, flags=re.DOTALL)
    page = re.sub(r"<colgroup>.*?</colgroup>\s*", "", page, flags=re.DOTALL)

    items = "\n".join(
        f'<li class="r r-{style}"><span class="r-id">{html.escape(label)}</span>'
        f'<span class="r-text">{html.escape(finding)}<small>{html.escape(detail)}</small></span></li>'
        for label, style, finding, detail in results_strip()
    )
    actions = (
        '<li><a href="paper_en.pdf">Download PDF</a></li>'
        '<li><a href="paper_th.pdf">ฉบับภาษาไทย (PDF)</a></li>'
        f'<li><a href="{REPO_URL}">Code and replication</a></li>'
    )
    bib = (
        "@misc{chongmankhong2026demonetization,\n"
        "  author = {Chongmankhong, Thanatchon},\n"
        f"  title  = {{{TITLE} {SUBTITLE.replace('Thailand', '{Thailand}')}}},\n"
        "  year   = {2026},\n"
        "  note   = {Preprint},\n"
        f"  url    = {{{PAPER_URL}}}\n"
        "}"
    )
    colophon = (
        "<p>Rendered from <code>paper/en/main.tex</code> by <code>paper/build_web.py</code> (<code>make web</code>). "
        "The results strip is read from <code>results/</code> (seed 7). The PDF is authoritative.</p>"
    )
    for marker, value in (
        ("<!--ACTIONS-->", actions),
        ("<!--RESULTS-NOTE-->", "Headline numbers, read from the committed model outputs. They follow from "
                                "assumptions and approximate statistics; they are not forecasts. Amber: model "
                                "results; grey: pending."),
        ("<!--RESULTS-->", items),
        ("<!--CITE-->", f"<h2>How to cite</h2><pre><code>{html.escape(bib)}</code></pre>"),
        ("<!--COLOPHON-->", colophon),
    ):
        if marker not in page:
            raise RuntimeError(f"reader.html lacks {marker}")
        page = page.replace(marker, value)
    unresolved = re.findall(r"\\(?:cite\w*|ref)\{|\?\?|nan%", page)
    if unresolved:
        raise RuntimeError(f"unresolved LaTeX in the web reader: {sorted(set(unresolved))}")

    (OUT / "index.html").write_text(page, encoding="utf-8")
    for pdf in ("paper_en.pdf", "paper_th.pdf"):
        shutil.copyfile(PAPER / "pdf" / pdf, OUT / pdf)
    (OUT / "figs_en").mkdir(exist_ok=True)
    for name in sorted(set(re.findall(r'src="figs_en/([\w.-]+)"', page))):
        shutil.copyfile(PAPER / "en" / "figs_en" / name, OUT / "figs_en" / name)
    return OUT / "index.html"


if __name__ == "__main__":
    print(build())
