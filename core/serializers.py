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
            'genres',
            'equipments',
            'portfolio_url',
            'image_url',
            'history',
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


class DummyUserSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone']
        read_only_fields = ['id', 'username', 'email', 'phone']
        ref_name = 'DummyUser'

    def get_phone(self, obj):
        return self.context.get('phone')


class DummyArtistSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    portfolio_link = serializers.URLField(source='portfolio_url', read_only=True)
    required_equipment = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ['id', 'name', 'category', 'portfolio_link', 'required_equipment', 'phone']
        read_only_fields = ['id', 'name', 'category', 'portfolio_link', 'required_equipment', 'phone']
        ref_name = 'DummyArtist'

    def get_category(self, obj):
        return self.context.get('category', 'music')

    def get_required_equipment(self, obj):
        return self.context.get('required_equipment', [])

    def get_phone(self, obj):
        return self.context.get('phone')


class DummyCreateResponseSerializer(serializers.Serializer):
    events_created = serializers.IntegerField(default=0)
    artists_created = serializers.IntegerField(default=0)
    spaces_created = serializers.IntegerField(default=0)


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['id', 'name', 'location', 'capacity', 'description', 'phone']
        read_only_fields = ['id', 'name', 'location', 'capacity', 'description', 'phone']
