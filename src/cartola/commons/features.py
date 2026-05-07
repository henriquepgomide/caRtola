"""Feature engineering helpers used across pipelines."""

from unidecode import unidecode


def compute_slug(nickname: str) -> str:
    """Return a URL-safe slug derived from a player nickname."""
    return unidecode(nickname.lower().replace(" ", "-"))
