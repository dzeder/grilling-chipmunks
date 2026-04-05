"""
Fetcher registry for the content-watcher pipeline.

Maps SourceType → BaseFetcher subclass. Fetchers register themselves on import.
"""

from schema import SourceType

_REGISTRY: dict[SourceType, type] = {}


def register(source_type: SourceType):
    """Decorator to register a fetcher class for a source type."""

    def decorator(cls):
        _REGISTRY[source_type] = cls
        return cls

    return decorator


def get_fetcher(source_type: SourceType):
    """Get the fetcher class for a source type."""
    if source_type not in _REGISTRY:
        raise ValueError(f"No fetcher registered for source type: {source_type}")
    return _REGISTRY[source_type]()


def get_registered_types() -> list[SourceType]:
    """Return all source types that have a registered fetcher."""
    return list(_REGISTRY.keys())


# Import fetcher modules to trigger registration
from fetchers import rss  # noqa: F401, E402
from fetchers import reddit  # noqa: F401, E402
