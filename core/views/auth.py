from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    SessionLoginResponseSerializer,
    SessionLoginSerializer,
    SessionLogoutResponseSerializer,
    UserSerializer,
)

User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class FakeLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [SessionAuthentication]

    @extend_schema(
        tags=['auth'],
        responses={200: SessionLoginResponseSerializer},
        description='테스트용 계정을 자동 생성 후 세션을 발급하는 페이크 로그인 엔드포인트',
    )
    def post(self, request):
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'testuser@example.com', 'first_name': 'Test', 'last_name': 'User'},
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=['password'])

        backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user, backend=backend)
        csrf_token = get_token(request)

        response = Response(
            {
                'message': 'Fake login successful',
                'user': UserSerializer(user).data,
                'csrf_token': csrf_token,
            },
            status=status.HTTP_200_OK,
        )
        response.headers['X-CSRFToken'] = csrf_token
        return response


class SessionLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [SessionAuthentication]

    @extend_schema(
        tags=['auth'],
        request=SessionLoginSerializer,
        responses={
            200: SessionLoginResponseSerializer,
            400: OpenApiResponse(description='잘못된 사용자 이름 또는 비밀번호'),
        },
        description='세션을 생성하고 CSRF 토큰을 함께 반환하는 로그인 엔드포인트',
    )
    def post(self, request):
        serializer = SessionLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if user is None:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        csrf_token = get_token(request)

        response = Response(
            {
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'csrf_token': csrf_token,
            },
            status=status.HTTP_200_OK,
        )
        response.headers['X-CSRFToken'] = csrf_token
        return response


class SessionLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    @extend_schema(
        tags=['auth'],
        responses={200: SessionLogoutResponseSerializer},
        description='세션을 종료하고 세션/CSRF 쿠키를 삭제하는 로그아웃 엔드포인트',
    )
    def post(self, request):
        logout(request)

        response = Response({'message': 'Logged out'}, status=status.HTTP_200_OK)
        response.delete_cookie(
            settings.SESSION_COOKIE_NAME,
            path='/',
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )
        response.delete_cookie(
            settings.CSRF_COOKIE_NAME,
            path='/',
            samesite=settings.CSRF_COOKIE_SAMESITE,
        )
        return response


@method_decorator(csrf_exempt, name='dispatch')
class FakeLogoutView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [SessionAuthentication]

    @extend_schema(
        tags=['auth'],
        responses={200: SessionLogoutResponseSerializer},
        description='페이크 로그인 세션을 종료하고 쿠키를 삭제하는 엔드포인트',
    )
    def post(self, request):
        logout(request)

        response = Response({'message': 'Fake logged out'}, status=status.HTTP_200_OK)
        response.delete_cookie(
            settings.SESSION_COOKIE_NAME,
            path='/',
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )
        response.delete_cookie(
            settings.CSRF_COOKIE_NAME,
            path='/',
            samesite=settings.CSRF_COOKIE_SAMESITE,
        )
        return response
