from release_watcher.watchers.watcher_manager import register_watcher_type
from release_watcher.watchers.docker_registry_watcher \
    import DockerRegistryWatcherType
from release_watcher.watchers.gitlab_commit_watcher \
    import GithubCommitWatcherType
from release_watcher.watchers.gitlab_release_watcher \
    import GithubReleaseWatcherType
from release_watcher.watchers.gitlab_tag_watcher \
    import GithubTagWatcherType
from release_watcher.watchers.pypi_watcher \
    import PyPIWatcherType

register_watcher_type(DockerRegistryWatcherType())
register_watcher_type(GithubCommitWatcherType())
register_watcher_type(GithubReleaseWatcherType())
register_watcher_type(GithubTagWatcherType())
register_watcher_type(PyPIWatcherType())
