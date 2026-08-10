from .base import BaseSource
from .hn import HackerNewsSource
from .reddit import RedditSource
from .rss import RSSSource

# Registry mapping source types to their implementation classes
SOURCE_REGISTRY = {
    "hn": HackerNewsSource,
    "reddit": RedditSource,
    "rss": RSSSource,
}
