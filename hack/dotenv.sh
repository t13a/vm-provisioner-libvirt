#!/usr/bin/env bash

set -euo pipefail

if [ "${1:-}" = -- -a -f .env ]
then
    set -a
    . .env
    set +a
fi

while [ $# -gt 0 ]
do
  case "${1}" in
    --)
      shift
      break
      ;;
    *)
      set -a
      . "${1}"
      set +a
      shift
      ;;
  esac
done

exec "${@}"
