from __future__ import annotations

import cloudinary.uploader
from django.conf import settings
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView


class ImageUploadView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        """multipart/form-data 이미지 파일을 받아 Cloudinary에 업로드하고 URL을 반환합니다."""
        file_obj = request.data.get('image')
        if not file_obj:
            return Response(
                {'detail': 'image 필드로 보낼 파일이 누락되었습니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        folder = f"{settings.DYVE_DUMMY_IMAGE_FOLDER}/uploads"
        try:
            result = cloudinary.uploader.upload(
                file_obj,
                folder=folder,
                use_filename=True,
                unique_filename=False,
            )
        except Exception as exc:
            return Response(
                {'detail': '이미지 업로드 실패', 'error': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        secure_url = result.get('secure_url')
        if not secure_url:
            return Response(
                {'detail': 'Cloudinary 응답에 secure_url이 없습니다.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({'image_url': secure_url}, status=status.HTTP_201_CREATED)
