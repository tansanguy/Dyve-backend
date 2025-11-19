"""Dev-only endpoints that seed realistic demo data."""

from __future__ import annotations

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.dummy_seed import seed_all as run_seed_all
from utils.dummy_seed import seed_artists as run_seed_artists
from utils.dummy_seed import seed_events as run_seed_events
from utils.dummy_seed import seed_spaces as run_seed_spaces
from ..serializers import DevSeedResponseSerializer


class SeedAllRequestSerializer(serializers.Serializer):
    reset = serializers.BooleanField(default=False, help_text='기존 Artist/Space/Event 데이터를 모두 삭제합니다.')

SEED_RESPONSE_EXAMPLE = OpenApiExample(
    'SeedResponse',
    summary='더미 데이터 생성 결과 예시',
    value={'artists_created': 10, 'spaces_created': 10, 'events_created': 20, 'dyve_available': 15},
    response_only=True,
)

SEED_ALL_REQUEST_EXAMPLE = OpenApiExample(
    'SeedAllResetRequest',
    summary='Seed-All 요청 예시',
    value={'reset': True},
    request_only=True,
)


class SeedArtistsView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Dev Seed'],
        summary='아티스트 더미 생성',
        description='실제 팀명을 기반으로 한 아티스트 데이터 10개 이상을 생성합니다.',
        request=None,
        responses={201: DevSeedResponseSerializer},
        examples=[SEED_RESPONSE_EXAMPLE],
    )
    def post(self, request):
        summary = run_seed_artists()
        return Response(summary, status=status.HTTP_201_CREATED)


class SeedSpacesView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Dev Seed'],
        summary='공간 더미 생성',
        description='홍대/성수 등 실제 느낌의 명칭과 카테고리로 공간 데이터를 10개 이상 생성합니다.',
        request=None,
        responses={201: DevSeedResponseSerializer},
        examples=[SEED_RESPONSE_EXAMPLE],
    )
    def post(self, request):
        summary = run_seed_spaces()
        return Response(summary, status=status.HTTP_201_CREATED)


class SeedEventsView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Dev Seed'],
        summary='공연 더미 생성',
        description='서울 비중 70% 이상, entry_type(general/seat/standing) 고르게 분배된 공연 데이터를 20개 이상 생성합니다.',
        request=None,
        responses={201: DevSeedResponseSerializer},
        examples=[SEED_RESPONSE_EXAMPLE],
    )
    def post(self, request):
        summary = run_seed_events()
        return Response(summary, status=status.HTTP_201_CREATED)


class SeedAllView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Dev Seed'],
        summary='전체 더미 데이터 생성',
        description='아티스트/공간/공연을 순서대로 생성하고 FK 관계를 연결합니다. reset=True면 기존 데이터를 모두 삭제합니다.',
        request=SeedAllRequestSerializer,
        responses={201: DevSeedResponseSerializer},
        examples=[SEED_ALL_REQUEST_EXAMPLE, SEED_RESPONSE_EXAMPLE],
    )
    def post(self, request):
        serializer = SeedAllRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        summary = run_seed_all(reset=serializer.validated_data.get('reset', False))
        return Response(summary, status=status.HTTP_201_CREATED)
