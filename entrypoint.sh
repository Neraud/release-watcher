#!/usr/bin/env sh

export PATH="$HOME/.local/bin:$PATH"

echo "Using CONFIG_PATH=$CONFIG_PATH"

echo "Starting release_watcher"
release_watcher --config $CONFIG_PATH
