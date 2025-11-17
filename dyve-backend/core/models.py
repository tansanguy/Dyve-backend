from django.conf import settings
from django.db import models

from .constants import GENRES, REGIONS, SPACE_CATEGORIES


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


REGION_CHOICES = [(value, value) for value in REGIONS]
GENRE_CHOICES = [(value, value) for value in GENRES]
SPACE_CATEGORY_CHOICES = [(value, value) for value in SPACE_CATEGORIES]
ENTRY_TYPE_CHOICES = [
    ('standing', 'Standing'),
    ('seat', 'Seat'),
    ('free', 'Free'),
]
PROPOSAL_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]


class NotificationSetting(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='notification_setting',
        on_delete=models.CASCADE,
    )
    performance_update = models.BooleanField(default=True)
    proposal = models.BooleanField(default=True)
    reservation = models.BooleanField(default=True)
    marketing = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"NotificationSetting({self.user})"


class Artist(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='artist_profile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    genres = models.CharField(max_length=255, help_text='쉼표로 구분된 장르')
    equipments = models.TextField()
    portfolio_url = models.URLField(blank=True)
    image_url = models.URLField()
    history = models.TextField()

    def __str__(self) -> str:
        return self.name


class Space(TimeStampedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='spaces',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=SPACE_CATEGORY_CHOICES)
    genres = models.TextField()
    region = models.CharField(max_length=50, choices=REGION_CHOICES)
    address = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    description = models.TextField()
    equipments = models.TextField()
    image_url = models.URLField()

    def __str__(self) -> str:
        return self.name


class Event(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    region = models.CharField(max_length=50, choices=REGION_CHOICES)
    date = models.DateField()
    time = models.TimeField()
    venue_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    price = models.PositiveIntegerField()
    is_free = models.BooleanField(default=False)
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    image_url = models.URLField()
    allow_dyve_reservation = models.BooleanField(default=True)
    advertise = models.BooleanField(default=False)
    space = models.ForeignKey(
        Space,
        related_name='events',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    artists = models.ManyToManyField(Artist, related_name='events', blank=True)

    def __str__(self) -> str:
        return self.title


class Reservation(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='reservations',
        on_delete=models.CASCADE,
    )
    event = models.ForeignKey(Event, related_name='reservations', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    seat = models.CharField(max_length=255, blank=True)
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    price = models.PositiveIntegerField()
    qr_code = models.CharField(max_length=255)
    reservation_code = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return f"Reservation({self.reservation_code})"


class Proposal(TimeStampedModel):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_proposals',
        on_delete=models.CASCADE,
    )
    receiver_artist = models.ForeignKey(
        Artist,
        related_name='received_proposals',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    receiver_space = models.ForeignKey(
        Space,
        related_name='received_proposals',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    content = models.TextField()
    status = models.CharField(max_length=20, choices=PROPOSAL_STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Proposal({self.sender_id}->{self.receiver_artist_id or self.receiver_space_id})"


class Settlement(TimeStampedModel):
    space = models.ForeignKey(Space, related_name='settlements', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name='settlements', on_delete=models.CASCADE)
    total_tickets = models.PositiveIntegerField()
    settled_amount = models.PositiveIntegerField()
    settled_at = models.DateTimeField()

    def __str__(self) -> str:
        return f"Settlement({self.event_id})"
