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
from .views.dev_seed import SeedAllView, SeedOneView

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
    path('dev/seed-all/', SeedAllView.as_view(), name='dev-seed-all'),
    path('dev/seed-one/', SeedOneView.as_view(), name='dev-seed-one'),
]
