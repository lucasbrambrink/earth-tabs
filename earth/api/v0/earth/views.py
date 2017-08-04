import random

from django.db.models import Q

from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .serializers import EarthImageSerializer, QuerySettingSerializer
from api.models import EarthImage, QuerySetting


class EarthImageView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializers = EarthImageSerializer

    def get_random_object(self, all_ids=None):
        all_ids = all_ids or EarthImage.objects.values_list('id', flat=True)
        return EarthImage.objects.get(id=random.choice(all_ids))

    def get_object_via_settings(self, settings_uid):
        query_ids = None
        try:
            setting = QuerySetting.objects\
                .exclude(query_keywords_title='')\
                .get(url_identifier=settings_uid)
        except QuerySetting.DoesNotExist:
            pass
        else:
            query_kwargs = [Q(title__icontains=kw.strip())
                            for kw in setting.query_keywords_title.split(',')]
            query = query_kwargs.pop()
            for item in query_kwargs:
                query |= item

            query_ids = EarthImage.objects.filter(query).values_list('id', flat=True)

            if not query_ids.count():
                query_ids = None

        return self.get_random_object(query_ids)

    def get(self, request, settings_uid=None, *args, **kwargs):
        obj = self.get_random_object() if settings_uid is None else \
            self.get_object_via_settings(settings_uid)

        return Response(EarthImageSerializer(obj).data,
                        status=status.HTTP_200_OK)


class QuerySettingCreate(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = QuerySettingSerializer

    def get_object(self):
        new_setting = QuerySetting.objects.create()
        new_setting.url_identifier = new_setting.get_identifier()
        return new_setting
