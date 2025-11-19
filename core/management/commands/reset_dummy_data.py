from django.core.management.base import BaseCommand

from utils.dummy_data import DummyDataBuilder


class Command(BaseCommand):
    help = 'Reset curated dummy artists/spaces/events and optionally rebuild them.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--rebuild',
            action='store_true',
            help='데이터 초기화 후 즉시 새로운 큐레이션 세트를 생성합니다.',
        )

    def handle(self, *args, **options):
        builder = DummyDataBuilder()
        builder.reset_all()
        self.stdout.write(self.style.SUCCESS('Existing dummy artists/spaces/events were deleted.'))
        if options.get('rebuild'):
            summary = builder.create_all()
            self.stdout.write(self.style.SUCCESS(f"Rebuild complete: {summary}"))
