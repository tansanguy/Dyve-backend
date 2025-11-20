from __future__ import annotations

from django.conf import settings
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from utils.dummy_data import create_one, seed_all
from ..serializers import SeedOneResponseSerializer, SeedResultSerializer

SEED_RESPONSE_EXAMPLE = OpenApiExample(
    "SeedAllResponse",
    summary="더미 데이터 생성 결과",
    description="10명의 아티스트, 10개의 공간, 24개의 이벤트를 생성한 후 반환되는 예시입니다.",
    value={"artists_created": 10, "spaces_created": 10, "events_created": 24},
    response_only=True,
)

SEED_DESCRIPTION = (
    "- 고정된 10개 아티스트 · 10개 공간 · 20~25개 이벤트 세트를 한 번에 생성합니다.\n"
    "- 모든 이미지(artist/space/poster)는 `dummy_images/` 하위 폴더에서 순서대로 읽고 Cloudinary 폴더 `dyve_dummy` 로 업로드한 secure_url 을 저장합니다.\n"
    "- 각 폴더에 있는 개별 이미지는 1회만 사용되며 소진되면 default.jpg 로 자동 대체됩니다.\n"
    "- 이벤트 지역은 서울 70% / 비서울 30% 비율을 유지하며, 티켓 타입은 ['입장확인','좌석','스탠딩'] 을 균등 분배합니다.\n"
    "- 가격은 [0, 10000, 15000, 20000, 25000, 30000] 중 순환 선택하고, 시간 포맷은 YYYY-MM-DD HH:MM 규칙을 따릅니다.\n"
    "- 아티스트/공간명은 제공된 큐레이션 리스트(Luna Quartet, 홍대 Moonlight Stage 등)만을 사용합니다."
)

SEED_ONE_EXAMPLE = OpenApiExample(
    "SeedOneResponse",
    summary="단일 더미 데이터 세트",
    description="아티스트/공간/이벤트 1개씩 생성한 예시",
    value={
        "artist": {
            "id": 101,
            "name": "Canopy Ensemble",
            "description": "서울 성수동에서 모듈러 신스를 기반으로 라이브를 진행하는 팀",
            "category": "재즈 앙상블",
            "profile_image_url": "https://res.cloudinary.com/demo/image/upload/v1/dyve_dummy/artist_profiles/sample.jpg",
            "portfolio_link": "https://example.com/artists/canopy-ensemble",
            "required_equipment": ["mic", "monitor speaker"],
        },
        "space": {
            "id": 55,
            "name": "성수 Lofi Lab",
            "description": "따뜻한 무드의 로컬 아트 공연장입니다.",
            "region": "서울",
            "address": "서울 문화로 42",
            "image_url": "https://res.cloudinary.com/demo/image/upload/v1/dyve_dummy/space_profiles/sample.jpg",
            "capacity": 80,
            "mood": "따뜻한",
            "phone_number": "02-1200-8899",
        },
        "event": {
            "id": 88,
            "artist_id": 101,
            "space_id": 55,
            "title": "Parallel Garden Showcase",
            "description": "아트워크 전시와 함께 진행되는 몰입형 라이브",
            "poster_image_url": "https://res.cloudinary.com/demo/image/upload/v1/dyve_dummy/posters/sample.jpg",
            "date_time": "2024-09-20 19:30",
            "genre": "Indie",
            "running_time": 75,
            "price": 20000,
            "entry_type": "입장확인",
        },
    },
    response_only=True,
)


@method_decorator(csrf_exempt, name="dispatch")
class SeedAllView(GenericAPIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Dev Seed"],
        summary="큐레이션 더미 데이터 일괄 생성",
        description=SEED_DESCRIPTION,
        responses={201: SeedResultSerializer},
        examples=[SEED_RESPONSE_EXAMPLE],
    )
    def post(self, request):
        with transaction.atomic():
            summary = seed_all(clear_existing=True)
        return Response(summary, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class SeedOneView(GenericAPIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Dev Seed"],
        summary="단일 아티스트/공간/이벤트 생성",
        description=(
            "- utils/assets/* 폴더의 이미지를 무작위로 선택해 Cloudinary(dyve_dummy/artist_profiles|space_profiles|posters)에 업로드합니다.\n"
            "- Artist 1명, Space 1개, Event 1개를 순서대로 만들고 FK를 연결합니다.\n"
            "- PRODUCTION 환경에서 요청 시 400 으로 비활성화합니다."
        ),
        responses={201: SeedOneResponseSerializer},
        examples=[SEED_ONE_EXAMPLE],
    )
    def post(self, request):
        if settings.ENVIRONMENT == 'production':
            return Response({'error': 'seed disabled in production'}, status=status.HTTP_400_BAD_REQUEST)
        summary = create_one()
        return Response(summary, status=status.HTTP_201_CREATED)
