from __future__ import annotations

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from utils.dummy_data import seed_all
from ..serializers import SeedResultSerializer

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


class SeedAllView(APIView):
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
