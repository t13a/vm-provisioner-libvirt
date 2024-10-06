.DELETE_ON_ERROR:
MAKEFLAGS += --no-builtin-rules --no-builtin-variables --warn-undefined-variables
SHELL := bash -euo pipefail

DOCKER := docker
DOCKER_COMPOSE := docker compose
EXAMPLES := advanced basic
VMP := .pyinstaller/dist/vmp

.PHONY: init
init: .env
	mkdir -pv $(shell hack/dotenv.sh -- printenv WORK_DIR)

.env:
	hack/dotenvgen.sh > $@

.PHONY: up
up: .env
	$(DOCKER_COMPOSE) up -d

.PHONY: down
down: .env
	$(DOCKER_COMPOSE) down

.PHONY: build
build: .env
	$(DOCKER_COMPOSE) build

.PHONY: exec
exec: CMD := bash
exec: .env
	@$(DOCKER_COMPOSE) exec main $(CMD)

.PHONY: bundle
bundle: $(VMP)

$(VMP): .env
	mkdir -pv .pyinstaller
	$(DOCKER_COMPOSE) run --rm -v $$(pwd)/.pyinstaller:/mnt/pyinstaller:rw -w /mnt/pyinstaller main pyinstaller \
		--clean \
		--noconfirm \
		--onefile \
		--collect-data vmp \
		/mnt/src/scripts/vmp

.PHONY: examples
examples: $(addprefix examples/,$(EXAMPLES))

define example_rule
.PHONY: examples/$(1)
examples/$(1): $(VMP)
	$(MAKE) -C examples/$(1) clean gen VMP=$(PWD)/$(VMP)

endef
$(eval $(foreach _,$(EXAMPLES),$(call example_rule,$_)))
