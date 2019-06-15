#!/usr/bin/env sh

echo "Using CONFIG_PATH=$CONFIG_PATH"

echo "Starting release_watcher"
release_watcher --config $CONFIG_PATH
