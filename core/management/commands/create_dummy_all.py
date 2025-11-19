from django.core.management.base import BaseCommand
from django.db import transaction

from utils.dummy_data import seed_all


class Command(BaseCommand):
    help = 'Create development dummy dataset (events, artists, spaces).'

    def handle(self, *args, **options):
        with transaction.atomic():
            summary = seed_all(clear_existing=True)
        self.stdout.write(
            self.style.SUCCESS(
                'Dummy data created: '
                f"{summary['artists_created']} artists, {summary['spaces_created']} spaces, "
                f"{summary['events_created']} events."
            )
        )
