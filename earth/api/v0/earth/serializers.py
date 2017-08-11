from rest_framework import serializers
from api.models import EarthImage, QuerySetting, Filter


class EarthImageSerializer(serializers.ModelSerializer):
    contain_image = serializers.BooleanField(default=False)

    class Meta:
        model = EarthImage
        exclude = ('id',)


class FilterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Filter
        exclude = ('id',)


class QuerySettingSerializer(serializers.ModelSerializer):
    filters = FilterSerializer(many=True,
                               allow_null=True,
                               read_only=True)

    class Meta:
        model = QuerySetting
        exclude = ('id', 'history')




class HistorySerializer(serializers.Serializer):
    images = EarthImageSerializer(many=True,
                                  read_only=True,
                                  allow_null=True)

    class Meta:
        fields = ('images')
