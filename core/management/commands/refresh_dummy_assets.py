import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image

SOURCE_TARGET_MAP = {
    'artist_profiles': ('artist', 'artist'),
    'space_profiles': ('space', 'space'),
    'posters': ('event', 'event'),
}


class Command(BaseCommand):
    help = 'Copies and re-encodes dummy_images assets into utils/assets with safe JPEGs.'

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        src_root = base_dir / 'dummy_images'
        dst_root = base_dir / 'utils' / 'assets'
        skipped: list[tuple[str, str]] = []

        for src_folder, (dst_folder, prefix) in SOURCE_TARGET_MAP.items():
            src_path = src_root / src_folder
            dst_path = dst_root / dst_folder
            dst_path.mkdir(parents=True, exist_ok=True)
            self._clear_folder(dst_path)

            if not src_path.exists():
                self.stderr.write(self.style.WARNING(f'Source folder missing: {src_path}'))
                continue

            files = sorted(p for p in src_path.iterdir() if p.is_file())
            if not files:
                self.stderr.write(self.style.WARNING(f'No files found in {src_path}'))
                continue

            default_written = False
            counter = 0

            for file_path in files:
                try:
                    with Image.open(file_path) as img:
                        rgb = img.convert('RGB')
                        counter += 1
                        target_name = f"{prefix}_{counter}.jpg"
                        target_path = dst_path / target_name
                        rgb.save(target_path, format='JPEG', quality=90)
                        if not default_written:
                            default_path = dst_path / 'default.jpg'
                            rgb.save(default_path, format='JPEG', quality=90)
                            default_written = True
                except Exception as exc:  # pylint: disable=broad-except
                    skipped.append((str(file_path), str(exc)))
                    counter -= 1

            self.stdout.write(
                self.style.SUCCESS(f'Copied {counter} images from {src_folder} to {dst_folder}.')
            )

        if skipped:
            self.stderr.write(self.style.WARNING('Skipped files:'))
            for name, reason in skipped:
                self.stderr.write(f' - {name}: {reason}')
        else:
            self.stdout.write(self.style.SUCCESS('All dummy images refreshed successfully.'))

    def _clear_folder(self, folder: Path) -> None:
        for child in folder.glob('*'):
            if child.is_file():
                child.unlink()
            else:
                shutil.rmtree(child)
