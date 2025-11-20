import uuid

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from ..constants import GENRES, REGIONS, SPACE_CATEGORIES
from ..models import Artist, Event, NotificationSetting, Proposal, Reservation, Settlement, Space
from ..serializers import (
    ArtistSerializer,
    EventSerializer,
    NotificationSettingSerializer,
    ProposalSerializer,
    ReservationSerializer,
    SettlementSerializer,
    SpaceSerializer,
    UserSerializer,
)

User = get_user_model()

META_RESPONSE_SERIALIZER = inline_serializer(
    name='MetaAggregateResponse',
    fields={
        'regions': serializers.ListField(child=serializers.CharField()),
        'genres': serializers.ListField(child=serializers.CharField()),
        'space_categories': serializers.ListField(child=serializers.CharField()),
    },
)
REGION_LIST_SERIALIZER = inline_serializer(
    name='RegionListResponse',
    fields={'regions': serializers.ListField(child=serializers.CharField())},
)
GENRE_LIST_SERIALIZER = inline_serializer(
    name='GenreListResponse',
    fields={'genres': serializers.ListField(child=serializers.CharField())},
)
SPACE_CATEGORY_LIST_SERIALIZER = inline_serializer(
    name='SpaceCategoryListResponse',
    fields={'space_categories': serializers.ListField(child=serializers.CharField())},
)
PROFILE_RESPONSE_SERIALIZER = inline_serializer(
    name='MyPageProfileResponse',
    fields={
        'user': UserSerializer(),
        'artist_id': serializers.IntegerField(allow_null=True),
        'space_ids': serializers.ListField(child=serializers.IntegerField(), allow_empty=True),
    },
)
HOME_AROUND_RESPONSE_SERIALIZER = inline_serializer(
    name='HomeAroundYouResponse',
    fields={
        'region': serializers.CharField(),
        'events': serializers.ListSerializer(child=EventSerializer()),
    },
)

META_REGIONS_EXAMPLE = OpenApiExample(
    'RegionsExample',
    summary='지원 지역 예시',
    value={'regions': REGIONS},
    response_only=True,
)
META_GENRES_EXAMPLE = OpenApiExample(
    'GenresExample',
    summary='지원 장르 예시',
    value={'genres': GENRES},
    response_only=True,
)
META_SPACE_CATEGORIES_EXAMPLE = OpenApiExample(
    'SpaceCategoriesExample',
    summary='공간 카테고리 예시',
    value={'space_categories': SPACE_CATEGORIES},
    response_only=True,
)
META_AGGREGATE_EXAMPLE = OpenApiExample(
    'MetaAggregateExample',
    value={
        'regions': REGIONS,
        'genres': GENRES,
        'space_categories': SPACE_CATEGORIES,
    },
    response_only=True,
)
EVENT_LIST_RESPONSE_EXAMPLE = OpenApiExample(
    'EventListExample',
    summary='공연 리스트 응답 예시',
    value=[
        {
            'id': 1,
            'title': 'Hongdae Indie Night',
            'description': '신예 인디 밴드 쇼케이스',
            'genre': 'Indie',
            'region': '서울',
            'date': '2024-03-15',
            'time': '19:00:00',
            'venue_name': 'Dyve Live Club',
            'address': '서울시 마포구 어딘가 123',
            'price': 20000,
            'is_free': False,
            'entry_type': '스탠딩',
            'image_url': 'https://images.dyve.local/event1.jpg',
            'allow_dyve_reservation': True,
            'advertise': True,
            'space': 1,
            'artists': [1],
            'created_at': '2024-02-12T00:00:00Z',
            'updated_at': '2024-02-12T00:00:00Z',
        }
    ],
    response_only=True,
)
EVENT_CREATE_REQUEST_EXAMPLE = OpenApiExample(
    'EventCreateRequest',
    summary='공연 생성 요청 예시',
    value={
        'title': 'City Rooftop Session',
        'description': '일렉트로닉 루프탑 공연',
        'genre': 'Electronic',
        'region': '인천',
        'date': '2024-04-20',
        'time': '19:30:00',
        'venue_name': 'Incheon Rooftop',
        'address': '인천 연수구 바닷가 45',
        'price': 0,
        'is_free': True,
        'entry_type': '입장확인',
        'image_url': 'https://images.dyve.local/event-new.jpg',
        'allow_dyve_reservation': True,
        'advertise': False,
        'space': 2,
        'artists': [2],
    },
    request_only=True,
)
RESERVATION_CREATE_REQUEST_EXAMPLE = OpenApiExample(
    'ReservationCreateRequest',
    summary='예매 생성 요청 예시',
    value={'event': 1, 'quantity': 2, 'seat': 'Standing A-1'},
    request_only=True,
)
RESERVATION_CREATE_RESPONSE_EXAMPLE = OpenApiExample(
    'ReservationCreateResponse',
    summary='예매 생성 응답 예시',
    value={
        'id': 10,
        'user': 1,
        'event': 1,
        'quantity': 2,
        'seat': 'Standing A-1',
        'entry_type': '스탠딩',
        'price': 40000,
        'qr_code': 'QR-1AB23CD4',
        'reservation_code': 'RSVABC123456',
        'created_at': '2024-02-20T12:00:00Z',
        'updated_at': '2024-02-20T12:00:00Z',
    },
    response_only=True,
)
HOME_BANNER_RESPONSE_EXAMPLE = OpenApiExample(
    'HomeBannerResponse',
    summary='홈 배너 응답 예시',
    value=[
        {
            'id': 1,
            'title': 'Hongdae Indie Night',
            'description': '인디 밴드 쇼케이스',
            'genre': 'Indie',
            'region': '서울',
            'date': '2024-03-15',
            'time': '19:00:00',
            'venue_name': 'Dyve Live Club',
            'address': '서울시 마포구',
            'price': 20000,
            'is_free': False,
            'entry_type': '스탠딩',
            'image_url': 'https://images.dyve.local/event1.jpg',
            'allow_dyve_reservation': True,
            'advertise': True,
            'space': 1,
            'artists': [1],
            'created_at': '2024-02-12T00:00:00Z',
            'updated_at': '2024-02-12T00:00:00Z',
        }
    ],
    response_only=True,
)

EVENT_FILTER_PARAMETERS = [
    OpenApiParameter(
        name='genre',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description='장르 상수 중 하나로 필터링합니다.',
        examples=[OpenApiExample('IndieGenre', value='Indie')],
    ),
    OpenApiParameter(
        name='region',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description='지역 상수 중 하나로 필터링합니다.',
        examples=[OpenApiExample('SeoulRegion', value='서울')],
    ),
    OpenApiParameter(
        name='free',
        type=OpenApiTypes.BOOL,
        location=OpenApiParameter.QUERY,
        description='"true"로 설정하면 무료 공연만 조회합니다.',
    ),
    OpenApiParameter(
        name='dyve_only',
        type=OpenApiTypes.BOOL,
        location=OpenApiParameter.QUERY,
        description='"true"로 설정하면 DYVE 예약 허용 공연만 조회합니다.',
    ),
    OpenApiParameter(
        name='ordering',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description='정렬 기준입니다. "dday"는 날짜,시간 오름차순을 의미합니다.',
        examples=[OpenApiExample('DDayOrdering', value='dday')],
    ),
]

HOME_AROUND_PARAMETERS = [
    OpenApiParameter(
        name='lat',
        type=OpenApiTypes.DOUBLE,
        location=OpenApiParameter.QUERY,
        description='사용자 위도. 현재는 region 추정에만 사용되는 더미 값입니다.',
    ),
    OpenApiParameter(
        name='lng',
        type=OpenApiTypes.DOUBLE,
        location=OpenApiParameter.QUERY,
        description='사용자 경도. 현재는 region 추정에만 사용되는 더미 값입니다.',
    ),
    OpenApiParameter(
        name='region',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description='명시적으로 지역을 지정하고 싶을 때 사용합니다.',
    ),
]


@method_decorator(csrf_exempt, name='dispatch')
@extend_schema_view(
    list=extend_schema(
        tags=['Meta'],
        summary='DYVE 메타 데이터 전체 조회',
        description='프론트/백엔드에서 공유하는 지역, 장르, 공간 카테고리 상수를 한 번에 반환합니다.',
        responses=META_RESPONSE_SERIALIZER,
        examples=[META_AGGREGATE_EXAMPLE],
    )
)
class MetaViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        return Response(
            {
                'regions': REGIONS,
                'genres': GENRES,
                'space_categories': SPACE_CATEGORIES,
            }
        )

    @extend_schema(
        methods=['GET'],
        tags=['Meta'],
        summary='지역 상수 목록',
        description='DYVE 서비스에서 지원하는 지역 코드 목록을 반환합니다.',
        responses=REGION_LIST_SERIALIZER,
        examples=[META_REGIONS_EXAMPLE],
    )
    @action(detail=False, methods=['get'], url_path='regions')
    def regions(self, request):
        return Response({'regions': REGIONS})

    @extend_schema(
        methods=['GET'],
        tags=['Meta'],
        summary='장르 상수 목록',
        description='공연 등록 시 사용할 수 있는 장르 목록을 반환합니다.',
        responses=GENRE_LIST_SERIALIZER,
        examples=[META_GENRES_EXAMPLE],
    )
    @action(detail=False, methods=['get'], url_path='genres')
    def genres(self, request):
        return Response({'genres': GENRES})

    @extend_schema(
        methods=['GET'],
        tags=['Meta'],
        summary='공간 카테고리 상수 목록',
        description='공간 등록 시 사용할 수 있는 카테고리 목록을 반환합니다.',
        responses=SPACE_CATEGORY_LIST_SERIALIZER,
        examples=[META_SPACE_CATEGORIES_EXAMPLE],
    )
    @action(detail=False, methods=['get'], url_path='space-categories')
    def space_categories(self, request):
        return Response({'space_categories': SPACE_CATEGORIES})


@extend_schema_view(
    list=extend_schema(
        tags=['MyPage'],
        summary='내 계정 요약 조회',
        description='세션으로 인증된 사용자의 기본 계정 정보, 연결된 아티스트/공간 프로필 ID를 반환합니다.',
        responses=PROFILE_RESPONSE_SERIALIZER,
    )
)
class MyPageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        artist = getattr(request.user, 'artist_profile', None)
        space_ids = list(request.user.spaces.values_list('id', flat=True))
        data = {
            'user': UserSerializer(request.user).data,
            'artist_id': artist.id if artist else None,
            'space_ids': space_ids,
        }
        return Response(data)

    @extend_schema(
        methods=['GET'],
        tags=['MyPage'],
        summary='내 프로필 정보 조회',
        description='로그인한 사용자의 User 기본 정보를 반환합니다.',
        responses=UserSerializer,
    )
    @extend_schema(
        methods=['PATCH'],
        tags=['MyPage'],
        summary='내 프로필 정보 수정',
        description='이메일, 이름 등의 기본 계정 정보를 수정합니다.',
        request=UserSerializer,
        responses=UserSerializer,
    )
    @action(detail=False, methods=['get', 'patch'], url_path='profile')
    def profile(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        methods=['GET'],
        tags=['MyPage'],
        summary='알림 설정 조회',
        description='현재 사용자에 대한 NotificationSetting 값을 반환합니다.',
        responses=NotificationSettingSerializer,
    )
    @extend_schema(
        methods=['PATCH'],
        tags=['MyPage'],
        summary='알림 설정 수정',
        description='performance_update 등 알림 관련 설정 값을 수정합니다.',
        request=NotificationSettingSerializer,
        responses=NotificationSettingSerializer,
    )
    @action(detail=False, methods=['get', 'patch'], url_path='notifications')
    def notifications(self, request):
        setting, _ = NotificationSetting.objects.get_or_create(user=request.user)
        if request.method == 'PATCH':
            serializer = NotificationSettingSerializer(setting, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = NotificationSettingSerializer(setting)
        return Response(serializer.data)

    @extend_schema(
        methods=['GET'],
        tags=['MyPage'],
        summary='내 예매 목록 조회',
        description='인증된 사용자의 Reservation 목록을 반환합니다.',
        responses=ReservationSerializer(many=True),
    )
    @action(detail=False, methods=['get'], url_path='reservations')
    def reservations(self, request):
        queryset = Reservation.objects.filter(user=request.user).select_related('event')
        serializer = ReservationSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        methods=['GET'],
        tags=['MyPage'],
        summary='내 공간 정산 내역 조회',
        description='내가 소유한 공간에 대한 Settlement 목록을 반환합니다.',
        responses=SettlementSerializer(many=True),
    )
    @action(detail=False, methods=['get'], url_path='settlements')
    def settlements(self, request):
        queryset = Settlement.objects.filter(space__owner=request.user).select_related('event', 'space')
        serializer = SettlementSerializer(queryset, many=True)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
@extend_schema_view(
    list=extend_schema(
        tags=['Artists'],
        summary='아티스트 목록 조회',
        description='공개된 아티스트 프로필 목록을 반환합니다.',
        responses=ArtistSerializer(many=True),
    ),
    retrieve=extend_schema(
        tags=['Artists'],
        summary='아티스트 상세 조회',
        description='선택한 아티스트 프로필 정보를 조회합니다.',
        responses=ArtistSerializer,
    ),
)
class ArtistViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Artist.objects.select_related('user').all()
    serializer_class = ArtistSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        methods=['POST'],
        tags=['Artists'],
        summary='내 아티스트 프로필 생성',
        description='로그인 사용자가 자신의 Artist 프로필을 신규 생성합니다. genres 필드는 쉼표로 장르를 구분합니다.',
        request=ArtistSerializer,
        responses=ArtistSerializer,
    )
    @extend_schema(
        methods=['PUT'],
        tags=['Artists'],
        summary='내 아티스트 프로필 수정',
        description='이미 존재하는 내 Artist 프로필을 전체 수정합니다.',
        request=ArtistSerializer,
        responses=ArtistSerializer,
    )
    @action(detail=False, methods=['post', 'put'], permission_classes=[permissions.IsAuthenticated], url_path='profile')
    def profile(self, request):
        instance = getattr(request.user, 'artist_profile', None)
        serializer = self.get_serializer(instance, data=request.data, partial=bool(instance))
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        status_code = status.HTTP_200_OK if instance else status.HTTP_201_CREATED
        return Response(serializer.data, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
@extend_schema_view(
    list=extend_schema(
        tags=['Spaces'],
        summary='공간 목록 조회',
        description='공개된 공간 프로필 목록을 조회합니다.',
        responses=SpaceSerializer(many=True),
    ),
    retrieve=extend_schema(
        tags=['Spaces'],
        summary='공간 상세 조회',
        description='지정된 공간 정보를 반환합니다.',
        responses=SpaceSerializer,
    ),
)
class SpaceViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Space.objects.select_related('owner').all()
    serializer_class = SpaceSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        methods=['POST'],
        tags=['Spaces'],
        summary='내 공간 프로필 생성',
        description='로그인 사용자가 자신의 공간 프로필을 생성합니다. category/region 필드는 상수 리스트 값만 허용됩니다.',
        request=SpaceSerializer,
        responses=SpaceSerializer,
    )
    @extend_schema(
        methods=['PUT'],
        tags=['Spaces'],
        summary='내 공간 프로필 수정',
        description='기존 공간 프로필을 전체 수정합니다.',
        request=SpaceSerializer,
        responses=SpaceSerializer,
    )
    @action(detail=False, methods=['post', 'put'], permission_classes=[permissions.IsAuthenticated], url_path='profile')
    def profile(self, request):
        instance = request.user.spaces.first()
        serializer = self.get_serializer(instance, data=request.data, partial=bool(instance))
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        status_code = status.HTTP_200_OK if instance else status.HTTP_201_CREATED
        return Response(serializer.data, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
@extend_schema_view(
    list=extend_schema(
        tags=['Events'],
        summary='공연 목록 조회',
        description='필터(장르, 지역, 무료 여부 등)를 적용해 공연 목록을 조회합니다.',
        parameters=EVENT_FILTER_PARAMETERS,
        responses=EventSerializer(many=True),
        examples=[EVENT_LIST_RESPONSE_EXAMPLE],
    ),
    retrieve=extend_schema(
        tags=['Events'],
        summary='공연 상세 조회',
        description='특정 공연의 상세 정보를 반환합니다.',
        responses=EventSerializer,
    ),
    create=extend_schema(
        tags=['Events'],
        summary='새 공연 등록',
        description='로그인된 공간 소유자만 호출 가능합니다. space 필드는 자신의 공간 ID여야 합니다.',
        request=EventSerializer,
        responses=EventSerializer,
        examples=[EVENT_CREATE_REQUEST_EXAMPLE],
    ),
)
class EventViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Event.objects.select_related('space').prefetch_related('artists').all()

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        genre = self.request.query_params.get('genre')
        if genre:
            queryset = queryset.filter(genre=genre)
        region = self.request.query_params.get('region')
        if region:
            queryset = queryset.filter(region=region)
        free = self.request.query_params.get('free')
        if free in {'true', '1'}:
            queryset = queryset.filter(is_free=True)
        dyve_only = self.request.query_params.get('dyve_only')
        if dyve_only in {'true', '1'}:
            queryset = queryset.filter(allow_dyve_reservation=True)
        ordering = self.request.query_params.get('ordering')
        if ordering == 'dday':
            queryset = queryset.order_by('date', 'time')
        return queryset

    def perform_create(self, serializer):
        space = serializer.validated_data.get('space')
        if space and space.owner != self.request.user:
            raise PermissionDenied('해당 공간의 소유자만 공연을 등록할 수 있습니다.')
        serializer.save()


@method_decorator(csrf_exempt, name='dispatch')
@extend_schema_view(
    create=extend_schema(
        tags=['Reservations'],
        summary='새 예매 생성',
        description='선택한 이벤트에 대해 quantity/seat 정보를 제출하면 entry_type·price·reservation_code가 자동 설정됩니다.',
        request=ReservationSerializer,
        responses=ReservationSerializer,
        examples=[
            RESERVATION_CREATE_REQUEST_EXAMPLE,
            RESERVATION_CREATE_RESPONSE_EXAMPLE,
        ],
    )
)
class ReservationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.select_related('event', 'user')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.validated_data['event']
        quantity = serializer.validated_data.get('quantity', 1)
        price = 0 if event.is_free or event.price == 0 else event.price * quantity
        entry_type = event.entry_type
        reservation_code = uuid.uuid4().hex[:12]
        qr_code = f"QR-{uuid.uuid4().hex[:8]}"
        serializer.save(
            user=request.user,
            entry_type=entry_type,
            price=price,
            reservation_code=reservation_code,
            qr_code=qr_code,
        )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema_view(
    list=extend_schema(
        tags=['Proposals'],
        summary='내가 보낸 제안서 목록',
        description='현재 로그인한 사용자가 보낸 Proposal 목록을 반환합니다.',
        responses=ProposalSerializer(many=True),
    ),
    create=extend_schema(
        tags=['Proposals'],
        summary='새 제안서 작성',
        description='sender는 자동으로 현재 사용자로 설정됩니다. receiver_artist 또는 receiver_space 중 하나 이상이 필요합니다.',
        request=ProposalSerializer,
        responses=ProposalSerializer,
    ),
)
class ProposalViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Proposal.objects.filter(sender=self.request.user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @extend_schema(
        methods=['GET'],
        tags=['Proposals'],
        summary='내가 받은 제안서 목록',
        description='나의 Artist/Space 프로필로 전달된 Proposal 목록을 반환합니다.',
        responses=ProposalSerializer(many=True),
    )
    @action(detail=False, methods=['get'], url_path='received')
    def received(self, request):
        queryset = Proposal.objects.filter(
            Q(receiver_artist__user=request.user)
            | Q(receiver_space__owner=request.user)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class HomeViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        methods=['GET'],
        tags=['Home'],
        summary='홈 배너 공연',
        description='광고 설정(advertise=True)이 활성화된 공연을 최신순으로 반환합니다.',
        responses=EventSerializer(many=True),
        examples=[HOME_BANNER_RESPONSE_EXAMPLE],
    )
    @action(detail=False, methods=['get'], url_path='banner')
    def banner(self, request):
        queryset = Event.objects.filter(advertise=True).order_by('-created_at')[:5]
        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        methods=['GET'],
        tags=['Home'],
        summary='다가오는 공연',
        description='오늘 기준으로 다가오는 공연을 날짜/시간 오름차순으로 반환합니다.',
        responses=EventSerializer(many=True),
    )
    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming(self, request):
        today = timezone.localdate()
        queryset = (
            Event.objects.filter(date__gte=today)
            .order_by('date', 'time')
            [:5]
        )
        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        methods=['GET'],
        tags=['Home'],
        summary='내 주변 공연',
        description='lat/lng를 기반으로 region을 추정하는 더미 로직으로, 현재는 region 파라미터 기준으로 가까운 공연만 반환합니다.',
        parameters=HOME_AROUND_PARAMETERS,
        responses=HOME_AROUND_RESPONSE_SERIALIZER,
    )
    @action(detail=False, methods=['get'], url_path='around-you')
    def around_you(self, request):
        region = request.query_params.get('region') or '서울'
        queryset = Event.objects.filter(region=region).order_by('date', 'time')[:5]
        serializer = EventSerializer(queryset, many=True)
        return Response({'region': region, 'events': serializer.data})
