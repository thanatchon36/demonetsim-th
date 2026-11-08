# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- MIT license.
- Web reader for the English paper, `docs/paper/index.html`, built from `paper/en/main.tex` by `paper/build_web.py`
  (`make web`) and served at <https://thanatchon36.github.io/demonetsim-th/paper/>. Its results strip is read from
  `results/`.
- README banner `docs/assets/banner.png` (`make banner`), drawn from the S1 median bite in `results/`.
- Test suite (`make test`): denomination and bulk figures, accounting identities and comparative statics of the
  model, ABC acceptance, and a check that the committed `results/` carry the numbers the paper quotes. CI runs it on
  every push and pull request.
- `pyproject.toml`, `make setup` (uv, Python 3.12), `CHANGELOG.md` and `.zenodo.json`.

### Changed
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
