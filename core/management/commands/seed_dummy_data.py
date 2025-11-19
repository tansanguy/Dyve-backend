from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.constants import REGIONS
from core.models import Artist, Event, NotificationSetting, Proposal, Reservation, Settlement, Space

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed dummy DYVE data for local development.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding dummy data...')
        alice, _ = User.objects.get_or_create(
            username='alice',
            defaults={'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Kim'},
        )
        if not alice.has_usable_password():
            alice.set_password('password123')
            alice.save()

        bob, _ = User.objects.get_or_create(
            username='bob',
            defaults={'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Lee'},
        )
        if not bob.has_usable_password():
            bob.set_password('password123')
            bob.save()

        cara, _ = User.objects.get_or_create(
            username='cara',
            defaults={'email': 'cara@example.com', 'first_name': 'Cara', 'last_name': 'Park'},
        )
        if not cara.has_usable_password():
            cara.set_password('password123')
            cara.save()

        NotificationSetting.objects.get_or_create(user=alice)

        artist1, _ = Artist.objects.get_or_create(
            user=alice,
            defaults={
                'name': 'Seoul Groove',
                'genres': 'Jazz,Indie',
                'equipments': 'Guitar, Keyboard',
                'portfolio_url': 'https://example.com/seoulgroove',
                'image_url': 'https://images.dyve.local/artist1.jpg',
                'history': '2023 Seoul Jazz Festival',
            },
        )
        artist2, _ = Artist.objects.get_or_create(
            user=cara,
            defaults={
                'name': 'Rooftop Vibes',
                'genres': 'Electronic,디제잉',
                'equipments': 'DJ Controller',
                'portfolio_url': 'https://example.com/rooftopvibes',
                'image_url': 'https://images.dyve.local/artist2.jpg',
                'history': 'Hongdae Rooftop Party',
            },
        )

        space1, _ = Space.objects.get_or_create(
            owner=bob,
            name='Dyve Live Club',
            defaults={
                'category': '라이브클럽',
                'genres': 'Rock,Indie',
                'region': '서울',
                'address': '서울시 마포구 어딘가 123',
                'capacity': 200,
                'description': '홍대 메인 라이브 클럽',
                'equipments': 'Full band set',
                'image_url': 'https://images.dyve.local/space1.jpg',
            },
        )
        space2, _ = Space.objects.get_or_create(
            owner=cara,
            name='Incheon Rooftop',
            defaults={
                'category': '루프탑',
                'genres': 'Electronic,디제잉',
                'region': '인천',
                'address': '인천 연수구 바닷가 45',
                'capacity': 120,
                'description': '바다 전망 루프탑',
                'equipments': 'Sound system',
                'image_url': 'https://images.dyve.local/space2.jpg',
            },
        )

        event1, _ = Event.objects.get_or_create(
            title='Hongdae Indie Night',
            defaults={
                'description': '신예 인디 밴드 쇼케이스',
                'genre': 'Indie',
                'region': '서울',
                'date': timezone.now().date(),
                'time': timezone.now().time().replace(second=0, microsecond=0),
                'venue_name': 'Dyve Live Club',
                'address': '서울시 마포구 어딘가 123',
                'price': 20000,
                'is_free': False,
                'entry_type': '스탠딩',
                'image_url': 'https://images.dyve.local/event1.jpg',
                'allow_dyve_reservation': True,
                'advertise': True,
                'space': space1,
            },
        )
        event1.artists.set([artist1])

        event2, _ = Event.objects.get_or_create(
            title='Incheon Sunset Beats',
            defaults={
                'description': '디제잉과 일렉트로닉 라이브',
                'genre': 'Electronic',
                'region': '인천',
                'date': timezone.now().date(),
                'time': timezone.now().time().replace(second=0, microsecond=0),
                'venue_name': 'Incheon Rooftop',
                'address': '인천 연수구 바닷가 45',
                'price': 0,
                'is_free': True,
                'entry_type': '입장확인',
                'image_url': 'https://images.dyve.local/event2.jpg',
                'allow_dyve_reservation': True,
                'advertise': False,
                'space': space2,
            },
        )
        event2.artists.set([artist2])

        Reservation.objects.get_or_create(
            user=alice,
            event=event1,
            defaults={
                'quantity': 2,
                'seat': 'Standing',
                'entry_type': event1.entry_type,
                'price': event1.price * 2,
                'qr_code': 'QR-AUTO-1',
                'reservation_code': 'RSV-AUTO-1',
            },
        )
        Reservation.objects.get_or_create(
            user=cara,
            event=event2,
            defaults={
                'quantity': 1,
                'seat': 'General',
                'entry_type': event2.entry_type,
                'price': 0,
                'qr_code': 'QR-AUTO-2',
                'reservation_code': 'RSV-AUTO-2',
            },
        )

        Proposal.objects.get_or_create(
            sender=bob,
            receiver_artist=artist1,
            defaults={'content': '홍대 인디 나잇 콜라보 제안', 'status': 'pending'},
        )
        Proposal.objects.get_or_create(
            sender=alice,
            receiver_space=space2,
            defaults={'content': '루프탑 공연 제안', 'status': 'accepted'},
        )

        Settlement.objects.get_or_create(
            space=space1,
            event=event1,
            defaults={'total_tickets': 180, 'settled_amount': 3000000, 'settled_at': timezone.now()},
        )
        Settlement.objects.get_or_create(
            space=space2,
            event=event2,
            defaults={'total_tickets': 120, 'settled_amount': 1500000, 'settled_at': timezone.now()},
        )

        self.stdout.write(self.style.SUCCESS('Dummy data seeded.'))
