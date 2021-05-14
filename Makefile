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
