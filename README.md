# DemonetSim-TH: Can Demonetization Defeat Grey Capital?

**Author:** Thanatchon Chongmankhong · **Status:** preprint draft, 7 November 2026

This repository contains the paper *Can Demonetization Defeat Grey Capital? Evidence, a Calibrated Agent-Based Model,
and a Research Agenda for Retiring Thailand's 1,000-Baht Note*, its Thai-language companion, and **DemonetSim-TH**, the
agent-based simulation model behind its results.

> งานวิจัยนี้ประเมินข้อเสนอยกเลิกธนบัตร 1,000 บาทเพื่อปราบทุนเทา–ทุนดำ ด้วยบทเรียนจาก 12 กรณีต่างประเทศ
> แบบจำลองตัวแทนที่ปรับเทียบกับอินเดีย 2016 และวาระการวิจัยสำหรับประเทศไทย

## Key findings

- The 1,000-baht note is worth 0.38% of GDP per capita: a mid-sized "large note", about a quarter of the EUR 500 at its
  withdrawal.
- An India-style shock destroys or seizes a median 7.7% of illicit cash while causing about one sixth of India's
  liquidity disruption, roughly 90% of it borne by vulnerable and informal holders.
- India's 99.3% return rate is consistent with illicit shares from 3% to 29%, so it does not identify the illicit stock.
- The bite of any design hinges on laundering capacity relative to the illicit stock; disruption hinges on replacement
  logistics. A phase-out combined with anti-money-laundering measures bites 6.1% at negligible liquidity cost.

## Repository structure

```
demonetsim-th/
├── model/
│   ├── demonet_sim_th.py     # DemonetSim-TH: scenarios, Monte Carlo, ABC calibration, logistics
│   └── analysis.py           # PRCC global sensitivity, bootstrap SEs, ABC prior/posterior summary
├── results/                  # model outputs at seed 7 (CSV, PNG, prcc_s1.json, summary_stats.txt)
├── paper/
│   ├── en/
│   │   ├── main.tex          # English paper, arXiv preprint format (pdflatex)
│   │   └── figs_en/          # 12 vector figures (PDF) and their SVG sources
│   ├── figures.py            # shared SVG helpers + Thai figure set
│   ├── figures_en.py         # English figure set + automatic text-overlap checker
│   ├── build_th.py           # Thai paper builder (HTML/CSS -> PDF via WeasyPrint)
│   ├── paper_th.md           # Thai manuscript
│   └── pdf/                  # compiled papers: paper_en.pdf, paper_th.pdf
├── prompts/
│   └── master_prompt_th.md   # master prompt used to structure the research (Thai)
├── tools/
│   └── check_whitespace.py   # measures blank space on every page of a PDF
├── Makefile
├── requirements.txt
└── CITATION.cff
```

## Reproducing the results

```bash
pip install -r requirements.txt
make all
```

or step by step:

```bash
python model/demonet_sim_th.py --draws 600 --seed 7 --out results   # simulation, a few minutes
python model/analysis.py --results results                          # PRCC, bootstrap SEs, ABC summary
python paper/figures_en.py                                          # 12 figures + overlap check
cd paper/en && pdflatex main.tex && pdflatex main.tex               # English paper
python paper/build_th.py                                            # Thai paper
make arxiv                                                          # arXiv upload package in build/
```

`figures_en.py` measures every label with the real font metrics and reports overlapping labels, clipping and text that
overflows its box; it should print `OK` for all 12 figures.

## Requirements

- Python 3.10+ with the packages in `requirements.txt`.
- A TeX distribution with `pdflatex` and standard packages (mathptmx, natbib, booktabs, tabularx, threeparttable,
  titlesec, fancyhdr, hyperref).
- WeasyPrint needs the Pango system library (version 1.44 or later).
- Fonts: Inter for the English figures; Sarabun and IBM Plex Sans Thai for the Thai paper. All are available from
  Google Fonts under the SIL Open Font License.

## Data caveats

Statistics on Thailand and on the international episodes are approximations compiled without access to live sources,
and model parameters are assumptions. Verify them against primary sources, in particular Bank of Thailand banknote
statistics, before citing the results or using them for policy. The model is a thinking tool, not a forecast.

## AI assistance

The paper, code and figures were drafted with AI assistance (Claude, Anthropic). `prompts/master_prompt_th.md` contains
the master prompt used to structure the research.

## Citation

```bibtex
@misc{chongmankhong2026demonetization,
  author = {Chongmankhong, Thanatchon},
  title  = {Can Demonetization Defeat Grey Capital? Evidence, a Calibrated Agent-Based Model,
            and a Research Agenda for Retiring {Thailand}'s 1,000-Baht Note},
  year   = {2026},
  note   = {Preprint}
}
```

## License

No license has been chosen yet. Until one is added, all rights are reserved by the author.
