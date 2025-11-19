"""Curated dummy dataset builder that uses local images + Cloudinary."""

from __future__ import annotations

import random
from datetime import datetime, time as dtime, timedelta
from itertools import cycle
from pathlib import Path
from typing import Dict, List, Sequence

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify

from core.constants import ARTIST_CATEGORIES, GENRES, REGIONS, SPACE_CATEGORIES
from core.models import Artist, Event, Space
from utils.dummy_image_loader import DummyImageLoader


ARTIST_PROFILES = [
    {
        "name": "Luna Quartet",
        "category": "재즈 앙상블",
        "genres": ["Jazz", "R&B"],
        "equipments": ["mic", "speaker"],
        "history": "성수 재즈 나잇에서 매달 레지던시를 진행하는 모던 재즈 팀입니다.",
        "phone": "010-1204-7785",
    },
    {
        "name": "Blue Note Ensemble",
        "category": "클래식 앙상블",
        "genres": ["Jazz", "클래식"],
        "equipments": ["mic", "string pickup"],
        "history": "남산 블루노트 스페이스에서 실내악과 재즈를 결합한 프로젝트를 운영합니다.",
        "phone": "010-2350-4410",
    },
    {
        "name": "HypeLab Crew",
        "category": "힙합 크루",
        "genres": ["Hip-Hop", "Electronic"],
        "equipments": ["mixer", "monitor"],
        "history": "이태원 스트리트 브랜드와 협업해 라이브 쇼케이스를 연속 기획한 힙합 크루입니다.",
        "phone": "010-3480-9921",
    },
    {
        "name": "The Wanderers",
        "category": "싱어송라이터",
        "genres": ["Indie", "Folk"],
        "equipments": ["mic", "acoustic amp"],
        "history": "홍대 문학광장에서 도심 버스킹 투어를 이어가는 싱어송라이터 집단입니다.",
        "phone": "010-4522-1805",
    },
    {
        "name": "MoonJazz Syndicate",
        "category": "밴드",
        "genres": ["Jazz", "Rock"],
        "equipments": ["mic", "guitar amp"],
        "history": "한강 야외무대와 클럽을 넘나들며 협업 세션을 펼치는 재즈 밴드입니다.",
        "phone": "010-5699-0340",
    },
    {
        "name": "Electronic Pulse",
        "category": "DJ",
        "genres": ["Electronic", "디제잉"],
        "equipments": ["mixer", "controller"],
        "history": "성수 레코드숍과 협력해 심야 라이브를 기획하는 전자 음악 듀오입니다.",
        "phone": "010-6724-8042",
    },
    {
        "name": "Urban Groove Unit",
        "category": "퍼포먼스 아티스트",
        "genres": ["R&B", "Hip-Hop"],
        "equipments": ["mic", "wireless in-ear"],
        "history": "도심 아트마켓과 연동된 라이브 세션과 퍼포먼스를 선보이는 팀입니다.",
        "phone": "010-7012-1134",
    },
    {
        "name": "Resonance Project",
        "category": "국악 프로젝트",
        "genres": ["Indie", "Jazz"],
        "equipments": ["janggu", "loop station"],
        "history": "국악기와 모던 사운드를 결합해 광주 컬처랩과 협업한 프로젝트입니다.",
        "phone": "010-8250-6643",
    },
    {
        "name": "Studio Harmonics",
        "category": "프로듀서 팀",
        "genres": ["Electronic", "Indie"],
        "equipments": ["synth", "studio monitor"],
        "history": "잠실 스튜디오 단지에서 신스·모듈러 기반 레지던시를 운영합니다.",
        "phone": "010-9300-8821",
    },
    {
        "name": "Indie Circle Collective",
        "category": "보컬 그룹",
        "genres": ["Indie", "R&B"],
        "equipments": ["vocal mic", "in-ear"],
        "history": "독립 레이블 커뮤니티가 큐레이션한 보컬 앙상블로 전국 투어를 진행했습니다.",
        "phone": "010-9977-1204",
    },
]

SPACE_PROFILES = [
    {
        "name": "홍대 Moonlight Stage",
        "region": "서울",
        "category": "라이브클럽",
        "capacity": 120,
        "address": "서울 마포구 와우산로 66 B1",
        "description": "홍대 와우산로에 위치한 레지던시 기반 라이브 클럽입니다.",
        "genres": "Indie, Rock",
        "equipments": ["마이크", "앰프"],
        "phone": "02-3110-7720",
    },
    {
        "name": "이태원 Velvet Lounge",
        "region": "서울",
        "category": "바/펍",
        "capacity": 80,
        "address": "서울 용산구 이태원로 223",
        "description": "월간 글로벌 셋리스트를 선보이는 저녁 쇼케이스 라운지입니다.",
        "genres": "Jazz, Electronic",
        "equipments": ["mixer", "DJ 장비"],
        "phone": "02-7788-2200",
    },
    {
        "name": "서울 Riverside Atrium",
        "region": "서울",
        "category": "멀티홀",
        "capacity": 200,
        "address": "서울 영등포구 여의대로 24",
        "description": "한강 수변이 보이는 유리돔 복합문화공간입니다.",
        "genres": "Jazz, Indie",
        "equipments": ["무대 조명", "프로젝터"],
        "phone": "02-9112-0404",
    },
    {
        "name": "부산 Horizon Hall",
        "region": "경상",
        "category": "공연장",
        "capacity": 200,
        "address": "부산 수영구 광안해변로 203",
        "description": "광안대교 뷰를 품은 미드사이즈 크리에이티브 홀입니다.",
        "genres": "Rock, Electronic",
        "equipments": ["라인어레이", "비주얼 콘솔"],
        "phone": "02-9201-4410",
    },
    {
        "name": "대구 Urban Warehouse",
        "region": "경상",
        "category": "소극장",
        "capacity": 120,
        "address": "대구 중구 동성로4길 89",
        "description": "창고형 구조를 살린 라이브 웨어하우스 공간입니다.",
        "genres": "Hip-Hop, Electronic",
        "equipments": ["서브우퍼", "DJ 부스"],
        "phone": "02-9300-1102",
    },
    {
        "name": "광주 Culture Lab",
        "region": "전라",
        "category": "갤러리",
        "capacity": 80,
        "address": "광주 동구 예술길 22",
        "description": "시각예술과 라이브셋을 결합한 연구형 갤러리입니다.",
        "genres": "Indie, Jazz",
        "equipments": ["스트링 라이트", "포터블 PA"],
        "phone": "02-9420-2882",
    },
    {
        "name": "제주 Old Town Warehouse",
        "region": "제주",
        "category": "루프탑",
        "capacity": 80,
        "address": "제주 제주시 관덕로8길 15",
        "description": "구도심 루프탑을 재해석한 야외 퍼포먼스 무대입니다.",
        "genres": "Indie, Electronic",
        "equipments": ["배터리 스피커", "앰비언트 데크"],
        "phone": "02-9770-0099",
    },
    {
        "name": "인천 Harbor Stage",
        "region": "인천",
        "category": "멀티홀",
        "capacity": 120,
        "address": "인천 중구 제물량로 12",
        "description": "항구 레일을 살린 복합 스테이지입니다.",
        "genres": "Rock, Jazz",
        "equipments": ["mixer", "in-ear system"],
        "phone": "02-9450-2207",
    },
    {
        "name": "성수 Concrete Box",
        "region": "서울",
        "category": "멀티홀",
        "capacity": 50,
        "address": "서울 성동구 성수이로 78",
        "description": "모듈러 아티스트가 상주하는 콘크리트 감성의 박스 스테이지입니다.",
        "genres": "Electronic, Indie",
        "equipments": ["모듈러 데스크", "라이팅 그리드"],
        "phone": "02-9012-6620",
    },
    {
        "name": "잠실 Live Plaza",
        "region": "서울",
        "category": "공연장",
        "capacity": 200,
        "address": "서울 송파구 올림픽로 300",
        "description": "대형 쇼케이스와 브랜드 페스티벌을 수용하는 라이브 플라자입니다.",
        "genres": "Pop, Indie",
        "equipments": ["LED 월", "인하우스 스태프"],
        "phone": "02-9901-1125",
    },
]

EVENT_PRESETS = [
    {"title": "Indie Garden Concert", "description": "성수 도심정원에서 펼쳐지는 인디 피크닉 쇼케이스", "genre": "Indie", "schedule": "2024-09-05 19:30"},
    {"title": "Resonance Field", "description": "재즈 스트링과 일렉트로닉을 잇는 협업 세션", "genre": "Jazz", "schedule": "2024-09-06 20:00"},
    {"title": "Studio 42 Residency", "description": "스튜디오 팀의 공개 레지던시 쇼", "genre": "Indie", "schedule": "2024-09-07 18:00"},
    {"title": "Electronic Midnight Session", "description": "심야 시티팝과 하우스를 잇는 라이브", "genre": "Electronic", "schedule": "2024-09-08 22:00"},
    {"title": "Citywave Showcase", "description": "도심 어반 크루가 꾸미는 라이브 쇼", "genre": "Hip-Hop", "schedule": "2024-09-09 19:30"},
    {"title": "Culture Lab Open Stage", "description": "광주 컬처랩 시그니처 오픈 스테이지", "genre": "Indie", "schedule": "2024-09-10 20:00"},
    {"title": "Jazz Horizon Night", "description": "강변 노을과 함께하는 모던 재즈 나잇", "genre": "Jazz", "schedule": "2024-09-11 19:00"},
    {"title": "Urban Light Festival", "description": "루프탑 라이트 인스톨과 전자음악 퍼포먼스", "genre": "Electronic", "schedule": "2024-09-12 21:00"},
    {"title": "Groove District Live", "description": "도심 펑크·소울 레이블 합동 쇼", "genre": "R&B", "schedule": "2024-09-13 19:30"},
    {"title": "Northern Echo Sessions", "description": "북부 생활권 팀들의 합동 세션", "genre": "Rock", "schedule": "2024-09-14 18:30"},
    {"title": "Solaris Listening Party", "description": "힙합과 신스웨이브의 리스닝 파티", "genre": "Electronic", "schedule": "2024-09-15 20:30"},
    {"title": "Culture Pulse Night", "description": "도심 문화살롱 협업 미니 페스티벌", "genre": "Indie", "schedule": "2024-09-16 19:00"},
    {"title": "Harbor Sunset Rooms", "description": "인천 항만 노을을 배경으로 한 스테이지", "genre": "Indie", "schedule": "2024-09-17 18:30"},
    {"title": "Busan Pulse Exchange", "description": "서울×부산 뮤지션 맞교환 프로그램", "genre": "Rock", "schedule": "2024-09-18 20:00"},
    {"title": "Concrete Dreams Salon", "description": "성수 콘크리트 박스에서 펼치는 사운드 살롱", "genre": "Indie", "schedule": "2024-09-19 19:30"},
    {"title": "Jeju Night Radar", "description": "제주 구도심 루프탑 일렉트로닉 쇼", "genre": "Electronic", "schedule": "2024-09-20 20:30"},
    {"title": "Loft Layers Residency", "description": "DJ와 라이브밴드가 동시에 전개되는 멀티 셋", "genre": "Electronic", "schedule": "2024-09-21 21:00"},
    {"title": "Sound Warehouse Dialogue", "description": "창고형 무대에서 진행하는 토크 콘서트", "genre": "Indie", "schedule": "2024-09-22 19:00"},
    {"title": "Culture Loop Marathon", "description": "도시 순환형 퍼포먼스 마라톤", "genre": "Indie", "schedule": "2024-09-23 19:00"},
    {"title": "Indie Cartography Live", "description": "지도를 타고 이동하는 로컬 인디 쇼", "genre": "Indie", "schedule": "2024-09-24 19:30"},
    {"title": "Velvet Analog Weekender", "description": "아날로그 신스와 재즈의 주말 잼", "genre": "Jazz", "schedule": "2024-09-25 21:00"},
    {"title": "Seaside Transit Pop-up", "description": "바다 이동형 팝업 퍼포먼스", "genre": "Indie", "schedule": "2024-09-26 18:30"},
    {"title": "Electronic Harbor Summit", "description": "항만 야경을 배경으로 한 일렉트로닉 세션", "genre": "Electronic", "schedule": "2024-09-27 20:00"},
    {"title": "Garden City Listening Lab", "description": "가든 시티 테라스에서 여는 리스닝 랩", "genre": "Indie", "schedule": "2024-09-28 17:30"},
    {"title": "Skyline Modular Revue", "description": "모듈러 신스와 퍼포먼스가 어우러진 쇼", "genre": "Electronic", "schedule": "2024-09-29 20:30"},
]

TICKET_TYPES = ["입장확인", "좌석", "스탠딩"]
PRICE_OPTIONS = [0, 10000, 15000, 20000, 25000, 30000]

SINGLE_ARTIST_NAMES = [
    "Canopy Ensemble",
    "Riverline Project",
    "Neon Transit",
    "Atlas Folk",
    "Parallel Lights",
]
ARTIST_STORIES = [
    "서울 성수동에서 모듈러 신스를 기반으로 라이브를 진행하는 팀",
    "부산 해변가 팝업 스테이지를 투어한 싱어송라이터 듀오",
    "재즈와 시티팝을 결합한 밤 시간대 쇼케이스 팀",
    "국내외 아트페어에서 사운드 퍼포먼스를 선보인 프로젝트",
]
SPACE_MOODS = ["따뜻한", "도시적인", "빈티지", "갤러리", "루프탑"]
EVENT_TITLES = [
    "Atlas Night Session",
    "Neon Canvas Live",
    "Parallel Garden Showcase",
    "Transit Stories",
    "Midnight Canopy",
]
EVENT_DESCRIPTIONS = [
    "신진 아티스트와 빈티지 디제잉을 결합한 도심형 공연",
    "아트워크 전시와 함께 진행되는 몰입형 라이브",
    "퍼포먼스와 토크세션이 함께하는 하이브리드 행사",
]
RUNNING_TIMES = [60, 75, 90]


class DummyDataBuilder:
    """Builds curated artists, spaces, and events with Cloudinary-hosted images."""

    def __init__(self):
        self.image_loader = DummyImageLoader(
            base_dir=Path(settings.BASE_DIR) / 'dummy_images',
            folders={'artist': 'artist_profiles', 'space': 'space_profiles', 'poster': 'posters'},
            consume_once=True,
        )
        self.random = random.Random(20240905)

    def reset_all(self) -> None:
        Event.objects.all().delete()
        Space.objects.all().delete()
        Artist.objects.all().delete()

    def create_artists(self) -> List[Artist]:
        artists: List[Artist] = []
        for profile in ARTIST_PROFILES:
            artist = Artist.objects.create(
                name=profile["name"],
                category=profile["category"],
                genres=", ".join(profile["genres"]),
                equipments=", ".join(profile["equipments"]),
                portfolio_url="https://example.com/artist",
                image_url=self.image_loader.next_artist_image(),
                history=profile["history"],
                phone=profile["phone"],
            )
            artists.append(artist)
        return artists

    def create_spaces(self) -> List[Space]:
        owner = _get_dummy_space_owner()
        spaces: List[Space] = []
        for profile in SPACE_PROFILES:
            space = Space.objects.create(
                owner=owner,
                name=profile["name"],
                category=profile["category"],
                genres=profile["genres"],
                region=profile["region"],
                address=profile["address"],
                capacity=profile["capacity"],
                description=profile["description"],
                equipments=", ".join(profile["equipments"]),
                image_url=self.image_loader.next_space_image(),
                phone=profile["phone"],
            )
            spaces.append(space)
        return spaces

    def create_events(self, artists: Sequence[Artist], spaces: Sequence[Space]) -> List[Event]:
        if not artists or not spaces:
            raise ValueError('Artists and spaces must exist before creating events.')

        seoul_spaces = [space for space in spaces if space.region == '서울']
        non_seoul_spaces = [space for space in spaces if space.region != '서울']
        if not seoul_spaces:
            raise ValueError('At least one 서울 공간이 필요합니다.')
        if not non_seoul_spaces:
            raise ValueError('서울 외 공간이 필요합니다.')

        ticket_cycle = cycle(TICKET_TYPES)
        price_cycle = cycle(PRICE_OPTIONS)
        seoul_target = round(len(EVENT_PRESETS) * 0.7)
        events: List[Event] = []
        seoul_count = 0

        for idx, preset in enumerate(EVENT_PRESETS):
            if seoul_count < seoul_target or not non_seoul_spaces:
                space = self.random.choice(seoul_spaces)
                seoul_count += 1
            else:
                space = self.random.choice(non_seoul_spaces)

            entry_type = next(ticket_cycle)
            price = next(price_cycle)
            date_value, time_value = self._parse_schedule(preset["schedule"])
            event = Event.objects.create(
                title=preset["title"],
                description=preset["description"],
                genre=preset["genre"],
                region=space.region,
                date=date_value,
                time=time_value,
                venue_name=space.name,
                address=space.address,
                price=price,
                is_free=price == 0,
                entry_type=entry_type,
                image_url=self.image_loader.next_event_poster(),
                allow_dyve_reservation=True,
                advertise=idx % 4 == 0,
                space=space,
            )
            lineup_size = self.random.choice([1, 2, 3])
            event.artists.set(self.random.sample(list(artists), k=lineup_size))
            events.append(event)

        return events

    def create_all(self) -> Dict[str, int]:
        artists = self.create_artists()
        spaces = self.create_spaces()
        events = self.create_events(artists, spaces)
        return {
            'artists_created': len(artists),
            'spaces_created': len(spaces),
            'events_created': len(events),
        }

    def _parse_schedule(self, schedule: str):
        dt = datetime.strptime(schedule, '%Y-%m-%d %H:%M')
        aware = timezone.make_aware(dt, timezone.get_current_timezone())
        return aware.date(), aware.time().replace(second=0, microsecond=0)


def seed_all(clear_existing: bool = True) -> Dict[str, int]:
    builder = DummyDataBuilder()
    if clear_existing:
        builder.reset_all()
    return builder.create_all()


def create_dummy_artist(image_loader: DummyImageLoader | None = None):
    loader = image_loader or DummyImageLoader()
    name = random.choice(SINGLE_ARTIST_NAMES)
    description = random.choice(ARTIST_STORIES)
    category = random.choice(ARTIST_CATEGORIES)
    genres = ', '.join(random.sample(GENRES, k=min(2, len(GENRES))))
    equipments = random.sample(
        [
            'mic',
            'monitor speaker',
            'mixer',
            'dj controller',
            'acoustic amp',
        ],
        k=2,
    )
    portfolio_slug = slugify(name)
    portfolio = f'https://example.com/artists/{portfolio_slug}'
    image_url = loader.next_artist_image()
    artist = Artist.objects.create(
        name=name,
        category=category,
        genres=genres,
        equipments=', '.join(equipments),
        portfolio_url=portfolio,
        image_url=image_url,
        history=description,
        phone=f"010-{random.randint(1000, 9999):04d}-{random.randint(0, 9999):04d}",
    )
    meta = {
        'name': name,
        'description': description,
        'category': category,
        'profile_image_url': image_url,
        'portfolio_link': portfolio,
        'required_equipment': equipments,
    }
    return artist, meta


def create_dummy_space(image_loader: DummyImageLoader | None = None):
    loader = image_loader or DummyImageLoader()
    name = random.choice([
        '성수 Lofi Lab',
        '부산 Wave Loft',
        '홍대 Resonance Room',
        '제주 Forest Stage',
        '대구 Warehouse 79',
    ])
    region = random.choice([r for r in REGIONS if r])
    mood = random.choice(SPACE_MOODS)
    capacity = random.choice([50, 80, 120, 200])
    description = f"{mood} 무드의 로컬 아트 공연장입니다."
    address = f"{region} 문화로 {random.randint(10, 199)}"
    phone = f"02-{random.randint(1000, 9999):04d}-{random.randint(1000, 9999):04d}"
    image_url = loader.next_space_image()
    owner = _get_dummy_space_owner()
    space = Space.objects.create(
        owner=owner,
        name=name,
        category=random.choice(SPACE_CATEGORIES) if SPACE_CATEGORIES else '공연장',
        genres=', '.join(random.sample(GENRES, k=min(2, len(GENRES)))),
        region=region,
        address=address,
        capacity=capacity,
        description=description,
        equipments='기본 음향, 조명',
        image_url=image_url,
        phone=phone,
    )
    meta = {
        'name': name,
        'description': description,
        'region': region,
        'address': address,
        'image_url': image_url,
        'capacity': capacity,
        'mood': mood,
        'phone_number': phone,
    }
    return space, meta


def create_dummy_event(
    artist: Artist,
    space: Space,
    image_loader: DummyImageLoader | None = None,
):
    loader = image_loader or DummyImageLoader()
    poster_url = loader.next_event_poster()
    title = random.choice(EVENT_TITLES)
    description = random.choice(EVENT_DESCRIPTIONS)
    future_date = timezone.localdate() + timedelta(days=random.randint(7, 35))
    future_time = dtime(hour=random.choice([18, 19, 20, 21]), minute=random.choice([0, 15, 30, 45]))
    future_start = timezone.make_aware(datetime.combine(future_date, future_time), timezone.get_current_timezone())
    date_value = future_start.date()
    time_value = future_start.time().replace(second=0, microsecond=0)
    genre = random.choice(GENRES) if GENRES else 'Indie'
    price = random.choice(PRICE_OPTIONS)
    entry_type = random.choice(TICKET_TYPES)
    running_time = random.choice(RUNNING_TIMES)
    event = Event.objects.create(
        title=title,
        description=description,
        genre=genre,
        region=space.region,
        date=date_value,
        time=time_value,
        venue_name=space.name,
        address=space.address,
        price=price,
        is_free=price == 0,
        entry_type=entry_type,
        image_url=poster_url,
        allow_dyve_reservation=True,
        advertise=False,
        space=space,
    )
    event.artists.set([artist])
    meta = {
        'title': title,
        'description': description,
        'poster_image_url': poster_url,
        'date_time': future_start.strftime('%Y-%m-%d %H:%M'),
        'genre': genre,
        'running_time': running_time,
        'price': price,
        'entry_type': entry_type,
    }
    return event, meta


def create_one() -> Dict[str, Dict[str, object]]:
    loader = DummyImageLoader()
    artist, artist_meta = create_dummy_artist(loader)
    space, space_meta = create_dummy_space(loader)
    event, event_meta = create_dummy_event(artist, space, loader)
    return {
        'artist': {
            'id': artist.id,
            **artist_meta,
        },
        'space': {
            'id': space.id,
            **space_meta,
        },
        'event': {
            'id': event.id,
            'artist_id': artist.id,
            'space_id': space.id,
            **event_meta,
        },
    }


def _get_dummy_space_owner():
    user_model = get_user_model()
    owner, _ = user_model.objects.get_or_create(
        username='dyve_dummy_host',
        defaults={
            'email': 'dummy-host@dyve.local',
            'first_name': 'Dummy',
            'last_name': 'Host',
        },
    )
    if not owner.has_usable_password():
        owner.set_unusable_password()
        owner.save(update_fields=['password'])
    return owner
