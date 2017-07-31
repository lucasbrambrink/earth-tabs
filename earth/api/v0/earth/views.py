import random

from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .serializers import EarthImageSerializer
from api.models import EarthImage


class EarthImageView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializers = EarthImageSerializer

    def get(self, request, *args, **kwargs):
        all_ids = EarthImage.objects.values_list('id', flat=True)
        random_obj = EarthImage.objects.get(id=random.choice(all_ids))
        return Response(EarthImageSerializer(random_obj).data,
                        status=status.HTTP_200_OK)
