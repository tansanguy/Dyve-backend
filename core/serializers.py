from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    Artist,
    Event,
    NotificationSetting,
    Proposal,
    Reservation,
    Settlement,
    Space,
    Venue,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username']


class SessionLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class SessionLoginResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = UserSerializer()
    csrf_token = serializers.CharField()


class SessionLogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSetting
        fields = [
            'id',
            'performance_update',
            'proposal',
            'reservation',
            'marketing',
        ]


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = [
            'id',
            'user',
            'name',
            'category',
            'genres',
            'equipments',
            'portfolio_url',
            'image_url',
            'history',
            'phone',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = [
            'id',
            'owner',
            'name',
            'category',
            'genres',
            'region',
            'address',
            'capacity',
            'description',
            'equipments',
            'image_url',
            'phone',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class EventSerializer(serializers.ModelSerializer):
    artists = serializers.PrimaryKeyRelatedField(queryset=Artist.objects.all(), many=True, required=False)

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'genre',
            'region',
            'date',
            'time',
            'venue_name',
            'address',
            'price',
            'is_free',
            'entry_type',
            'image_url',
            'allow_dyve_reservation',
            'advertise',
            'space',
            'artists',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        artists = validated_data.pop('artists', [])
        event = super().create(validated_data)
        if artists:
            event.artists.set(artists)
        return event

    def update(self, instance, validated_data):
        artists = validated_data.pop('artists', None)
        event = super().update(instance, validated_data)
        if artists is not None:
            event.artists.set(artists)
        return event


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            'id',
            'user',
            'event',
            'quantity',
            'seat',
            'entry_type',
            'price',
            'qr_code',
            'reservation_code',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'entry_type', 'price', 'created_at', 'updated_at']


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = [
            'id',
            'sender',
            'receiver_artist',
            'receiver_space',
            'content',
            'status',
            'sent_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'sender', 'status', 'sent_at', 'created_at', 'updated_at']


class SettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settlement
        fields = [
            'id',
            'space',
            'event',
            'total_tickets',
            'settled_amount',
            'settled_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['id', 'name', 'location', 'capacity', 'description', 'phone']
        read_only_fields = ['id', 'name', 'location', 'capacity', 'description', 'phone']


class SeedResultSerializer(serializers.Serializer):
    artists_created = serializers.IntegerField()
    spaces_created = serializers.IntegerField()
    events_created = serializers.IntegerField()


class SeedOneArtistSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    category = serializers.CharField()
    profile_image_url = serializers.URLField()
    portfolio_link = serializers.CharField()
    required_equipment = serializers.ListField(child=serializers.CharField())


class SeedOneSpaceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    region = serializers.CharField()
    address = serializers.CharField()
    image_url = serializers.URLField()
    capacity = serializers.IntegerField()
    mood = serializers.CharField()
    phone_number = serializers.CharField()


class SeedOneEventSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    artist_id = serializers.IntegerField()
    space_id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    poster_image_url = serializers.URLField()
    date_time = serializers.CharField()
    genre = serializers.CharField()
    running_time = serializers.IntegerField()
    price = serializers.IntegerField()
    entry_type = serializers.CharField()


class SeedOneResponseSerializer(serializers.Serializer):
    artist = SeedOneArtistSerializer()
    space = SeedOneSpaceSerializer()
    event = SeedOneEventSerializer()
