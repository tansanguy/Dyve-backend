"""Local image loader that uploads curated dummy assets to Cloudinary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import cloudinary.uploader
from django.conf import settings


SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


@dataclass
class ImageQueue:
    folder: Path
    default_name: str = 'default.jpg'

    def __post_init__(self) -> None:
        if not self.folder.exists():
            raise FileNotFoundError(f'Image folder not found: {self.folder}')
        self.default_path = self.folder / self.default_name
        if not self.default_path.exists():
            raise FileNotFoundError(f'Default image missing: {self.default_path}')
        self._files = self._collect_files()
        self._index = 0

    def next_path(self) -> Path:
        if self._index < len(self._files):
            path = self._files[self._index]
            self._index += 1
            return path
        return self.default_path

    def _collect_files(self):
        files = []
        for path in sorted(self.folder.iterdir()):
            if not path.is_file():
                continue
            if path.name == self.default_name:
                continue
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            if path.name.startswith('.'):
                continue
            files.append(path)
        return files


class DummyImageLoader:
    """Provides deterministic access to local dummy images per category."""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = Path(base_dir) if base_dir else Path(settings.BASE_DIR) / 'dummy_images'
        self.queues: Dict[str, ImageQueue] = {
            'artist': ImageQueue(self.base_dir / 'artist_profiles'),
            'space': ImageQueue(self.base_dir / 'space_profiles'),
            'poster': ImageQueue(self.base_dir / 'posters'),
        }
        self._cloud_folder = {
            'artist': 'artist_profiles',
            'space': 'space_profiles',
            'poster': 'posters',
        }
        self._fallback_url = getattr(settings, 'DYVE_DEFAULT_EVENT_IMAGE', '')

    def next_artist_image(self) -> str:
        return self._upload_from_queue('artist')

    def next_space_image(self) -> str:
        return self._upload_from_queue('space')

    def next_poster_image(self) -> str:
        return self._upload_from_queue('poster')

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _upload_from_queue(self, category: str) -> str:
        queue = self.queues[category]
        image_path = queue.next_path()
        return self._upload_with_fallback(image_path, queue.default_path, self._cloud_folder[category])

    def _upload_with_fallback(self, path: Path, default_path: Path, folder_name: str) -> str:
        folder = f"{settings.DYVE_DUMMY_IMAGE_FOLDER}/{folder_name}"
        for candidate in (path, default_path):
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
