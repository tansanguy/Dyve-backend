"""Reusable dummy data generator used by dev-only endpoints."""

from __future__ import annotations

import random
from datetime import time as dtime, timedelta
from typing import List, Sequence, Tuple

from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Artist, Event, Space
from utils.json_loader import load_json

ENTRY_TYPES = ['standing', 'seat', 'free']


class DummyDataGenerator:
    EVENT_COUNT = 10
    ARTIST_COUNT = 5
    SPACE_COUNT = 5
    SEOUL_RATIO = 0.7

    def __init__(self):
        self.user_model = get_user_model()
        self.genres = load_json('genres')
        self.regions = load_json('regions')
        self.space_categories = load_json('space_categories')
        self.equipment_options = load_json('equipment')

    def _random_region(self) -> str:
        if not self.regions:
            return '서울'

        if '서울' in self.regions and random.random() < self.SEOUL_RATIO:
            return '서울'

        candidates = [region for region in self.regions if region != '서울']
        return random.choice(candidates or self.regions)

    def _random_time(self) -> dtime:
        hour = random.randint(17, 22)
        minute = random.choice([0, 15, 30, 45])
        return dtime(hour=hour, minute=minute)

    def _random_equipment(self, *, min_items: int = 1, max_items: int = 3) -> List[str]:
        if not self.equipment_options:
            return []

        upper = min(max_items, len(self.equipment_options))
        count = random.randint(min_items, max(upper, min_items))
        return random.sample(self.equipment_options, k=count)

    def _random_genre_list(self, *, max_items: int = 2) -> List[str]:
        if not self.genres:
            return []

        upper = min(max_items, len(self.genres))
        count = random.randint(1, max(upper, 1))
        return random.sample(self.genres, k=count)

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

    def create_artists(self, count: int | None = None) -> List[Artist]:
        count = count or self.ARTIST_COUNT
        artists: List[Artist] = []
        for _ in range(count):
            suffix = random.randint(1000, 9999)
            genres = ', '.join(self._random_genre_list())
            equipments = ', '.join(self._random_equipment())
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

    def create_spaces(self, count: int | None = None) -> List[Space]:
        count = count or self.SPACE_COUNT
        owner = self._get_space_owner()
        spaces: List[Space] = []
        for _ in range(count):
            suffix = random.randint(1000, 9999)
            region = self._random_region()
            equipments = ', '.join(self._random_equipment(min_items=1, max_items=3))
            genres = ', '.join(self._random_genre_list())
            category = random.choice(self.space_categories) if self.space_categories else '기타'
            space = Space.objects.create(
                owner=owner,
                name=f'Dummy Space #{suffix}',
                category=category,
                genres=genres,
                region=region,
                address=f'{region} 테스트로 {random.randint(1, 200)}',
                capacity=random.randint(40, 300),
                description='프론트엔드 개발용 임시 공간입니다.',
                equipments=equipments,
                image_url=f'https://placehold.co/600x400?text=Space{suffix}',
            )
            spaces.append(space)
        return spaces

    def create_events(
        self,
        count: int | None = None,
        *,
        spaces: Sequence[Space] | None = None,
        artists: Sequence[Artist] | None = None,
        ensure_relations: bool = True,
    ) -> Tuple[List[Event], int, int]:
        count = count or self.EVENT_COUNT
        created_events: List[Event] = []
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
            genre = random.choice(self.genres) if self.genres else 'Indie'
            event = Event.objects.create(
                title=f'Dummy Event #{suffix}',
                description='프론트 테스트용 임시 공연입니다.',
                genre=genre,
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
                sample_size = random.randint(1, max_artists) if max_artists else 0
                if sample_size:
                    event.artists.set(random.sample(list(artists), k=sample_size))
            created_events.append(event)

        return created_events, artists_created, spaces_created
