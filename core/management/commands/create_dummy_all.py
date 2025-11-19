from django.core.management.base import BaseCommand

from utils.dummy_data import build_dummy_data


class Command(BaseCommand):
    help = 'Create development dummy dataset (events, artists, spaces).'

    def handle(self, *args, **options):
        summary = build_dummy_data(reset=False)
        self.stdout.write(
            self.style.SUCCESS(
                'Dummy data created: '
                f"{summary['artists_created']} artists, {summary['spaces_created']} spaces, "
                f"{summary['events_created']} events."
            )
        )
