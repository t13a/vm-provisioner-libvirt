#!/usr/bin/env bash

set -euo pipefail

# Change UID/GID of the user
sed -Ei "s/^(main:x):(1000):(1000):(.+)/\\1:$(id -u):$(id -g):\\4/" /etc/passwd
sed -Ei "s/^(main:x):(1000):(.*)/\\1:$(id -g):\\3/" /etc/group

# Change owner of the user
sudo chown -R main:main /home/main

# Restore owner and permissions
sudo chown root:root /etc/{group,passwd}
sudo chmod 755 /etc
sudo chmod 644 /etc/{group,passwd}
