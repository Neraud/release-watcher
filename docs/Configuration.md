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
- type: docker_registry
  repo: registry-1.docker.io
  image: python
  tag: 3.7.2-alpine3.8
  includes:
    - 3\.[7-9]\.[0-9]+-alpine3\.
  excludes:
    - .*rc[0-9]*-.*
    - .*[ab][1-9]-.*
```

* `repo`: the domain of the docker registry.

For DockerHub, you need to use the real repo domain : `registry-1.docker.io`

* `image`: the docker image to watch

If the image name doesn't contain a `/`, `library/` is automatically added (example : `python` becomes `library/python`)

* `tag`: the currently used tag
* `includes`: an optional list of regular expressions that a tag must match to be considered
* `excludes`: an optional list of regular expressions that a tag must not match to be considered

In the example above, we are watching new tags on the `python` image on DockerHub.
We only want tags for a python v3.x.x based on alpine 3.x (include `3\.[7-9]\.[0-9]+-alpine3\.`)
We also want to ignore RCs (exclude `.*rc[0-9]*-.*`) and alphas/betas (exclude `.*[ab][1-9]-.*`)

If `tag` is found in the repo, only newer tags are listed.


### GitHub Release

You can watch for a release in a GitHub repository.

```yaml
- type: github_release
  repo: dateutil/dateutil
  release: 2.6.0
  includes:
    - ^2\.6\.
```

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
- type: github_tag
  repo: yaml/pyyaml
  tag: 4.1
  includes:
    - .*
  excludes:
    - .*[ab][1-9]$
```

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
- type: github_commit
  repo: docker-library/python
  branch: master
  commit: f6e98ea8b8ef4e9a520e05d481d2640a35f9542c
```

* `repo`: the repository name
* `branch`: the branch to scan
* `commit`: the current commit hash

In the example above, we are watching new tags on the `docker-library/python` repository on GitHub.

If `commit` is found on the repo, only newer tags are listed.

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

* `currentReleaseDate` : the date of the current release
* `friendlyName` : a friendly representation of the current release 
  * for example `docker_repo`:`docker_image`:`tag`
* `missedReleaseCount` : the number of missed releases
* `missedReleases` : the list of missed releases, with a `date` and `name` for each one of them
* `newestRelease` : the newest release, with a `date` and `name`
* `type` : the watcher type

Example : 

```yaml
results:
- currentReleaseDate: 2019-03-07 22:47:31.896533+00:00
  friendlyName: library/python:3.7.2-alpine3.8
  missedReleaseCount: 2
  missedReleases:
  - date: '2019-05-11 02:03:33.380024+00:00'
    name: 3.7.3-alpine3.9
  - date: '2019-05-08 00:13:13.242555+00:00'
    name: 3.7.3-alpine3.8
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
* `Friendly name`: a friendly representation of the current release 
  * for example `docker_repo`:`docker_image`:`tag`
* `Current release date`: the date of the current release
* `Missed releases`: the number of missed releases
* `Newest release`: the newest release name
* `Newest release date`: the newest release date

For example : 

```csv
Type,Friendly name,Current release date,Missed releases,Newest release,Newest release date
docker_registry,registry-1.docker.io:library/python:3.7.2-alpine3.8,2019-03-07 22:47:31.896533+00:00,2,3.7.3-alpine3.9,2019-05-11 02:03:33.380024+00:00
```
