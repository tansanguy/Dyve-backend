"""Utility helpers for loading shared dummy-json catalogs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from django.conf import settings

CATALOG_ROOT = Path(settings.BASE_DIR) / 'core' / 'fixtures' / 'catalogs'
CATALOG_FILES: Dict[str, str] = {
    'genres': 'genres.json',
    'regions': 'regions.json',
    'space_categories': 'space_categories.json',
    'artist_categories': 'artist_categories.json',
    'equipment': 'equipment.json',
}
_CACHE: Dict[str, Any] = {}


def load_json(name: str) -> List[Any]:
    """Load a catalog JSON file declared in ``CATALOG_FILES``.

    The function returns a new list per call so downstream consumers cannot mutate
    the cached data in-place.
    """

    filename = CATALOG_FILES.get(name)
    if not filename:
        raise ValueError(f'Unknown catalog name: {name}')

    if name not in _CACHE:
        path = CATALOG_ROOT / filename
        with path.open(encoding='utf-8') as fp:
            _CACHE[name] = json.load(fp)

    cached = _CACHE[name]
    return list(cached) if isinstance(cached, list) else cached
