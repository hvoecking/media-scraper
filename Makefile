# Preamble from https://tech.davis-hansson.com/p/make/
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

help:
	@cat $(MAKEFILE_LIST) \
		| sed -nr 's/^\.PHONY: ([^: ]+) ##/\1/p' Makefile \
		| awk '{printf "\033[36m%-16s\033[0m", $$1; $$1=""; print $$0}' \
	;
.PHONY: help ## Print help for all PHONY toplevel targets

.DEFAULT_GOAL := help
PYTHON ?= /usr/bin/env python

lint:
	docker run -e RUN_LOCAL=true -v "$$PWD:/tmp/lint" github/super-linter
.PHONY: lint ## Run GitHub's super-linter

build: tagesschau-dl
.PHONY: build ## Build the project

tagesschau-dl: tagesschau_dl/*.py
	mkdir -p zip/tagesschau_dl
	cp -pPR tagesschau_dl/*.py zip/tagesschau_dl/
	touch -t 200001010101 zip/tagesschau_dl/*.py
	mv zip/tagesschau_dl/__main__.py zip/
	(cd zip && zip -q ../tagesschau-dl tagesschau_dl/*.py __main__.py)
	rm -rf zip
	echo '#!$(PYTHON)' > tagesschau-dl
	cat tagesschau-dl.zip >> tagesschau-dl
	rm tagesschau-dl.zip
	chmod a+x tagesschau-dl
