from rest_framework import serializers
from api.models import EarthImage, QuerySetting


class EarthImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = EarthImage
        exclude = ('id',)


class QuerySettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuerySetting
        exclude = ('id', 'history')


class HistorySerializer(serializers.Serializer):
    images = EarthImageSerializer(many=True,
                                  read_only=True,
                                  allow_null=True)

    class Meta:
        fields = ('images')
