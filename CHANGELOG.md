# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Zenodo DOI [10.5281/zenodo.24050061](https://doi.org/10.5281/zenodo.24050061) (all versions; v1.1.0 is 10.5281/zenodo.24050062) in
  `CITATION.cff`, the README, the web reader and the Hugging Face dataset card.

## [1.1.0] - 2026-11-08

### Added
- MIT license.
- Web reader for the English paper, `docs/paper/index.html`, built from `paper/en/main.tex` by `paper/build_web.py`
  (`make web`) and served at <https://thanatchon36.github.io/demonetsim-th/paper/>. Its results strip is read from
  `results/`.
- README banner `docs/assets/banner.png` (`make banner`), drawn from the S1 median bite in `results/`.
- Test suite (`make test`): denomination and bulk figures, accounting identities and comparative statics of the
  model, ABC acceptance, and a check that the committed `results/` carry the numbers the paper quotes. CI runs it on
  every push and pull request.
- Dataset on Hugging Face, [`thanatchon36/demonetsim-th`](https://huggingface.co/datasets/thanatchon36/demonetsim-th)
  (CC BY 4.0): every file in `results/` plus the scenario priors and holder groups as `inputs/`, built by
  `scripts/export_hf.py`.
- Zenodo archiving of releases (`.zenodo.json`); DOI badge in the README.
- `pyproject.toml`, `make setup` (uv, Python 3.12) and `CHANGELOG.md`.

### Changed
- The Thai paper is set in the same arXiv preprint layout as the English one: `paper/build_th.py` converts
  `paper/paper_th.md` to LaTeX with pandoc (`paper/template_th.tex`) and compiles it with tectonic, with Times for
  Latin text and Sarabun (bundled in `paper/fonts/`) for Thai. Figure labels are set by XeTeX over shapes converted
  by svglib, so the Thai build no longer needs WeasyPrint. Author: ธนัชชนม์ จงมั่นคง.
- Dependencies moved from `requirements.txt` to `pyproject.toml` (core, `paper` and `dev` extras).
- `tools/` renamed to `scripts/`.
- `CITATION.cff` describes the software and cites the paper as the preferred citation.

## [1.0.0] - 2026-11-07

### Added
- DemonetSim-TH (`model/demonet_sim_th.py`): denomination metrics, bulk of THB 10 million, replacement logistics and
  seigniorage, honest-holder liquidity gap, agent-based choices of illicit holders under capacity-constrained
  laundering, Monte Carlo scenarios S1–S4 and rejection ABC calibration to India's 99.3% return rate.
- Post-processing (`model/analysis.py`): PRCC global sensitivity for S1, bootstrap standard errors of the medians and
  ABC prior/posterior summaries.
- Model outputs at seed 7 in `results/`.
- English paper in arXiv preprint format (`paper/en/main.tex`, 12 vector figures with an automatic text-overlap check)
  and its Thai-language companion (`paper/paper_th.md`, built with WeasyPrint); compiled PDFs in `paper/pdf/`.
- Master prompt used to structure the research (`prompts/master_prompt_th.md`).

[Unreleased]: https://github.com/thanatchon36/demonetsim-th/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/thanatchon36/demonetsim-th/releases/tag/v1.1.0
