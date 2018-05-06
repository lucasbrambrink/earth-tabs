from rest_framework import serializers
from api.models import EarthImage, QuerySetting, Filter, FavoriteImageItem


class EarthImageSerializer(serializers.ModelSerializer):
    contain_image = serializers.BooleanField(default=False)
    is_administrator = serializers.BooleanField(default=False)
    google_map_url = serializers.CharField(max_length=255)
    is_favorite = serializers.BooleanField(default=False)

    class Meta:
        model = EarthImage
        exclude = ()


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
        exclude = ('id', 'history', 'device_token')


class HistorySerializer(serializers.Serializer):
    images = EarthImageSerializer(many=True,
                                  read_only=True,
                                  allow_null=True)

    class Meta:
        fields = ('images',)


class FavoriteImageItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteImageItem
        exclude = ('id', 'settings')
