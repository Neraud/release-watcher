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

* Docker image : watches for new tags pushed on a docker v2 registry
* GitHub release : watches for a new release in a GitHub repository
* GitHub tag : watches for a new tag in a GitHub repository
* GitHub commit : watches for new commits in a GitHub repository
* Python Package Index (PyPI) : watches for new releases
* Raw HTML page : extracts items from a web page (for example a Gogs repo)

## Outputs

New releases are written to an output.
Release Watcher currently supports :

* YAML file
* CSV file
* Prometheus file
* Prometheus HTTP endpoint

## Installation

### Docker

You can use the following environment variables :

* `CONFIG_PATH` (defaults to `/data/config.yaml`) : path to the configuration file

The easiest way to use the image is to mount a `/data` folder :

```shell
mkdir data
cp example/{config,github_watchers}.yaml data/
# vi data/config.yaml
docker run -v $(pwd)/data:/data ghcr.io/neraud/release-watcher:latest
```

If you want to use the Prometheus HTTP output, you will need to forward the configured port.

```shell
docker run -v $(pwd)/data:/data -p 8080:8080 ghcr.io/neraud/release-watcher:latest
```

### Native

```shell
git clone https://github.com/Neraud/release-watcher
python3 -m pip install .
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
cd release-watcher
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --editable .
```

## Licence

[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

## Authors

`release_watcher` was written by `Neraud`.
