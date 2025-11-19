"""Central constants sourced from shared dummy JSON catalogs."""

from utils.json_loader import load_json

REGIONS = load_json('regions')
GENRES = load_json('genres')
SPACE_CATEGORIES = load_json('space_categories')
ARTIST_CATEGORIES = load_json('artist_categories')
EQUIPMENT_OPTIONS = load_json('equipment')
