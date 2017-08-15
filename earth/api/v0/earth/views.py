import random
from django.db.models import Q

from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .serializers import EarthImageSerializer, QuerySettingSerializer, HistorySerializer, FilterSerializer
from api.models import EarthImage, QuerySetting, Filter


class EarthImageView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializers = EarthImageSerializer
    too_restrictive = False

    def get_random_object(self, all_ids=None):
        all_ids = all_ids or EarthImage.public\
            .values_list('id', flat=True)

        return EarthImage.objects.get(id=random.choice(all_ids))

    def get_object_via_settings(self, settings_uid):
        query_ids = None
        try:
            setting = QuerySetting.objects\
                .get(url_identifier=settings_uid)

        except QuerySetting.DoesNotExist:
            pass
        else:
            query_ids = setting.filter_queryset(EarthImage.public)
            # if no results, allow random -- prevent null response
            if not query_ids.count():
                self.too_restrictive = True
                query_ids = None

            group_by_source = [
                random.choice(query_ids.filter(source=source))
                for source in setting.allowed_sources.split(',')
            ]

            image = self.get_random_object(group_by_source)
            setting.update_history(image)
            if image.source in setting.contain_data_sources:
                image.contain_image = True
            return image

        return self.get_random_object(query_ids)

    def get(self, request, settings_uid=None, *args, **kwargs):
        obj = self.get_random_object() if settings_uid is None else \
            self.get_object_via_settings(settings_uid)

        response_status = status.HTTP_206_PARTIAL_CONTENT if self.too_restrictive\
            else status.HTTP_200_OK

        return Response(EarthImageSerializer(obj).data,
                        status=response_status)


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
            obj = QuerySetting.objects\
                .prefetch_related('filter_set')\
                .get(url_identifier=self.kwargs[self.lookup_field])
        except QuerySetting.DoesNotExist:
            pass

        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        values = {key: value for key, value in request.GET.items()}
        if not len(values):
            instance.filters = instance.filter_set.all()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        filter_ids = set()
        for filter_obj in filter(None, values.get('filters', '').split('|')):

            parsed = dict(kw.split('=') for kw in filter_obj.split(','))
            parsed['setting'] = instance.id
            serializer = FilterSerializer(data=parsed)
            serializer.setting = instance
            if serializer.is_valid():
                args = serializer.validated_data
                args['arguments'] = '&'.join(args.get('arguments', '')\
                    .replace('*', '=')\
                    .split('$'))
                try:
                    obj = Filter.objects.get(source=args.get('source'),
                                             filter_class=args.get('filter_class'),
                                             setting=args.get('setting'))
                    obj.arguments = args.get('arguments')
                    obj.save()
                except Filter.DoesNotExist:
                    obj = Filter.objects.create(**args)

                filter_ids.add(obj.id)

        instance.filter_set.exclude(id__in=filter_ids).delete()

        selected_sources = []
        for source in EarthImage.VERIFIED_SOURCES:
            is_selected = values.pop('allow_{}'.format(source[0]), 'false') == 'true'
            if is_selected:
                selected_sources.append(source[0])
        values['allowed_sources'] = ','.join(selected_sources)
        values['url_identifier'] = self.kwargs[self.lookup_field]

        contained_data_sources = []
        for contained_source in EarthImage.VERIFIED_SOURCES:
            is_selected = values.pop('contain_{}'.format(contained_source[0]), 'false') == 'true'
            if is_selected:
                contained_data_sources.append(contained_source[0])
        values['contain_data_sources'] = ','.join(contained_data_sources)

        serializer = self.get_serializer(data=values)
        if serializer.is_valid():
            for attr, value in serializer.validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            too_restrictive = not instance.filter_queryset(EarthImage.public).count()
            response_status = status.HTTP_206_PARTIAL_CONTENT if too_restrictive \
                else status.HTTP_200_OK
            return Response(serializer.data, status=response_status)
        else:
            return Response({}, status=status.HTTP_304_NOT_MODIFIED)


class HistoryListApi(generics.ListAPIView):
    serializer_class = HistorySerializer
    permission_classes = (AllowAny,)
    lookup_url_kwarg = 'settings_uid'
    queryset = QuerySetting.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            setting = QuerySetting.objects\
                .get(url_identifier=kwargs['settings_uid'])
        except QuerySetting.DoesNotExist:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        # take slice to avoid showing cached result
        image_ids = [int(image_id) for image_id in setting.history.split(',')
                     if image_id != ''][1:]
        image_query = {i.id: i
                       for i in EarthImage.objects.filter(id__in=image_ids)}

        # preserve order
        images = []
        for image_id in image_ids:
            earth_image = EarthImageSerializer(image_query[image_id])
            images.append(earth_image.data)

        return Response(images)
