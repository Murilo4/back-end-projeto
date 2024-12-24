from rest_framework import serializers
from ..models import Places, Category, PlaceCategories, PlacesPhotos


class CreatePlace(serializers.ModelSerializer):
    class Meta:
        model = Places
        fields = ('description', 'type', 'locationX',
                  'locationY', 'work_start', 'work_stop',
                  'enterprise', 'about')

    def create(self, validated_data):
        print("chegou ao serializer")
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
        fields = ('description', 'type', 'rating',
                  'locationX', 'rating_number',
                  'locationY', 'workStart', 'workStop',
                  'enterprise', 'about')


class PlacePhotoGetSerializer(serializers.ModelSerializer):
    imgUrl = serializers.CharField(source="img_url")

    class Meta:
        model = PlacesPhotos
        fields = ('imgUrl', 'description')


class UpdatePlaces(serializers.ModelSerializer):
    workStart = serializers.CharField(source="work_start", required=False)
    workStop = serializers.CharField(source="work_stop", required=False)

    class Meta:
        model = Places
        fields = ('description', 'type', 'locationX', 'locationY',
                  'workStart', 'workStop', 'about')

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CreatePhotos(serializers.ModelSerializer):
    class Meta:
        model = PlacesPhotos
        fields = ['img_url', 'description', 'place_photo']

    def create(self, validated_data):
        photo = PlacesPhotos(**validated_data)
        photo.save()
        return photo


class PlaceCommentsGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacesPhotos
        fields = ('imgUrl', 'description')
