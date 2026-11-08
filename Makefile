PY ?= python3

.PHONY: all simulate analysis figures paper-en paper-th arxiv clean

all: simulate analysis figures paper-en paper-th

simulate:
	$(PY) model/demonet_sim_th.py --draws 600 --seed 7 --out results

analysis:
	$(PY) model/analysis.py --results results

figures:
	$(PY) paper/figures_en.py

paper-en:
	cd paper/en && pdflatex -interaction=nonstopmode main.tex >/dev/null && pdflatex -interaction=nonstopmode main.tex >/dev/null
	cp paper/en/main.pdf paper/pdf/paper_en.pdf

paper-th:
	$(PY) paper/build_th.py

arxiv:
	rm -rf build/arxiv_source && mkdir -p build/arxiv_source/figs_en build/arxiv_source/anc
	cp paper/en/main.tex build/arxiv_source/
	cp paper/en/figs_en/*.pdf build/arxiv_source/figs_en/
	cp model/demonet_sim_th.py build/arxiv_source/anc/
	cd build && $(PY) -m zipfile -c arxiv_source.zip arxiv_source/

clean:
	rm -f paper/en/*.aux paper/en/*.log paper/en/*.out paper/en/main.pdf
	rm -rf build paper/figs_th
