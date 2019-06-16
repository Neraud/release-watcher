# Release Watcher

Release Watcher is an application that ... watches for releases.

You can configure it with a list of *things* to watch for, and it will
search for new releases.

## Sources

A source handles listing the *things* you want to watch for.
Release Watcher currently supports :

* inline YAML configuration, inside config.yaml
* external YAML file

## Watchers

A watcher is a type of *thing* you want to watch for.
Release Watcher currently supports :

* Docker image : watchs for new tags pushed on a docker v2 registry
* Github release : watchs for a new release in a Github repository
* Github tag : watchs for a new tag in a Github repository
* Github commit : watchs for new commits in a Github repository

## Outputs

New releases are written to an output.
Release Watcher currently supports :

* YAML file
* CSV file
* Prometheus file
* Prometheus HTTP endpoint

## Installation

### Native

```shell
git clone https://github.com/Neraud/release-watcher
python3 -m pip install .
```

### Docker

```shell
git clone https://github.com/Neraud/release-watcher
docker build -t release_watcher .
```

You can use the following environment variables :

* `CONFIG_PATH` (defaults to `/data/config.yaml`) : path to the configuration file

The easiest way to use the image is to mount a `/data` folder :

```shell
mkdir data
cp example/{config,github_watchers}.yaml data/
# vi data/config.yaml
docker run -v $(pwd)/data:/data release_watcher
```

If you want to use the Prometheus HTTP output, you will need to forward the configured port.

```shell
docker run -v $(pwd)/data:/data -p 8080:8080 release_watcher
```

## Configuration

The repository contains a sample configuration file : `example/config.yaml`.

For more information : [Configuration](docs/Configuration.md)

## Usage

```shell
release_watcher --config /path/to/config.yaml
```

## Development

```shell
git clone https://github.com/Neraud/release-watcher
python3 -m pip install --editable .
```

## Licence

[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

## Authors

`release_watcher` was written by `Neraud`.
