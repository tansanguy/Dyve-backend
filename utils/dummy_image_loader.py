"""Local image loader that uploads curated dummy assets to Cloudinary."""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable

import cloudinary.uploader
from django.conf import settings


SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


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
        self.folder_map = folders or {'artist': 'artists', 'space': 'spaces', 'poster': 'events'}
        self.consume_once = consume_once
        self.pools: Dict[str, ImagePool] = {
            key: ImagePool(self.base_dir / value, consume_once=consume_once)
            for key, value in self.folder_map.items()
        }
        self._cloud_folder = {
            'artist': 'artist_profiles',
            'space': 'space_profiles',
            'poster': 'posters',
        }
        self._fallback_url = getattr(settings, 'DYVE_DEFAULT_EVENT_IMAGE', '')

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
    def _upload(self, category: str) -> str:
        pool = self.pools.get(category)
        if not pool:
            return self._fallback_url
        path = pool.next_path()
        if path is None:
            return self._fallback_url
        cloud_folder = self._cloud_folder.get(category, category)
        return self._upload_with_fallback([path, pool.default_path], cloud_folder)

    def _upload_with_fallback(self, candidates: Iterable[Path], folder_name: str) -> str:
        folder = f"{settings.DYVE_DUMMY_IMAGE_FOLDER}/{folder_name}"
        for candidate in candidates:
            if candidate is None:
                continue
            try:
                result = cloudinary.uploader.upload(
                    str(candidate),
                    folder=folder,
                    use_filename=True,
                    unique_filename=False,
                )
                secure_url = result.get('secure_url')
            except Exception:
                secure_url = None
            if secure_url:
                return secure_url
        return self._fallback_url
