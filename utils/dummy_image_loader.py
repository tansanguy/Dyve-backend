"""Local image loader that uploads curated dummy assets to Cloudinary."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import cloudinary.uploader
from PIL import Image
from django.conf import settings


logger = logging.getLogger(__name__)

ASSET_BASE = Path(settings.BASE_DIR) / 'utils' / 'assets'
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
FALLBACK_IMAGE = ASSET_BASE / 'common' / 'default.jpg'


@dataclass
class ImagePool:
    folder: Path
    consume_once: bool = False

    def __post_init__(self) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        self._files = sorted(
            path
            for path in self.folder.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS and not path.name.startswith('.')
        )
        self._index = 0

    def next_path(self) -> Path | None:
        if not self._files:
            return None
        if self.consume_once:
            if self._index < len(self._files):
                path = self._files[self._index]
                self._index += 1
                return path
            return None
        return random.choice(self._files)


class DummyImageLoader:
    """Provides access to curated local images and uploads them to Cloudinary."""

    def __init__(
        self,
        *,
        base_dir: Path | None = None,
        folders: Dict[str, str] | None = None,
        consume_once: bool = False,
    ) -> None:
        self.base_dir = Path(base_dir) if base_dir else ASSET_BASE
        self.folder_map = folders or {'artist': 'artist', 'space': 'space', 'poster': 'event'}
        self.consume_once = consume_once
        self._ensure_asset_dirs()
        self.pools: Dict[str, ImagePool] = {
            key: ImagePool(self.base_dir / value, consume_once=consume_once)
            for key, value in self.folder_map.items()
        }
        self._cloud_folder = {
            'artist': 'artist_profiles',
            'space': 'space_profiles',
            'poster': 'posters',
        }
        self._fallback_url = getattr(settings, 'DYVE_DEFAULT_EVENT_IMAGE', str(FALLBACK_IMAGE))

    # ------------------------------------------------------------------
    def get_random_image(self, category: str) -> Path | None:
        pool = self.pools.get(category)
        if not pool:
            logger.warning('Unknown image category requested: %s', category)
            return self.load_image_or_fallback(None)
        return self.load_image_or_fallback(pool.next_path())

    def validate_image(self, path: Path | None) -> bool:
        if not path or not path.exists():
            return False
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return False
        if path.stat().st_size == 0:
            return False
        try:
            with Image.open(path) as img:
                img.verify()
            return True
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning('Invalid image %s: %s', path, exc)
            return False

    def load_image_or_fallback(self, path: Path | None) -> Path | None:
        if self.validate_image(path):
            return path
        fallback_path = FALLBACK_IMAGE
        if self.validate_image(fallback_path):
            logger.info('Using fallback image at %s.', fallback_path)
            return fallback_path
        logger.error('Fallback image missing or broken at %s.', fallback_path)
        return None

    def get_random_artist_image(self) -> str:
        # 한국어 주석: 아티스트 이미지를 artist 폴더에서만 선택하도록 강제합니다.
        return self._upload_category('artist')

    def get_random_space_image(self) -> str:
        return self._upload_category('space')

    def get_random_event_poster(self) -> str:
        return self._upload_category('poster')

    # alias for backward compatibility
    def next_artist_image(self) -> str:
        return self.get_random_artist_image()

    def next_space_image(self) -> str:
        return self.get_random_space_image()

    def next_event_poster(self) -> str:
        return self.get_random_event_poster()

    def next_poster_image(self) -> str:
        return self.get_random_event_poster()

    # ------------------------------------------------------------------
    def _ensure_asset_dirs(self) -> None:
        for folder_name in set(self.folder_map.values()) | {'common'}:
            folder_path = self.base_dir / folder_name
            folder_path.mkdir(parents=True, exist_ok=True)

    def _upload_category(self, category: str) -> str:
        image_path = self.get_random_image(category)
        if not image_path:
            logger.warning('No valid image available for %s.', category)
            return self._fallback_url
        fallback_path = self.load_image_or_fallback(FALLBACK_IMAGE)
        return self._upload_with_fallback(image_path, fallback_path, self._cloud_folder.get(category, category))

    def _upload_with_fallback(self, path: Path | None, fallback_path: Path | None, folder_name: str) -> str:
        folder = f"{settings.DYVE_DUMMY_IMAGE_FOLDER}/{folder_name}"
        if path:
            url = self._try_upload(path, folder)
            if url:
                return url
        if fallback_path:
            url = self._try_upload(fallback_path, folder)
            if url:
                return url
        return self._fallback_url

    def _try_upload(self, candidate: Path, folder: str) -> str | None:
        try:
            result = cloudinary.uploader.upload(
                str(candidate),
                folder=folder,
                use_filename=True,
                unique_filename=False,
            )
            url = result.get('secure_url')
            if not url:
                logger.warning('Cloudinary response missing secure_url for %s', candidate)
            return url
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning('Cloudinary upload failed for %s: %s', candidate, exc)
            return None
