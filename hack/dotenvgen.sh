#!/usr/bin/env bash

set -euo pipefail

cat << EOF
MAIN_GID=$(id -g)
MAIN_UID=$(id -u)
SSH_IDENTITY=${SSH_IDENTITY:-${HOME}/.ssh/id_rsa}
SSH_IDENTITY_PUB=${SSH_IDENTITY_PUB:-${HOME}/.ssh/id_rsa.pub}
WORK_DIR=examples
EOF
