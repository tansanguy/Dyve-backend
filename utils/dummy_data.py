"""Curated dummy-data builder for artists/spaces/events."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime
from itertools import cycle
from typing import Dict, Iterable, List, Sequence

import cloudinary.uploader
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from core.models import Artist, Event, Space

ARTIST_NAMES = [
    "Luna Quartet",
    "Blue Note Ensemble",
    "HypeLab Crew",
    "The Wanderers",
    "MoonJazz Syndicate",
    "Electronic Pulse",
    "Urban Groove Unit",
    "Resonance Project",
    "Studio Harmonics",
    "Indie Circle Collective",
]

SPACE_PROFILES = [
    {
        "name": "홍대 Moonlight Stage",
        "region": "서울",
        "region_group": "서울",
        "category": "라이브클럽",
        "description": "홍대 와우산 퍼레이드와 연계된 레지던시 라이브 클럽",
        "capacity": 120,
        "genres": "Indie, Rock",
        "address": "서울 마포구 와우산로 66 B1",
        "equipments": ["풀밴드 PA", "스테이지 조명"],
        "phone": "02-3110-7720",
        "image_slug": "hongdae-moonlight",
    },
    {
        "name": "이태원 Velvet Lounge",
        "region": "서울",
        "region_group": "서울",
        "category": "바/펍",
        "description": "이태원 다국적 신을 담는 저녁 쇼케이스 라운지",
        "capacity": 80,
        "genres": "Jazz, Electronic",
        "address": "서울 용산구 이태원로 223",
        "equipments": ["mixer", "turntable"],
        "phone": "02-7788-2200",
        "image_slug": "itaewon-velvet",
    },
    {
        "name": "서울 Riverside Atrium",
        "region": "서울",
        "region_group": "서울",
        "category": "멀티홀",
        "description": "한강 수변을 내려다보는 유리돔 복합 문화 아트리움",
        "capacity": 200,
        "genres": "Jazz, Indie",
        "address": "서울 영등포구 여의대로 24",
        "equipments": ["projector", "monitor"],
        "phone": "02-9112-0404",
        "image_slug": "seoul-riverside",
    },
    {
        "name": "부산 Horizon Hall",
        "region": "경상",
        "region_group": "지방",
        "category": "공연장",
        "description": "광안대교 뷰를 담는 미드사이즈 크리에이티브 홀",
        "capacity": 200,
        "genres": "Rock, Electronic",
        "address": "부산 수영구 광안해변로 203",
        "equipments": ["line array", "visual console"],
        "phone": "02-9201-4410",
        "image_slug": "busan-horizon",
    },
    {
        "name": "대구 Urban Warehouse",
        "region": "경상",
        "region_group": "지방",
        "category": "소극장",
        "description": "리모델링된 창고형 라이브 웨어하우스",
        "capacity": 120,
        "genres": "Hip-Hop, Electronic",
        "address": "대구 중구 동성로4길 89",
        "equipments": ["subwoofer", "dj booth"],
        "phone": "02-9300-1102",
        "image_slug": "daegu-warehouse",
    },
    {
        "name": "광주 Culture Lab",
        "region": "전라",
        "region_group": "지방",
        "category": "갤러리",
        "description": "시각예술과 라이브셋을 함께 담는 컬쳐 랩",
        "capacity": 80,
        "genres": "Indie, Jazz",
        "address": "광주 동구 예술길 22",
        "equipments": ["string lights", "portable pa"],
        "phone": "02-9420-2882",
        "image_slug": "gwangju-lab",
    },
    {
        "name": "제주 Old Town Warehouse",
        "region": "제주",
        "region_group": "지방",
        "category": "루프탑",
        "description": "제주 구도심을 내려보는 루프탑 공연창고",
        "capacity": 80,
        "genres": "Indie, Electronic",
        "address": "제주 제주시 관덕로8길 15",
        "equipments": ["battery speaker", "ambient deck"],
        "phone": "02-9770-0099",
        "image_slug": "jeju-warehouse",
    },
    {
        "name": "인천 Harbor Stage",
        "region": "인천",
        "region_group": "지방",
        "category": "멀티홀",
        "description": "항구 레일을 살린 복합 스테이지",
        "capacity": 120,
        "genres": "Rock, Jazz",
        "address": "인천 중구 제물량로 12",
        "equipments": ["mixer", "in-ear system"],
        "phone": "02-9450-2207",
        "image_slug": "incheon-harbor",
    },
    {
        "name": "성수 Concrete Box",
        "region": "서울",
        "region_group": "서울",
        "category": "멀티홀",
        "description": "레지던시 팀이 상시 상주하는 시멘트 박스",
        "capacity": 50,
        "genres": "Electronic, Indie",
        "address": "서울 성동구 성수이로 78",
        "equipments": ["modular desk", "lighting grid"],
        "phone": "02-9012-6620",
        "image_slug": "seongsu-box",
    },
    {
        "name": "잠실 Live Plaza",
        "region": "서울",
        "region_group": "서울",
        "category": "공연장",
        "description": "대형 쇼케이스를 위한 잠실 컬처 플라자",
        "capacity": 200,
        "genres": "Pop, Indie",
        "address": "서울 송파구 올림픽로 300",
        "equipments": ["led wall", "in-house crew"],
        "phone": "02-9901-1125",
        "image_slug": "jamsil-plaza",
    },
]

EVENT_PRESETS = [
    {"title": "Indie Garden Concert", "description": "성수 도심정원 인디 레이블 쇼케이스", "genre": "Indie", "schedule": "2024-07-05 19:00"},
    {"title": "Resonance Field", "description": "재즈 스트링과 일렉트로닉의 이중편성", "genre": "Jazz", "schedule": "2024-07-06 20:00"},
    {"title": "Studio 42 Residency", "description": "스튜디오 기반 창작팀의 공개 레지던시", "genre": "Indie", "schedule": "2024-07-07 18:30"},
    {"title": "Electronic Midnight Session", "description": "야간 시티팝 × 하우스 크로스오버", "genre": "Electronic", "schedule": "2024-07-08 22:00"},
    {"title": "Citywave Showcase", "description": "서울 어반 신예 셀프 큐레이션", "genre": "Hip-Hop", "schedule": "2024-07-09 19:30"},
    {"title": "Culture Lab Open Stage", "description": "광주 컬처랩 창작 발표 오픈스테이지", "genre": "Indie", "schedule": "2024-07-10 20:00"},
    {"title": "Jazz Horizon Night", "description": "재즈 콜렉티브 × 모던댄스 협업", "genre": "Jazz", "schedule": "2024-07-11 19:00"},
    {"title": "Urban Light Festival", "description": "루프탑 라이트 인스톨과 라이브셋", "genre": "Electronic", "schedule": "2024-07-12 21:00"},
    {"title": "Groove District Live", "description": "펑크/소울 기반 시티 그루브 쇼", "genre": "R&B", "schedule": "2024-07-13 19:30"},
    {"title": "Northern Echo Sessions", "description": "북부 생활권 뮤지션 합동 세션", "genre": "Rock", "schedule": "2024-07-14 18:00"},
    {"title": "Solaris Listening Party", "description": "힙합과 신스웨이브의 믹스셋", "genre": "Electronic", "schedule": "2024-07-15 20:30"},
    {"title": "Concrete Dreams Salon", "description": "콘크리트박스 인스톨 사운드 쇼", "genre": "Indie", "schedule": "2024-07-16 19:00"},
    {"title": "Harborline Stories", "description": "항구도시 포크 아티스트 순회", "genre": "Indie", "schedule": "2024-07-17 19:30"},
    {"title": "Loft Layers Residency", "description": "DJ & 밴드 동시 진행 멀티 셋", "genre": "Electronic", "schedule": "2024-07-18 21:30"},
    {"title": "Sound Warehouse Dialogue", "description": "창고형 무대에서 펼치는 토크콘서트", "genre": "Indie", "schedule": "2024-07-19 19:00"},
    {"title": "Harbor Sunset Rooms", "description": "인천 선셋 비주얼 퍼포먼스", "genre": "Indie", "schedule": "2024-07-20 18:30"},
    {"title": "Busan Pulse Exchange", "description": "부산 로컬과 서울 팀의 교환무대", "genre": "Rock", "schedule": "2024-07-21 20:00"},
    {"title": "Jeju Night Radar", "description": "제주 루프탑에서 즐기는 일렉트로닉 쇼", "genre": "Electronic", "schedule": "2024-07-22 20:30"},
    {"title": "Culture Loop Marathon", "description": "도시 순환형 퍼포먼스 전시", "genre": "Indie", "schedule": "2024-07-23 19:00"},
    {"title": "Indie Cartography Live", "description": "지도 위에 펼치는 로컬 인디 스토리", "genre": "Indie", "schedule": "2024-07-24 19:30"},
    {"title": "Velvet Analog Weekender", "description": "아날로그 신스와 재즈의 주말 잼", "genre": "Jazz", "schedule": "2024-07-25 21:00"},
    {"title": "Seaside Transit Pop-up", "description": "바다 이동형 팝업 퍼포먼스", "genre": "Indie", "schedule": "2024-07-26 18:30"},
]

EVENT_IMAGE_SOURCES = [
    "https://images.unsplash.com/photo-1470229538611-16ba8c7ffbd7?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1497032628192-86f99bcd76bc?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1506157786151-b8491531f063?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?auto=format&fit=crop&w=1600&q=80",
]

PRICE_OPTIONS = [0, 10000, 15000, 20000, 25000, 30000]
TICKET_TYPES = ["입장확인", "좌석", "스탠딩"]


@dataclass(frozen=True)
class ArtistProfile:
    name: str
    category: str
    genres: List[str]
    equipments: List[str]
    phone: str
    history: str


class DummyDataBuilder:
    """Generates curated dummy data with Cloudinary-backed assets."""

    portfolio_url = "https://example.com/artist"

    def __init__(self, *, seed: int = 20240718):
        self.random = random.Random(seed)
        self.user_model = get_user_model()
        self._default_event_image = getattr(settings, "DYVE_DEFAULT_EVENT_IMAGE", "https://res.cloudinary.com/Your_Cloud_Name/image/upload/v1/dyve_dummy/default_event.jpg")
        self._space_profiles: Dict[str, Dict[str, str]] = {profile["name"]: profile for profile in SPACE_PROFILES}
        self._artist_profiles = self._build_artist_profiles()

    # ------------------------------------------------------------------
    # Public entrypoints
    # ------------------------------------------------------------------
    def create_artists(self) -> List[Artist]:
        Artist.objects.filter(name__in=ARTIST_NAMES).delete()
        created: List[Artist] = []
        cloud_name = settings.CLOUDINARY_CLOUD_NAME or "Your_Cloud_Name"
        for profile in self._artist_profiles:
            slug = slugify(profile.name)
            artist = Artist.objects.create(
                name=profile.name,
                category=profile.category,
                genres=", ".join(profile.genres),
                equipments=", ".join(profile.equipments),
                portfolio_url=self.portfolio_url,
                image_url=f"https://res.cloudinary.com/{cloud_name}/image/upload/v1/dyve_dummy/artist_{slug}.jpg",
                history=profile.history,
                phone=profile.phone,
            )
            created.append(artist)
        return created

    def create_spaces(self) -> List[Space]:
        Space.objects.filter(name__in=self._space_profiles.keys()).delete()
        owner = self._get_space_owner()
        created: List[Space] = []
        cloud_name = settings.CLOUDINARY_CLOUD_NAME or "Your_Cloud_Name"
        for profile in SPACE_PROFILES:
            slug = slugify(profile["image_slug"])
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
                image_url=f"https://res.cloudinary.com/{cloud_name}/image/upload/v1/dyve_dummy/space_{slug}.jpg",
                phone=profile["phone"],
            )
            created.append(space)
        return created

    def create_events(self, *, ensure_dependencies: bool = True) -> Dict[str, int]:
        if ensure_dependencies:
            artists = list(Artist.objects.filter(name__in=ARTIST_NAMES))
            spaces = list(Space.objects.filter(name__in=self._space_profiles.keys()))
            artists_created = spaces_created = 0
            if len(artists) < len(ARTIST_NAMES):
                artists = self.create_artists()
                artists_created = len(artists)
            if len(spaces) < len(self._space_profiles):
                spaces = self.create_spaces()
                spaces_created = len(spaces)
        else:
            artists_created = spaces_created = 0
            artists = list(Artist.objects.all())
            spaces = list(Space.objects.all())

        if not artists or not spaces:
            raise ValueError("Artists and spaces must exist before creating events.")

        Event.objects.filter(title__in=[preset["title"] for preset in EVENT_PRESETS]).delete()
        seoul_spaces = [space for space in spaces if self._space_profiles.get(space.name, {}).get("region_group") == "서울"]
        non_seoul_spaces = [space for space in spaces if self._space_profiles.get(space.name, {}).get("region_group") != "서울"]
        seoul_target = round(len(EVENT_PRESETS) * 0.7)
        seoul_count = 0
        ticket_cycle = cycle(TICKET_TYPES)
        price_cycle = cycle(PRICE_OPTIONS)
        image_cycle = cycle(EVENT_IMAGE_SOURCES)
        events_created = 0
        for preset in EVENT_PRESETS:
            use_seoul = seoul_count < seoul_target and bool(seoul_spaces)
            if not seoul_spaces:
                use_seoul = False
            if not non_seoul_spaces:
                use_seoul = True

            if use_seoul:
                space = self.random.choice(seoul_spaces)
                seoul_count += 1
            else:
                space = self.random.choice(non_seoul_spaces)

            event_date, event_time = self._parse_schedule(preset["schedule"])
            ticket_type = next(ticket_cycle)
            price = next(price_cycle)
            image_source = next(image_cycle)
            image_url = self._upload_event_image(image_source)
            event = Event.objects.create(
                title=preset["title"],
                description=preset["description"],
                genre=preset["genre"],
                region=space.region,
                date=event_date,
                time=event_time,
                venue_name=space.name,
                address=space.address,
                price=price,
                is_free=price == 0,
                entry_type=ticket_type,
                image_url=image_url,
                allow_dyve_reservation=True,
                advertise=events_created % 3 == 0,
                space=space,
            )
            artist_sample = self._artist_sample(artists)
            event.artists.set(artist_sample)
            events_created += 1

        return {
            "artists_created": artists_created,
            "spaces_created": spaces_created,
            "events_created": events_created,
        }

    def create_all(self, *, reset: bool = False) -> Dict[str, int]:
        with transaction.atomic():
            if reset:
                self.reset_all()
            artists = self.create_artists()
            spaces = self.create_spaces()
            event_summary = self.create_events(ensure_dependencies=False)
        return {
            "artists_created": len(artists),
            "spaces_created": len(spaces),
            "events_created": event_summary["events_created"],
        }

    def reset_all(self) -> None:
        Event.objects.all().delete()
        Space.objects.all().delete()
        Artist.objects.all().delete()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_space_owner(self):
        owner, _ = self.user_model.objects.get_or_create(
            username="dyve_dummy_host",
            defaults={
                "email": "dummy-host@dyve.local",
                "first_name": "Dummy",
                "last_name": "Host",
            },
        )
        if not owner.has_usable_password():
            owner.set_unusable_password()
            owner.save(update_fields=["password"])
        return owner

    def _artist_sample(self, artists: Sequence[Artist]) -> List[Artist]:
        pool = list(artists)
        if not pool:
            return []
        max_size = min(3, len(pool))
        sample_size = self.random.choice(list(range(1, max_size + 1)))
        return list(self.random.sample(pool, sample_size))

    def _parse_schedule(self, scheduled: str):
        dt = datetime.strptime(scheduled, "%Y-%m-%d %H:%M")
        localized = timezone.make_aware(dt, timezone.get_current_timezone())
        return localized.date(), localized.time().replace(second=0, microsecond=0)

    def _upload_event_image(self, asset_url: str) -> str:
        try:
            response = cloudinary.uploader.upload(asset_url, folder=settings.DYVE_DUMMY_IMAGE_FOLDER)
            return response.get("secure_url", self._default_event_image)
        except Exception:
            return self._default_event_image

    def _build_artist_profiles(self) -> List[ArtistProfile]:
        categories = [
            "재즈 앙상블",
            "밴드",
            "힙합 크루",
            "싱어송라이터",
            "재즈 앙상블",
            "DJ",
            "밴드",
            "국악 프로젝트",
            "프로듀서 팀",
            "보컬 그룹",
        ]
        genre_sets = [
            ["Jazz", "R&B"],
            ["Jazz", "Indie"],
            ["Hip-Hop", "Electronic"],
            ["Indie", "Folk"],
            ["Jazz", "Electronic"],
            ["Electronic", "Hip-Hop"],
            ["Rock", "Indie"],
            ["Indie", "Jazz"],
            ["Electronic", "Indie"],
            ["Indie", "R&B"],
        ]
        equipments = [
            ["mic", "speaker"],
            ["mic", "monitor"],
            ["mixer", "controller"],
            ["mic", "acoustic amp"],
            ["mic", "sax mic"],
            ["dj controller", "sampler"],
            ["guitar amp", "drum kit"],
            ["janggu", "loop station"],
            ["synth", "studio monitor"],
            ["vocal mic", "in-ear monitor"],
        ]
        phones = [
            "010-1024-7735",
            "010-2044-1198",
            "010-3411-8801",
            "010-4502-7754",
            "010-5690-2240",
            "010-6731-9042",
            "010-7012-1134",
            "010-8250-6643",
            "010-9300-8821",
            "010-9977-1204",
        ]
        histories = [
            "서울 재즈파크 주간 프로그램 레지던시 팀",
            "블루노트 인디 포럼에서 연주를 선보인 하우스 밴드",
            "성수 기반 크루와 글로벌 스트리트 브랜드 협업 팀",
            "홍대 라이브러리에서 로컬 투어를 이어가는 싱어송라이터 집단",
            "남산 재즈 나잇에서 모던 재즈와 힙합을 혼합한 프로젝트",
            "일렉트로닉 신과 디지털 아트 전시를 잇는 프로듀서 팀",
            "어반 아트마켓과 연계한 오리지널 소울 퍼포먼스",
            "국악기를 활용한 레지던시 협업 프로젝트",
            "스튜디오 기반 사운드 아티스트 협업 그룹",
            "독립 레이블과 커뮤니티가 운영하는 싱어즈 클럽",
        ]
        profiles: List[ArtistProfile] = []
        for idx, name in enumerate(ARTIST_NAMES):
            profiles.append(
                ArtistProfile(
                    name=name,
                    category=categories[idx],
                    genres=genre_sets[idx],
                    equipments=equipments[idx],
                    phone=phones[idx],
                    history=f"{name} — {histories[idx]}",
                )
            )
        return profiles


def build_dummy_data(reset: bool = False) -> Dict[str, int]:
    return DummyDataBuilder().create_all(reset=reset)


def build_artists() -> Dict[str, int]:
    created = DummyDataBuilder().create_artists()
    return {"artists_created": len(created), "spaces_created": 0, "events_created": 0}


def build_spaces() -> Dict[str, int]:
    created = DummyDataBuilder().create_spaces()
    return {"artists_created": 0, "spaces_created": len(created), "events_created": 0}


def build_events() -> Dict[str, int]:
    summary = DummyDataBuilder().create_events()
    return summary
