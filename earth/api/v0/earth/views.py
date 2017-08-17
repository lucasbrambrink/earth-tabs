import random
from django.db.models import Q

from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from api.models import EarthImage, QuerySetting, Filter
from .serializers import EarthImageSerializer, QuerySettingSerializer, HistorySerializer, FilterSerializer


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

            group_by_source = []
            for source, frequency in zip(EarthImage.SOURCES,
                                         setting.frequencies):
                if source not in setting.allowed_sources:
                    continue

                filtered_by_source = query_ids.filter(source=source)
                if not filtered_by_source.count():
                    continue

                for choice in range(frequency):
                    group_by_source.append(
                        random.choice(filtered_by_source)
                    )

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


class QuerySettingCreate(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = QuerySettingSerializer

    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_TOKEN')
        if not token:
            return Response({}, status=status.HTTP_403_FORBIDDEN)

        new_setting = QuerySetting.objects.create(
            device_token=token,
            url_identifier=QuerySetting.get_identifier())
        serializer = QuerySettingSerializer(new_setting)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuerySettingRetrieveMixin(object):
    """
    requires token in header to match with db object's token
    """
    kwargs = None
    lookup_field = None

    def get_object(self, request):
        token = request.META.get('HTTP_TOKEN')
        obj = None
        try:
            obj = QuerySetting.objects\
                .prefetch_related('filter_set')\
                .get(url_identifier=self.kwargs[self.lookup_field])

            # TODO: remove this before release
            if obj.device_token == '':
                obj.device_token = token
                obj.save()

            if obj.device_token != token:
               obj = None

        except QuerySetting.DoesNotExist:
            pass

        return obj


class QuerySettingRetrieveView(QuerySettingRetrieveMixin,
                               generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = QuerySettingSerializer
    queryset = QuerySetting.objects.all()
    lookup_field = 'settings_uid'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object(request)
        if instance is None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        instance.filters = instance.filter_set.all()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class QuerySettingSave(QuerySettingRetrieveMixin,
                       generics.UpdateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = QuerySettingSerializer
    queryset = QuerySetting.objects.all()
    lookup_field = 'settings_uid'

    def put(self, request, *args, **kwargs):
        instance = self.get_object(request)
        if instance is None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        values = dict(request.data)
        if not len(values):
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        filter_ids = set()
        for filter_obj in values.get('filters', []):
            filter_obj['setting'] = instance.id
            serializer = FilterSerializer(data=filter_obj)
            serializer.setting = instance
            if serializer.is_valid():
                args = serializer.validated_data
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
        for source in EarthImage.SOURCES:
            is_selected = values.pop('allow_{}'.format(source))
            if is_selected:
                selected_sources.append(source)
        values['allowed_sources'] = ','.join(selected_sources)

        contained_data_sources = []
        for contained_source in EarthImage.SOURCES:
            is_selected = values.pop('contain_{}'.format(contained_source))
            if is_selected:
                contained_data_sources.append(contained_source)
        values['contain_data_sources'] = ','.join(contained_data_sources)

        values['url_identifier'] = self.kwargs[self.lookup_field]
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


class HistoryListApi(QuerySettingRetrieveMixin,
                     generics.ListAPIView):
    serializer_class = HistorySerializer
    permission_classes = (AllowAny,)
    lookup_field = 'settings_uid'
    queryset = QuerySetting.objects.all()

    def list(self, request, *args, **kwargs):
        instance = self.get_object(request)
        if instance is None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        # take slice to avoid showing cached result
        image_ids = [int(image_id) for image_id in instance.history.split(',')
                     if image_id != ''][1:]
        image_query = {i.id: i
                       for i in EarthImage.objects.filter(id__in=image_ids)}

        # preserve order
        images = []
        for image_id in image_ids:
            earth_image = image_query.get(image_id)
            if earth_image is None:
                continue

            serialized_image = EarthImageSerializer(earth_image)
            images.append(serialized_image.data)

        return Response(images)
