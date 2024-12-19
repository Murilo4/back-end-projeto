from rest_framework import serializers
from ..models import Places, Category, PlaceCategories, PlacesPhotos


class CreatePlace(serializers.ModelSerializer):
    class Meta:
        model = Places
        fields = ('description', 'type', 'locationX',
                  'locationY', 'work_start', 'work_stop',
                  'enterprise', 'about')

    def create(self, validated_data):
        place = Places(**validated_data)
        place.save()
        return place


class CreateCategory(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category']

    def create(self, validated_data):
        category = Category(**validated_data)
        category.save()
        return category


class CreatePlaceCat(serializers.ModelSerializer):
    class Meta:
        model = PlaceCategories
        fields = ('category', 'place')

    def create(self, validated_data):
        placeCat = PlaceCategories(**validated_data)
        placeCat.save()
        return placeCat


class PlaceGetSerializer(serializers.ModelSerializer):
    workStart = serializers.CharField(source="work_start")
    workStop = serializers.IntegerField(source="work_stop")

    class Meta:
        model = Places
        fields = ('description', 'type', 'locationX',
                  'locationY', 'workStart', 'workStop',
                  'enterprise', 'about')


class PlacePhotoGetSerializer(serializers.ModelSerializer):
    workStart = serializers.CharField(source="work_start")
    workStop = serializers.IntegerField(source="work_stop")

    class Meta:
        model = PlacesPhotos
        fields = ('')
