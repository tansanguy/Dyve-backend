from django.core.management.base import BaseCommand

from core.views_dev import DummyDataGenerator


class Command(BaseCommand):
    help = 'Create development dummy dataset (events, artists, spaces).'

    def handle(self, *args, **options):
        generator = DummyDataGenerator()
        artists = generator.create_artists()
        spaces = generator.create_spaces()
        events, _, _ = generator.create_events(artists=artists, spaces=spaces, ensure_relations=False)

        self.stdout.write(
            self.style.SUCCESS(
                f'Dummy data created: {len(artists)} artists, {len(spaces)} spaces, {len(events)} events.'
            )
        )
