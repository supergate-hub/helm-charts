# Makefile for linting GitHub Actions workflows with actionlint
SHELL := /usr/bin/env bash
.ONESHELL:
.SHELLFLAGS := -eo pipefail -c
.DEFAULT_GOAL := lint-actions

# ---- Config ----
WORKFLOWS_DIR ?= .github/workflows
ACTIONLINT_PKG := github.com/rhysd/actionlint/cmd/actionlint@latest
ACTIONLINT ?= $(shell command -v actionlint 2>/dev/null)

EXTRA_ARGS ?=

SHELLCHECK ?=
PYFLAKES ?=

.PHONY: help
help: 
	@grep -E '^[a-zA-Z0-9_.-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk -F':|##' '{printf "\033[36m%-20s\033[0m %s\n", $$1, $$3}'

.PHONY: ensure-actionlint
ensure-actionlint: 
ifeq ($(ACTIONLINT),)
	@echo "[info] actionlint not found. Trying to install via 'go install'..."
	@if ! command -v go >/dev/null 2>&1; then \
		echo "[error] go toolchain not found. Install Go or use 'make lint-actions-docker'"; \
		exit 1; \
	fi
	@GO111MODULE=on go install $(ACTIONLINT_PKG)
	@$(eval ACTIONLINT := $(shell command -v actionlint 2>/dev/null))
	@if [ -z "$(ACTIONLINT)" ]; then \
		echo "[error] actionlint install failed. Consider 'make lint-actions-docker'"; \
		exit 1; \
	fi
else
	@true
endif

.PHONY: install-actionlint
install-actionlint: 
	@GO111MODULE=on go install $(ACTIONLINT_PKG)
	@echo "Installed to: $$(go env GOPATH)/bin/actionlint"

.PHONY: update-actionlint
update-actionlint: 
	@GO111MODULE=on go install github.com/rhysd/actionlint/cmd/actionlint@latest
	@echo "Updated actionlint to latest (in GOPATH/bin)."

# ---- Lint ----
.PHONY: lint-actions
lint-actions: ensure-actionlint 
	@test -d "$(WORKFLOWS_DIR)" || { echo "[warn] $(WORKFLOWS_DIR) not found"; exit 0; }
	@echo "[run] actionlint on $(WORKFLOWS_DIR)"
	@OUTPUT=$$($(ACTIONLINT) -oneline \
		$(EXTRA_ARGS) \
		$(if $(SHELLCHECK),-shellcheck=$(SHELLCHECK),) \
		$(if $(PYFLAKES),-pyflakes=$(PYFLAKES),) 2>&1); \
	EXIT_CODE=$$?; \
	if [ $$EXIT_CODE -ne 0 ]; then \
		echo "$$OUTPUT"; \
		echo "[error] actionlint found issues in workflow files"; \
		exit 1; \
	fi

.PHONY: ci
ci: lint-actions 
