from release_watcher.sources.source_manager import register_source_type
from release_watcher.sources.file_source import FileSourceType
from release_watcher.sources.inline_source import InlineSourceType

register_source_type(FileSourceType())
register_source_type(InlineSourceType())
