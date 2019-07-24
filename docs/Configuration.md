# Release Watcher Configuration

A complete configuration sample, along with the generated outputs is available in the `example` folder of the repository.

## Logger

Logs can be printed on stdout (default):

```yaml
logger:
  type: stdout
  level: INFO
```

Or in a file

```yaml
logger:
  type: file
  path: /path/to/release_watcher.log
  level: INFO
```

Allowed levels are : `DEBUG`, `INFO`, `WARN`, `ERROR`.

## Core

```yaml
core:
  threads: 2
  runMode: once|repeat
  sleepDuration: duration in seconds
```

Watchers are executed in a thread pool with `threads` threads.

With `runMode: once` (default), the programm simply exits once the results are written to the outputs.

Using `runMode: repeat`, the program never stops (untill interrupted) and sleeps for `sleepDuration` between each execution.

## Sources

Multiple sources can be used at the same time.

### Inline

Watchers can be configured inline in the main configuration file :

```yaml
sources:
  - type: inline
    watchers:
      - [watcher_1]
      - [watcher_n]
```

### External

```yaml
sources:
  - type: file
    path: /path/to/watchers.yml
```

If `path` doesn't start with a `/`, it is assumed to be relative to the main configuration file directory.

The external file has the same structure as the `watchers` subelement :

```yaml
watchers:
  - [watcher_1]
  - [watcher_n]
```

## Watchers

Each watcher configures a *thing* to watch new releases for.

### Docker image

You can watch for a docker image in any v2 registry.

```yaml
- name: PythonAlpineImage
  type: docker_registry
  repo: registry-1.docker.io
  image: python
  tag: 3.7.2-alpine3.8
  includes:
    - 3\.[7-9]\.[0-9]+-alpine3\.8
  excludes:
    - .*rc[0-9]*-.*
    - .*[ab][1-9]-.*
```

* `name`: optional name for the watcher. Defaults to `[repo]:[image]`
* `repo`: the domain of the docker registry.

For DockerHub, you need to use the real repo domain : `registry-1.docker.io`

* `image`: the docker image to watch

For the DockerHub repo (`registry-1.docker.io`), if the image name doesn't contain a `/`, `library/` is automatically added (example : `python` becomes `library/python`)

* `tag`: the currently used tag
* `includes`: an optional list of regular expressions that a tag must match to be considered
* `excludes`: an optional list of regular expressions that a tag must not match to be considered

In the example above, we are watching new tags on the `python` image on DockerHub.
We only want tags for a python v3.x.x based on alpine 3.8 (include `3\.[7-9]\.[0-9]+-alpine3\.8`)
We also want to ignore RCs (exclude `.*rc[0-9]*-.*`) and alphas/betas (exclude `.*[ab][1-9]-.*`)

If `tag` is found in the repo, only newer tags are listed.

### GitHub Release

You can watch for a release in a GitHub repository.

```yaml
- name: DateUtil
  type: github_release
  repo: dateutil/dateutil
  release: 2.6.0
  includes:
    - ^2\.6\.
```

* `name`: optional name for the watcher. Defaults to `[repo]`
* `repo`: the repository name
* `release`: the currently used release (based on the release tag name)
* `includes`: an optional list of regular expressions that a tag must match to be considered
* `excludes`: an optional list of regular expressions that a tag must not match to be considered

In the example above, we are watching new releases on the `dateutil/dateutil` repository on GitHub.
We also only want to consider new 2.6.x releases.

If `release` is found in the repo, only newer releases are listed.

### GitHub Tag

You can watch for a tag in a GitHub repository.

```yaml
- name: PyYAML
  type: github_tag
  repo: yaml/pyyaml
  tag: 4.1
  includes:
    - .*
  excludes:
    - .*[ab][1-9]$
```

* `name`: optional name for the watcher. Defaults to `[repo]`
* `repo`: the repository name
* `tag`: the currently used tag
* `includes`: an optional list of regular expressions that a tag must match to be considered
* `excludes`: an optional list of regular expressions that a tag must not match to be considered

In the example above, we are watching new tags on the `yaml/pyyaml` repository on GitHub.
We also want to ignore alphas/betas (exclude `.*[ab][1-9]$`)

If `tag` is found on the repo, only newer tags are listed.

*Note* : the tag API doesn't list the tag date, it requires an additional API call to the commit API. If possible, prefer the 'GitHub Release' watcher.

### GitHub Commit

You can watch for commits in a GitHub repository.

```yaml
- name: PythonDockerSource
  type: github_commit
  repo: docker-library/python
  branch: master
  commit: f6e98ea8b8ef4e9a520e05d481d2640a35f9542c
```

* `name`: optional name for the watcher. Defaults to `[repo]`
* `repo`: the repository name
* `branch`: the branch to scan
* `commit`: the current commit hash

In the example above, we are watching new tags on the `docker-library/python` repository on GitHub.

If `commit` is found on the repo, only newer tags are listed.

### PyPI release

You can watch for releases of a PyPI package.

```yaml
- name: PyYAML
  type: pypi
  package: PyYAML
  version: 5.1.0
  includes: 
    - 5\..*
  excludes: 
    - .*[ab][1-9]$
```

* `name`: optional name for the watcher. Defaults to `[package]`
* `package`: the package name
* `version`: the current version
* `includes`: an optional list of regular expressions that a version must match to be considered
* `excludes`: an optional list of regular expressions that a version must not match to be considered

In the example above, we are watching new releases of the `PyYAML` package.
We only want to consider versions `5.*` and ignore betas (exclude `.*[ab] [1-9]$`)

## Outputs

Once new releases have been found, you need to save the output.

Multiple outputs can be configured at the same time.

### YAML file

You can export the outputs to a YAML file.

```yaml
- type: yaml_file
  path: /path/to/out.yaml
  displayUpToDate: yes
```

* `path`: path to the yaml file

If `path` doesn't start with a `/`, it is assumed to be relative to the main configuration file directory.

* `displayUpToDate`: if set to `no`, only watchers with new releases will be listed

The generated file will contain a list of results, each with :

* `currentRelease` : the current release
* `currentReleaseDate` : the date of the current release
* `name` : the watcher name
  * for example `docker_repo`:`docker_image`:`tag`
* `missedReleaseCount` : the number of missed releases
* `missedReleases` : the list of missed releases, with a `date` and `name` for each one of them
* `newestRelease` : the newest release, with a `date` and `name`
* `type` : the watcher type

Example :

```yaml
results:
- currentRelease: 3.7.2-alpine3.8
  currentReleaseDate: 2019-03-07 22:47:31.896533+00:00
  missedReleaseCount: 2
  missedReleases:
  - date: '2019-05-11 02:03:33.380024+00:00'
    name: 3.7.3-alpine3.9
  - date: '2019-05-08 00:13:13.242555+00:00'
    name: 3.7.3-alpine3.8
  name: PythonImage
  newestRelease:
    date: '2019-05-11 02:03:33.380024+00:00'
    name: 3.7.3-alpine3.9
  type: docker_registry
```

### CSV File

You can export the outputs to a CSV file.

```yaml
- type: csv_file
  path: /path/to/out.csv
  displayUpToDate: yes
  displayHeaders: yes
```

* `path`: path to the csv file

If `path` doesn't start with a `/`, it is assumed to be relative to the main configuration file directory.

* `displayUpToDate` (optionnal, default `yes`): if set to `no`, only watchers with new releases will be listed
* `displayHeaders` (optionnal, default `yes`): if set to `no`, the header line is skipped

The generated file will contain 1 row for each result, with the following columns :

* `Type`: the watcher type
* `Name`: the watcher name
* `Current release`: the current release
* `Current release date`: the date of the current release
* `Missed releases`: the number of missed releases
* `Newest release`: the newest release name
* `Newest release date`: the newest release date

For example :

```csv
Type,Name,Current release,Current release date,Missed releases,Newest release,Newest release date
docker_registry,PythonImage,3.7.2-alpine3.8,2019-03-07 22:47:31.896533+00:00,2,3.7.3-alpine3.9,2019-05-11 02:03:33.380024+00:00
```

### Prometheus File

You can export the outputs to a Prometheus file.

```yaml
- type: prometheus_file
  path: /path/to/out.prom
```

* `path`: path to the prom file

If `path` doesn't start with a `/`, it is assumed to be relative to the main configuration file directory.

A single gauge is written : `missed_releases`, and it counts the number of missed releases.

If has a `name` label which is the watcher name.

For example :

```go
# HELP missed_releases Number of missed releases
# TYPE missed_releases gauge
missed_releases{name="PythonAlpineImage"} 2.0
```

### Prometheus Http endpoint

You can expose the outputs on an HTTP endpoint to be scraped by a Prometheus instance.

```yaml
- type: prometheus_http
  port: 8080
```

* `port`: port to expose

The metrics will be availble on <http://[host_ip]:[port]/>

A single gauge is exported : `missed_releases`, and it counts the number of missed releases.

If has a `name` label which is the watcher name.

For example :

```go
[many python standard metrics]

# HELP missed_releases Number of missed releases
# TYPE missed_releases gauge
missed_releases{name="PythonAlpineImage"} 2.0
```

*Note* : this exporter only makes sense with `core.runMode` set to `repeat`.
When using `core.runMode` = `once`, the HTTP server will start and shutdown immediately.
