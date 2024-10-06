#!/usr/bin/env bash

set -euo pipefail

for script in /entrypoint.d/*.sh
do
  "${script}"
done

exec "${@}"
