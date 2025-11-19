from django.core.management.base import BaseCommand

from utils.dummy_seed import seed_all


class Command(BaseCommand):
    help = 'Create development dummy dataset (events, artists, spaces).'

    def handle(self, *args, **options):
        summary = seed_all(reset=False)
        self.stdout.write(
            self.style.SUCCESS(
                'Dummy data created: '
                f"{summary['artists_created']} artists, {summary['spaces_created']} spaces, "
                f"{summary['events_created']} events (Dyve available: {summary['dyve_available']})."
            )
        )
