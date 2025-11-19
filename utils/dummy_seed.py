"""Utilities for seeding realistic artist/space/event data for demos."""

from __future__ import annotations

import math
import random
from datetime import time as dtime, timedelta
from typing import Dict, List, Sequence

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from core.models import Artist, Event, Space
from utils.json_loader import load_json

ARTIST_NAME_POOL = [
    'Midnight Jazz Trio',
    'DJ Neonwave',
    'Seoul Indie Folks',
    'Han River Ensemble',
    'Golden Hour Collective',
    'Downtown Vinyl Club',
    'Velvet Room Quartet',
    'Urban Groove Syndicate',
    'Hangang Acoustic Union',
    'Rooftop Orchestra',
    'Concrete Poetry Band',
    'City Lights Duo',
    'Neon Circle DJs',
    'Eastside Chamber',
    'Busan Coastline Sound',
    'Future Pulse Lab',
    'Maple Avenue Choir',
    'Lofi Transit Club',
    'Sunset Resonance',
    'Harborline Quartet',
]

ARTIST_STORY_POOL = [
    '홍대 라이브 클럽 월간 쇼케이스에서 레지던시를 맡고 있습니다',
    '서울뮤직위크 오프닝 무대로 초청되어 협업 무대를 진행했습니다',
    '독립 레이블과 함께 도심 팝업 스테이지 투어를 이어가고 있습니다',
    '한강 수변 아트마켓과 연계한 음악 버스킹 시리즈를 진행했습니다',
    '클럽 컬렉티브와 공동 기획한 올나잇 컬처 파티에 참여했습니다',
    '해운대 비치 페스티벌에서 지역 기반 브랜드와 협업했습니다',
]

SPACE_NAME_POOL = [
    '홍대 Moonlight Stage',
    '성수 Livehall 42',
    '이태원 Velvet Lounge',
    '연남 Hazy Studio',
    '부산 해운대 Sound Dock',
    '대구 동성로 Pulse Theatre',
    '광주 충장로 Culture Lab',
    '대전 은행동 Loft Hall',
    '제주 Old Town Warehouse',
    '강릉 Shoreline Deck',
    '수원 Skyline Room',
    '서울 Riverside Atrium',
]

SPACE_DESCRIPTION_POOL = [
    '도심 아티스트 쇼케이스와 프라이빗 공연을 위한 스테이지입니다.',
    '밴드와 DJ를 모두 수용할 수 있는 멀티 포맷 공연장입니다.',
    '씬의 크리에이터들을 위한 프라이빗 라이브 라운지 공간입니다.',
    '신진 아티스트 콘텐츠 발표회에 최적화된 복합문화공간입니다.',
]

EVENT_TITLE_POOL = [
    'Midnight Jazz Session',
    'Urban Groove Live',
    'Indie Connect Showcase',
    'River City Stories',
    'Neonwave Club Night',
    'Seoul Sound Assembly',
    'Rooftop Sunset Jam',
    'Downtown Vibes Weekend',
    'Moonlight Listening Party',
    'Future Pulse Festival',
    'Acoustic Bridge Night',
    'Concrete Poetry Live',
    'Velvet Room Secret Set',
    'Skyline City Stories',
    'Han River Collaboration',
    'Loft Hall Residency',
    'Sound Dock Spotlight',
    'Culture Lab Open Stage',
    'Velvet Groove Marathon',
    'Nightfall Listening Club',
    'Eastside Collaboration',
    'Electro Sphere Live',
    'Lofi Transit Showcase',
    'Coastline Sessions',
    'Resonance Field',
    'Station Square Live',
    'Mapo Modular Stories',
    'Studio 42 Residency',
    'Horizon Beat Meetup',
    'Indie Garden Concert',
]

EVENT_DESCRIPTION_POOL = [
    '신진 뮤지션과 DJ가 함께 꾸미는 도심 라이브 쇼케이스입니다.',
    '주말 밤 감성 라이브와 비트가 공존하는 클럽 스타일 공연입니다.',
    '어쿠스틱과 일렉트로닉이 만나는 협업 퍼포먼스입니다.',
    '크리에이터 커뮤니티와 함께하는 시티 팝업 공연입니다.',
]

ENTRY_TYPES = ['general', 'seat', 'standing']
EVENT_HOUR_CHOICES = [17, 18, 19, 20, 21, 22]
EVENT_MINUTE_CHOICES = [0, 15, 30, 45]


class DummySeedService:
    ARTIST_MIN = 10
    SPACE_MIN = 10
    EVENT_MIN = 20

    def __init__(self):
        self.user_model = get_user_model()
        self.genres = load_json('genres')
        self.regions = load_json('regions')
        self.space_categories = load_json('space_categories')
        self.artist_categories = load_json('artist_categories')
        self.equipment = load_json('equipment')

    # ------------------------------------------------------------------
    # Public entrypoints
    # ------------------------------------------------------------------
    def seed_artists(self, count: int | None = None) -> List[Artist]:
        target = max(count or self.ARTIST_MIN, self.ARTIST_MIN)
        names = self._ensure_pool(ARTIST_NAME_POOL, target)
        artists: List[Artist] = []
        history_pool = ARTIST_STORY_POOL or ['씬의 쇼케이스에 참여한 팀입니다.']
        categories = self.artist_categories or ['밴드']

        with transaction.atomic():
            for name in names[:target]:
                slug = self._slugify(name)
                genres = ', '.join(self._sample(self.genres, 2))
                equipments = ', '.join(self._sample(self.equipment, 1, 3))
                category = random.choice(categories)
                history = f"{name}는 {category} 프로젝트로 {random.choice(history_pool)}"
                artist = Artist.objects.create(
                    name=name,
                    genres=genres,
                    equipments=equipments,
                    portfolio_url=f'https://showcase.dyve.local/artists/{slug}',
                    image_url=f'https://images.dyve.local/artists/{slug}.jpg',
                    history=history,
                )
                artists.append(artist)
        return artists

    def seed_spaces(self, count: int | None = None) -> List[Space]:
        target = max(count or self.SPACE_MIN, self.SPACE_MIN)
        names = self._ensure_pool(SPACE_NAME_POOL, target)
        owner = self._space_owner()
        categories = self.space_categories or ['라이브클럽']
        descriptions = SPACE_DESCRIPTION_POOL or ['복합문화공간입니다.']
        regions = self._balanced_regions(target, minimum_ratio=0.6)
        spaces: List[Space] = []

        with transaction.atomic():
            for idx, name in enumerate(names[:target]):
                slug = self._slugify(name)
                region = regions[idx]
                category = random.choice(categories)
                genres = ', '.join(self._sample(self.genres, 2))
                equipments = ', '.join(self._sample(self.equipment, 2, 3))
                space = Space.objects.create(
                    owner=owner,
                    name=name,
                    category=category,
                    genres=genres,
                    region=region,
                    address=f'{region} 문화로 {random.randint(10, 199)}',
                    capacity=random.randint(80, 400),
                    description=random.choice(descriptions),
                    equipments=equipments,
                    image_url=f'https://images.dyve.local/spaces/{slug}.jpg',
                )
                spaces.append(space)
        return spaces

    def seed_events(
        self,
        count: int | None = None,
        *,
        artists: Sequence[Artist] | None = None,
        spaces: Sequence[Space] | None = None,
    ) -> Dict[str, int | List[Event]]:
        target = max(count or self.EVENT_MIN, self.EVENT_MIN)
        artists_list = list(artists) if artists else list(Artist.objects.all())
        spaces_list = list(spaces) if spaces else list(Space.objects.all())
        artists_created = 0
        spaces_created = 0

        if not artists_list:
            artists_list = self.seed_artists()
            artists_created = len(artists_list)
        if not spaces_list:
            spaces_list = self.seed_spaces()
            spaces_created = len(spaces_list)

        titles = self._ensure_pool(EVENT_TITLE_POOL, target)
        entry_schedule = self._entry_type_schedule(target)
        reservation_flags = self._reservation_schedule(target)
        space_schedule = self._space_schedule(target, spaces_list)
        events: List[Event] = []

        with transaction.atomic():
            for idx in range(target):
                space = space_schedule[idx]
                title = titles[idx]
                entry_type = entry_schedule[idx]
                allow_reservation = reservation_flags[idx]
                slug = self._slugify(title)
                price = random.randint(20000, 70000)
                if random.random() < 0.15:
                    price = 0
                is_free = price == 0
                genre = random.choice(self.genres) if self.genres else 'Indie'
                event = Event.objects.create(
                    title=title,
                    description=random.choice(EVENT_DESCRIPTION_POOL),
                    genre=genre,
                    region=space.region,
                    date=timezone.localdate() + timedelta(days=random.randint(5, 60)),
                    time=dtime(hour=random.choice(EVENT_HOUR_CHOICES), minute=random.choice(EVENT_MINUTE_CHOICES)),
                    venue_name=space.name,
                    address=space.address,
                    price=price,
                    is_free=is_free,
                    entry_type=entry_type,
                    image_url=f'https://images.dyve.local/events/{slug}.jpg',
                    allow_dyve_reservation=allow_reservation,
                    advertise=random.choice([True, False]),
                    space=space,
                )
                artist_sample_size = 1 if len(artists_list) == 1 else random.randint(1, min(2, len(artists_list)))
                event.artists.set(random.sample(artists_list, k=artist_sample_size))
                events.append(event)

        dyve_available = sum(1 for allowed in reservation_flags if allowed)
        return {
            'events': events,
            'events_created': len(events),
            'artists_created': artists_created,
            'spaces_created': spaces_created,
            'dyve_available': dyve_available,
        }

    def seed_all(
        self,
        *,
        reset: bool = False,
        artist_count: int | None = None,
        space_count: int | None = None,
        event_count: int | None = None,
    ) -> Dict[str, int]:
        if reset:
            Event.objects.all().delete()
            Space.objects.all().delete()
            Artist.objects.all().delete()

        artists = self.seed_artists(artist_count)
        spaces = self.seed_spaces(space_count)
        event_result = self.seed_events(event_count, artists=artists, spaces=spaces)
        return {
            'artists_created': len(artists) + int(event_result['artists_created']),
            'spaces_created': len(spaces) + int(event_result['spaces_created']),
            'events_created': int(event_result['events_created']),
            'dyve_available': int(event_result['dyve_available']),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _slugify(self, value: str) -> str:
        slug = slugify(value)
        return slug or 'dyve-item'

    def _space_owner(self):
        owner, created = self.user_model.objects.get_or_create(
            username='dyve_seed_owner',
            defaults={
                'email': 'seed-owner@dyve.dev',
                'first_name': 'Seed',
                'last_name': 'Owner',
            },
        )
        if created:
            owner.set_password('dyve_seed_owner')
            owner.save(update_fields=['password'])
        return owner

    def _sample(self, source: Sequence[str], min_items: int, max_items: int | None = None) -> List[str]:
        if not source:
            return []
        upper_bound = len(source) if max_items is None else min(max_items, len(source))
        lower_bound = min_items if min_items <= upper_bound else upper_bound
        size = random.randint(lower_bound, upper_bound) if upper_bound else 0
        return random.sample(list(source), k=size) if size else []

    def _ensure_pool(self, pool: Sequence[str], target: int) -> List[str]:
        items = list(pool)
        results: List[str] = []
        while len(results) < target:
            if not items:
                items = list(pool)
            results.append(items.pop(random.randrange(len(items))))
        random.shuffle(results)
        return results

    def _balanced_regions(self, total: int, minimum_ratio: float) -> List[str]:
        if not self.regions:
            return ['서울'] * total
        seoul_required = min(total, math.ceil(total * minimum_ratio))
        other_regions = [region for region in self.regions if region != '서울'] or ['서울']
        assignments = ['서울'] * seoul_required
        while len(assignments) < total:
            assignments.append(random.choice(other_regions))
        random.shuffle(assignments)
        return assignments

    def _entry_type_schedule(self, count: int) -> List[str]:
        schedule: List[str] = []
        minimum_each = 5 if count >= 15 else max(1, count // len(ENTRY_TYPES))
        for entry_type in ENTRY_TYPES:
            required = min(minimum_each, max(0, count - len(schedule)))
            schedule.extend([entry_type] * required)
        while len(schedule) < count:
            schedule.append(random.choice(ENTRY_TYPES))
        random.shuffle(schedule)
        return schedule

    def _reservation_schedule(self, count: int) -> List[bool]:
        guaranteed = min(15, count)
        schedule = [True] * guaranteed
        schedule.extend(random.choice([True, False]) for _ in range(count - guaranteed))
        random.shuffle(schedule)
        return schedule

    def _space_schedule(self, count: int, spaces: Sequence[Space]) -> List[Space]:
        if not spaces:
            raise ValueError('At least one space is required to create events.')
        seoul_spaces = [space for space in spaces if space.region == '서울']
        other_spaces = [space for space in spaces if space.region != '서울']
        if not seoul_spaces:
            seoul_spaces = list(spaces)
        seoul_required = min(count, math.ceil(count * 0.7))
        schedule: List[Space] = []
        for idx in range(count):
            if idx < seoul_required and seoul_spaces:
                schedule.append(seoul_spaces[idx % len(seoul_spaces)])
            else:
                pool = other_spaces or seoul_spaces
                schedule.append(pool[idx % len(pool)])
        random.shuffle(schedule)
        return schedule


def seed_all(reset: bool = False) -> Dict[str, int]:
    return DummySeedService().seed_all(reset=reset)


def seed_artists(count: int | None = None) -> Dict[str, int]:
    service = DummySeedService()
    artists = service.seed_artists(count)
    return {
        'artists_created': len(artists),
        'spaces_created': 0,
        'events_created': 0,
        'dyve_available': 0,
    }


def seed_spaces(count: int | None = None) -> Dict[str, int]:
    service = DummySeedService()
    spaces = service.seed_spaces(count)
    return {
        'artists_created': 0,
        'spaces_created': len(spaces),
        'events_created': 0,
        'dyve_available': 0,
    }


def seed_events(count: int | None = None) -> Dict[str, int]:
    service = DummySeedService()
    result = service.seed_events(count)
    return {
        'artists_created': int(result['artists_created']),
        'spaces_created': int(result['spaces_created']),
        'events_created': int(result['events_created']),
        'dyve_available': int(result['dyve_available']),
    }
