import random
from datetime import time as dtime, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import GENRES, SPACE_CATEGORIES
from .models import Artist, Event, Space
from .serializers import DummyCreateResponseSerializer

User = get_user_model()

DEV_REGIONS = ['서울', '부산', '대구', '인천']
ENTRY_TYPES = ['standing', 'seat', 'free']
EQUIPMENT_PRESETS = [
    '마이크',
    '앰프',
    '모니터 스피커',
    '기본 음향 콘솔',
    '무선 마이크',
    'DJ 장비',
    '무대 조명',
]


class DummyDataGenerator:
    EVENT_COUNT = 10
    ARTIST_COUNT = 5
    SPACE_COUNT = 5

    def __init__(self):
        self.user_model = User

    def _random_region(self):
        return random.choice(DEV_REGIONS)

    def _random_time(self):
        hour = random.randint(17, 22)
        minute = random.choice([0, 15, 30, 45])
        return dtime(hour=hour, minute=minute)

    def _get_space_owner(self):
        owner, created = self.user_model.objects.get_or_create(
            username='dev_dummy_owner',
            defaults={
                'email': 'dev_dummy_owner@example.com',
                'first_name': 'Dev',
                'last_name': 'Owner',
            },
        )
        if created:
            owner.set_password('dev_dummy_owner')
            owner.save(update_fields=['password'])
        return owner

    def create_artists(self, count=None):
        count = count or self.ARTIST_COUNT
        artists = []
        for _ in range(count):
            suffix = random.randint(1000, 9999)
            genres = ', '.join(random.sample(GENRES, k=min(2, len(GENRES))))
            equipments = ', '.join(random.sample(EQUIPMENT_PRESETS, k=2))
            artist = Artist.objects.create(
                name=f'Dummy Artist #{suffix}',
                genres=genres,
                equipments=equipments,
                portfolio_url=f'https://example.com/dummy-artist-{suffix}',
                image_url=f'https://placehold.co/600x400?text=Artist{suffix}',
                history=f'프론트 테스트용 더미 아티스트 #{suffix}',
            )
            artists.append(artist)
        return artists

    def create_spaces(self, count=None):
        count = count or self.SPACE_COUNT
        owner = self._get_space_owner()
        spaces = []
        for _ in range(count):
            suffix = random.randint(1000, 9999)
            region = self._random_region()
            equipments = ', '.join(random.sample(EQUIPMENT_PRESETS, k=3))
            space = Space.objects.create(
                owner=owner,
                name=f'Dummy Space #{suffix}',
                category=random.choice(SPACE_CATEGORIES),
                genres=', '.join(random.sample(GENRES, k=min(2, len(GENRES)))),
                region=region,
                address=f'{region} 테스트로 {random.randint(1, 200)}',
                capacity=random.randint(40, 300),
                description='프론트엔드 개발용 임시 공간입니다.',
                equipments=equipments,
                image_url=f'https://placehold.co/600x400?text=Space{suffix}',
            )
            spaces.append(space)
        return spaces

    def create_events(self, count=None, *, spaces=None, artists=None, ensure_relations=True):
        count = count or self.EVENT_COUNT
        created_events = []
        artists_created = 0
        spaces_created = 0

        if artists is None:
            artists = list(Artist.objects.all())
        if not artists and ensure_relations:
            new_artists = self.create_artists()
            artists_created += len(new_artists)
            artists = new_artists

        if spaces is None:
            spaces = list(Space.objects.all())
        if not spaces and ensure_relations:
            new_spaces = self.create_spaces()
            spaces_created += len(new_spaces)
            spaces = new_spaces

        for _ in range(count):
            suffix = random.randint(1000, 9999)
            fallback_region = self._random_region()
            assigned_space = random.choice(spaces) if spaces else None
            region = assigned_space.region if assigned_space else fallback_region
            is_free = random.choice([True, False])
            price = 0 if is_free else random.randint(10000, 70000)
            event = Event.objects.create(
                title=f'Dummy Event #{suffix}',
                description='프론트 테스트용 임시 공연입니다.',
                genre=random.choice(GENRES),
                region=region,
                date=timezone.localdate() + timedelta(days=random.randint(1, 15)),
                time=self._random_time(),
                venue_name=assigned_space.name if assigned_space else f'{region} 컬쳐 스팟',
                address=assigned_space.address if assigned_space else f'{region} 거리 {random.randint(1, 120)}',
                price=price,
                is_free=is_free,
                entry_type=random.choice(ENTRY_TYPES),
                image_url=f'https://placehold.co/800x600?text=Event{suffix}',
                allow_dyve_reservation=random.choice([True, False]),
                advertise=random.choice([True, False]),
                space=assigned_space,
            )
            if artists:
                max_artists = min(len(artists), 3)
                sample_size = random.randint(1, max_artists)
                event.artists.set(random.sample(artists, k=sample_size))
            created_events.append(event)

        return created_events, artists_created, spaces_created


class BaseDummyCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_generator(self):
        return DummyDataGenerator()

    def build_response(self, *, events=0, artists=0, spaces=0):
        serializer = DummyCreateResponseSerializer(
            {
                'events_created': events,
                'artists_created': artists,
                'spaces_created': spaces,
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CreateDummyEventsView(BaseDummyCreateView):
    @extend_schema(
        tags=['Dev Dummy'],
        summary='개발용 더미 공연 생성',
        description='테스트용으로 랜덤한 공연 Event 10개를 생성합니다. 필요 시 공간/아티스트를 자동 보충합니다.',
        request=None,
        responses={201: DummyCreateResponseSerializer},
    )
    def post(self, request):
        generator = self.get_generator()
        events, artists_created, spaces_created = generator.create_events()
        return self.build_response(
            events=len(events),
            artists=artists_created,
            spaces=spaces_created,
        )


class CreateDummyArtistsView(BaseDummyCreateView):
    @extend_schema(
        tags=['Dev Dummy'],
        summary='개발용 더미 아티스트 생성',
        description='랜덤 장르와 장비 정보를 갖는 아티스트 5개를 생성합니다.',
        request=None,
        responses={201: DummyCreateResponseSerializer},
    )
    def post(self, request):
        generator = self.get_generator()
        artists = generator.create_artists()
        return self.build_response(artists=len(artists))


class CreateDummySpacesView(BaseDummyCreateView):
    @extend_schema(
        tags=['Dev Dummy'],
        summary='개발용 더미 공간 생성',
        description='랜덤 카테고리, 지역, 장비를 갖는 공간(Space) 5개를 생성합니다.',
        request=None,
        responses={201: DummyCreateResponseSerializer},
    )
    def post(self, request):
        generator = self.get_generator()
        spaces = generator.create_spaces()
        return self.build_response(spaces=len(spaces))


class CreateDummyAllView(BaseDummyCreateView):
    @extend_schema(
        tags=['Dev Dummy'],
        summary='개발용 더미 데이터 전체 생성',
        description='아티스트 5개, 공간 5개, 공연 10개 세트를 한 번에 생성하고 FK 관계를 연결합니다.',
        request=None,
        responses={201: DummyCreateResponseSerializer},
    )
    def post(self, request):
        generator = self.get_generator()
        artists = generator.create_artists()
        spaces = generator.create_spaces()
        events, _, _ = generator.create_events(spaces=spaces, artists=artists, ensure_relations=False)
        return self.build_response(
            events=len(events),
            artists=len(artists),
            spaces=len(spaces),
        )
