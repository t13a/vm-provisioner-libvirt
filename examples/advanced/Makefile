.DELETE_ON_ERROR:
MAKEFLAGS += --no-builtin-rules --no-builtin-variables --warn-undefined-variables
SHELL := bash -euo pipefail

VMP = ./vmp
VMP_URL = https://github.com/t13a/vm-provisioner-libvirt/releases/latest/download/vmp

export VMP_GEN_BASE_DIR := provisioners
export VMP_REGISTRY := registry/**/*.yaml

.PHONY: init
init: $(VMP)

$(VMP):
	mkdir -p $(@D)
	curl -L $(VMP_URL) -o $@
	chmod a+x $@

.PHONY: gen
gen:
	$(VMP) gen

.PHONY: clean
clean:
	$(VMP) list | xargs -I{} rm -rfv $(VMP_GEN_BASE_DIR)/{}

.PHONY: exec
exec: CMD = bash
exec:
	$(CMD)
