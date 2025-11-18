from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ArtistViewSet,
    CreateDummyArtistView,
    CreateDummyUserView,
    CreateDummyVenueView,
    EventViewSet,
    HomeViewSet,
    MetaViewSet,
    MyPageViewSet,
    ProposalViewSet,
    ReservationViewSet,
    SpaceViewSet,
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
    path('dummy/create-user/', CreateDummyUserView.as_view(), name='dummy-create-user'),
    path('dummy/create-artist/', CreateDummyArtistView.as_view(), name='dummy-create-artist'),
    path('dummy/create-venue/', CreateDummyVenueView.as_view(), name='dummy-create-venue'),
]
