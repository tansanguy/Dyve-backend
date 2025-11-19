"""Development helper endpoints for seeding large dummy datasets."""

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.dummy_generator import DummyDataGenerator
from .serializers import DummyCreateResponseSerializer


class BaseDummyCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_generator(self) -> DummyDataGenerator:
        return DummyDataGenerator()

    def build_response(self, *, events: int = 0, artists: int = 0, spaces: int = 0):
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
        description='장르/지역/카테고리 JSON에서 로드한 값으로 공연 10개를 생성합니다. 필요 시 공간/아티스트를 자동 보충합니다.',
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
        description='장르/장비 JSON 조합으로 랜덤 아티스트 5개를 생성합니다.',
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
        description='JSON 카테고리/지역/장비 값으로 공간(Space) 5개를 생성합니다.',
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
        description='아티스트/공간/공연 세트를 JSON 기준 데이터로 각각 5/5/10개 생성합니다.',
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
