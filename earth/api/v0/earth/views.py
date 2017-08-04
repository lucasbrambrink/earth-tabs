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
                .get(url_identifier=settings_uid)

        except QuerySetting.DoesNotExist:
            pass
        else:
            query_kwargs = [Q(title__icontains=kw.strip())
                            for kw in setting.query_keywords_title.split(',')]
            query = query_kwargs.pop()
            for item in query_kwargs:
                query |= item

            lazy_query = EarthImage.objects.filter(query)

            if setting.score_threshold is not None:
                score_query = '{type}__{operator}'.format(type=setting.score_type,
                                                          operator=setting.score_threshold_operand)
                lazy_query.filter(**{score_query: setting.score_threshold})

            query_ids = lazy_query.values_list('id', flat=True)
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
        new_setting = QuerySetting.objects.create(
            url_identifier=QuerySetting.get_identifier())
        return new_setting


class QuerySettingSave(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = QuerySettingSerializer
    queryset = QuerySetting.objects.all()
    lookup_field = 'settings_uid'

    def get_object(self):
        obj = None
        try:
            obj = QuerySetting.objects.get(url_identifier=self.kwargs[self.lookup_field])
        except QuerySetting.DoesNotExist:
            pass

        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        values = {key: value for key, value in request.GET.items()}
        if not len(values):
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        values['url_identifier'] = self.kwargs[self.lookup_field]
        if values['score_threshold'] == '':
            values['score_threshold'] = None

        serializer = self.get_serializer(data=values)
        if serializer.is_valid():
            for attr, value in serializer.validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return Response(serializer.data)
        else:
            return Response({}, status=status.HTTP_304_NOT_MODIFIED)




