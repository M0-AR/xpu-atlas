PYTHON ?= python3
export PYTHONPATH := src:.

.PHONY: help install fetch claims analyze bench figures report sim preview paper-check test pipeline all docker-build docker-run clean

help:
	@echo "XPU-Atlas targets:"
	@echo "  install       install python dependencies (editable)"
	@echo "  fetch         refresh live public-data snapshots (network required)"
	@echo "  claims        validate the claim ledger and compute evidence audit"
	@echo "  analyze       bibliometric / attention / market analyses from snapshots"
	@echo "  bench         refresh host CPU microbenchmarks (hardware-dependent; not part of all)"
	@echo "  figures       render publication-quality figures"
	@echo "  report        render docs/EVIDENCE.md and docs/RESULTS.md"
	@echo "  sim           screen hypothetical architectures and render the Pareto report"
	@echo "  preview       rebuild the browser bundle and GitHub Pages entry point"
	@echo "  paper-check   enforce README/paper consistency with generated results"
	@echo "  test          run the test suite"
	@echo "  pipeline      claims + analyze + figures + report + sim + preview + paper-check"
	@echo "  all           test + pipeline (offline, reproducible default)"
	@echo "  docker-build  build the container image"
	@echo "  docker-run    run the full pipeline in docker compose"

install:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e . --no-deps

fetch:
	$(PYTHON) -m xpu_atlas.fetch_live

claims:
	$(PYTHON) -m xpu_atlas.claims

analyze:
	$(PYTHON) -m xpu_atlas.analyze

bench:
	$(PYTHON) -m xpu_atlas.bench

figures:
	$(PYTHON) -m xpu_atlas.figures

report:
	$(PYTHON) -m xpu_atlas.report

sim:
	$(PYTHON) -m sim.run

preview:
	$(PYTHON) scripts/sync_preview.py

paper-check:
	$(PYTHON) -m xpu_atlas.paper_check

test:
	$(PYTHON) -m pytest

pipeline: claims analyze figures report sim preview paper-check

all: pipeline test

docker-build:
	docker compose build

docker-run:
	docker compose up --build --abort-on-container-exit

clean:
	rm -f results/evidence_audit.json results/analysis.json results/summary.json results/simulation.json results/simulation.csv figures/*.png docs/EVIDENCE.md docs/RESULTS.md docs/SIMULATION.md index.html
