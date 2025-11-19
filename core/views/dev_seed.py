from __future__ import annotations

from django.conf import settings
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.dummy_data import build_artists, build_dummy_data, build_events, build_spaces
from ..serializers import DummyAllRequestSerializer, DummyCreationSummarySerializer

SHARED_DESCRIPTION = (
    "- 아티스트·공간·공연 데이터를 고정 큐레이션 세트로 생성합니다.\n"
    "- 공연 지역 분포: 서울 70% / 비서울 30%.\n"
    "- 티켓 타입(enum): 입장확인 · 좌석 · 스탠딩 을 순환 분배합니다.\n"
    "- 이벤트 이미지는 Cloudinary 폴더 'dyve_dummy' 로 업로드하며 secure_url 을 저장합니다. "
    f"업로드 실패 시 {getattr(settings, 'DYVE_DEFAULT_EVENT_IMAGE', 'https://res.cloudinary.com/Your_Cloud_Name/image/upload/v1/dyve_dummy/default_event.jpg')} 를 사용합니다."
)

DUMMY_RESPONSE_EXAMPLE = OpenApiExample(
    "DummyCreationSummary",
    summary="생성 결과 예시",
    value={"artists_created": 10, "spaces_created": 10, "events_created": 22},
    response_only=True,
)

DUMMY_ALL_REQUEST_EXAMPLE = OpenApiExample(
    "DummyAllResetRequest",
    summary="전체 리셋 생성 요청",
    value={"reset": True},
    request_only=True,
)


def _response(summary: dict[str, int]) -> Response:
    return Response(summary, status=status.HTTP_201_CREATED)


class CreateDummyArtistsView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Dev Dummy"],
        summary="아티스트 큐레이션 생성",
        description=(
            SHARED_DESCRIPTION
            + "\n- 요청 시 기존 동일 명칭 아티스트 10팀을 덮어쓰고, 포트폴리오 링크와 한국형 연락처를 고정 세트로 제공합니다."
        ),
        responses={201: DummyCreationSummarySerializer},
        examples=[DUMMY_RESPONSE_EXAMPLE],
    )
    def post(self, request):
        return _response(build_artists())


class CreateDummySpacesView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Dev Dummy"],
        summary="공간 큐레이션 생성",
        description=(
            SHARED_DESCRIPTION
            + "\n- 서울/지방 소속이 고정된 10개 공간을 생성하며 지역별 설명, 수용인원(50·80·120·200)과 02 국번 연락처를 제공합니다."
        ),
        responses={201: DummyCreationSummarySerializer},
        examples=[DUMMY_RESPONSE_EXAMPLE],
    )
    def post(self, request):
        return _response(build_spaces())


class CreateDummyEventsView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Dev Dummy"],
        summary="공연 큐레이션 생성",
        description=(
            SHARED_DESCRIPTION
            + "\n- 20~25개의 공연을 생성하며 Cloudinary 업로드로 확보한 이미지 URL, 티켓 타입/가격 분배 규칙, "
            "고정 제목 리스트(Indie Garden Concert 등)를 문서화합니다."
        ),
        responses={201: DummyCreationSummarySerializer},
        examples=[DUMMY_RESPONSE_EXAMPLE],
    )
    def post(self, request):
        return _response(build_events())


class CreateDummyAllView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Dev Dummy"],
        summary="전체 큐레이션 생성",
        description=(
            SHARED_DESCRIPTION
            + "\n- reset=true 일 경우 기존 Artist/Space/Event 테이블을 비우고 단일 트랜잭션으로 아티스트→공간→공연 순으로 생성합니다."
        ),
        request=DummyAllRequestSerializer,
        responses={201: DummyCreationSummarySerializer},
        examples=[DUMMY_ALL_REQUEST_EXAMPLE, DUMMY_RESPONSE_EXAMPLE],
    )
    def post(self, request):
        serializer = DummyAllRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return _response(build_dummy_data(reset=serializer.validated_data.get("reset", False)))
