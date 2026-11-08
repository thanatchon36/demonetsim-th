PY ?= .venv/bin/python

.PHONY: setup simulate analysis figures paper-en paper-th paper web banner arxiv test all clean

setup:          ## create venv and install the dependencies (needs uv)
	uv venv .venv --python 3.12
	uv pip install --python .venv/bin/python -r pyproject.toml --extra dev --extra paper

simulate:       ## scenarios, Monte Carlo, ABC calibration, logistics -> results/ (seed 7, a few minutes)
	$(PY) model/demonet_sim_th.py --draws 600 --seed 7 --out results

analysis:       ## PRCC sensitivity, bootstrap SEs, ABC prior/posterior -> results/prcc_s1.json, summary_stats.txt
	$(PY) model/analysis.py --results results

figures:        ## 12 English vector figures + automatic text-overlap check -> paper/en/figs_en/
	$(PY) paper/figures_en.py

paper-en:       ## English paper (pdflatex, arXiv preprint format) -> paper/pdf/paper_en.pdf
	cd paper/en && pdflatex -interaction=nonstopmode main.tex >/dev/null && pdflatex -interaction=nonstopmode main.tex >/dev/null
	cp paper/en/main.pdf paper/pdf/paper_en.pdf

paper-th:       ## Thai paper, arXiv preprint format (pandoc + tectonic) -> paper/pdf/paper_th.pdf
	$(PY) paper/build_th.py

paper: paper-en paper-th web

web:            ## web reader -> docs/paper/index.html (pandoc), served at https://thanatchon36.github.io/demonetsim-th/paper/
	$(PY) paper/build_web.py

banner:         ## README images -> docs/assets/banner.png, docs/assets/preview.png
	$(PY) scripts/make_banner.py

arxiv:          ## arXiv upload package -> build/arxiv_source.zip
	rm -rf build/arxiv_source && mkdir -p build/arxiv_source/figs_en build/arxiv_source/anc
	cp paper/en/main.tex build/arxiv_source/
	cp paper/en/figs_en/*.pdf build/arxiv_source/figs_en/
	cp model/demonet_sim_th.py build/arxiv_source/anc/
	cd build && $(PY) -m zipfile -c arxiv_source.zip arxiv_source/

test:
	$(PY) -m pytest -q

all: simulate analysis figures paper

clean:
	rm -f paper/en/*.aux paper/en/*.log paper/en/*.out paper/en/main.pdf
	rm -rf build paper/figs_th
