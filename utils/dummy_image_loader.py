"""Local image loader that uploads curated dummy assets to Cloudinary."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable

import cloudinary.uploader
from PIL import Image
from django.conf import settings


logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
FALLBACK_IMAGE = 'https://res.cloudinary.com/demo/image/upload/v1312461204/sample.jpg'


@dataclass
class ImagePool:
    folder: Path
    default_name: str = 'default.jpg'
    consume_once: bool = False

    def __post_init__(self) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        self.default_path = self.folder / self.default_name
        if not self.default_path.exists():
            self.default_path.touch()
        self._files = self._collect_files()
        self._index = 0

    def next_path(self) -> Path | None:
        if self.consume_once and self._files:
            if self._index < len(self._files):
                path = self._files[self._index]
                self._index += 1
                return path
            return self.default_path if self.default_path.exists() else None
        if self._files:
            return random.choice(self._files)
        return self.default_path if self.default_path.exists() else None

    def _collect_files(self) -> list[Path]:
        files: list[Path] = []
        for path in sorted(self.folder.iterdir()):
            if not path.is_file() or path.name.startswith('.'):
                continue
            if path.name == self.default_name:
                continue
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            files.append(path)
        return files


class DummyImageLoader:
    """Provides access to curated local images and uploads them to Cloudinary."""

    def __init__(
        self,
        *,
        base_dir: Path | None = None,
        folders: Dict[str, str] | None = None,
        consume_once: bool = False,
    ) -> None:
        default_base = Path(settings.BASE_DIR) / 'utils' / 'assets'
        self.base_dir = Path(base_dir) if base_dir else default_base
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
        self._fallback_url = getattr(settings, 'DYVE_DEFAULT_EVENT_IMAGE', FALLBACK_IMAGE)

    def next_artist_image(self) -> str:
        return self._upload('artist')

    def next_space_image(self) -> str:
        return self._upload('space')

    def next_event_poster(self) -> str:
        return self._upload('poster')

    def next_poster_image(self) -> str:
        # backward compatibility
        return self.next_event_poster()

    # ------------------------------------------------------------------
    def _ensure_asset_dirs(self) -> None:
        for key, folder_name in self.folder_map.items():
            folder_path = self.base_dir / folder_name
            if not folder_path.exists():
                logger.warning('Asset folder missing for %s at %s. Creating automatically.', key, folder_path)
                folder_path.mkdir(parents=True, exist_ok=True)

    def _upload(self, category: str) -> str:
        pool = self.pools.get(category)
        if not pool:
            logger.warning('Unknown image category requested: %s', category)
            return self._fallback_url
        path = pool.next_path()
        cloud_folder = self._cloud_folder.get(category, category)
        return self._upload_with_fallback(path, pool.default_path, cloud_folder)

    def _upload_with_fallback(self, path: Path | None, default_path: Path | None, folder_name: str) -> str:
        folder = f"{settings.DYVE_DUMMY_IMAGE_FOLDER}/{folder_name}"
        # 1. try provided path
        if path:
            url = self._try_upload(path, folder)
            if url:
                return url
        # 2. try default fallback file
        if default_path:
            url = self._try_upload(default_path, folder)
            if url:
                return url
        # 3. return global fallback url
        return self._fallback_url or FALLBACK_IMAGE

    def _try_upload(self, candidate: Path, folder: str) -> str | None:
        if not candidate.exists():
            return None
        if candidate.stat().st_size == 0:
            logger.warning('Image %s is empty (0 bytes); skipping upload.', candidate)
            return None
        try:
            with Image.open(candidate) as img:
                detected_format = img.format.lower() if img.format else None
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning('Invalid image %s: %s', candidate, exc)
            return None
        if detected_format not in {'jpeg', 'png'}:
            logger.warning('Image %s is not a valid JPEG/PNG (detected %s).', candidate, detected_format)
            return None
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
