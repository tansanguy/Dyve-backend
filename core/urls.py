from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ArtistViewSet,
    EventViewSet,
    HomeViewSet,
    MetaViewSet,
    MyPageViewSet,
    ProposalViewSet,
    ReservationViewSet,
    SpaceViewSet,
)
from .views.dev_seed import (
    CreateDummyAllView,
    CreateDummyArtistsView,
    CreateDummyEventsView,
    CreateDummySpacesView,
)

router = DefaultRouter()
router.register('meta', MetaViewSet, basename='meta')
router.register('mypage', MyPageViewSet, basename='mypage')
router.register('artists', ArtistViewSet, basename='artist')
router.register('spaces', SpaceViewSet, basename='space')
router.register('events', EventViewSet, basename='event')
router.register('reservations', ReservationViewSet, basename='reservation')
router.register('proposals', ProposalViewSet, basename='proposal')
router.register('home', HomeViewSet, basename='home')

urlpatterns = router.urls + [
    path('dev/create-dummy-artists/', CreateDummyArtistsView.as_view(), name='dev-create-dummy-artists'),
    path('dev/create-dummy-spaces/', CreateDummySpacesView.as_view(), name='dev-create-dummy-spaces'),
    path('dev/create-dummy-events/', CreateDummyEventsView.as_view(), name='dev-create-dummy-events'),
    path('dev/create-dummy-all/', CreateDummyAllView.as_view(), name='dev-create-dummy-all'),
]
