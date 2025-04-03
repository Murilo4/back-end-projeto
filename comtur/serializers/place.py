from rest_framework import serializers
from ..models import Places, Category, PlaceCategories, PlacesPhotos
from ..models import UserPlaces, PlacesComments, PlacesRating, PlacesCity
from ..models import PlacesStates


class CreatePlace(serializers.ModelSerializer):
    lowerPrice = serializers.IntegerField(source="lower_price")
    higherPrice = serializers.IntegerField(source="higherPrice")

    class Meta:
        model = Places
        fields = ('description', 'type', 'locationX',
                  'locationY', 'work_start', 'work_stop',
                  'enterprise', 'about', 'city', 'lowerPrice',
                  'higherPrice')

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
    workStop = serializers.CharField(source="work_stop")
    lowerPrice = serializers.IntegerField(source="lower_price")
    higherPrice = serializers.IntegerField(source="higher_price")

    class Meta:
        model = Places
        fields = ('description', 'type',
                  'locationX', 'rating_number',
                  'locationY', 'workStart', 'workStop',
                  'enterprise', 'about', 'lowerPrice,'
                  'higherPrice')


class PlacePhotoGetSerializer(serializers.ModelSerializer):
    imgUrl = serializers.CharField(source="img_url")

    class Meta:
        model = PlacesPhotos
        fields = ('imgUrl', 'description')


class UpdatePlaces(serializers.ModelSerializer):
    workStart = serializers.CharField(source="work_start", required=False)
    workStop = serializers.CharField(source="work_stop", required=False)
    lowerPrice = serializers.IntegerField(source="lower_price", required=False)
    higherPrice = serializers.IntegerField(source="higher_price",
                                           required=False)

    class Meta:
        model = Places
        fields = ('description', 'type', 'locationX', 'locationY',
                  'workStart', 'workStop', 'about', 'lowerPrice',
                  'higherPrice')

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UpdatePlacesUsers(serializers.ModelSerializer):

    class Meta:
        model = Places
        fields = ('comments_number', 'rating_number')

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
        model = PlacesComments
        fields = ('comment')


class CreateUserPlace(serializers.ModelSerializer):
    class Meta:
        model = UserPlaces
        fields = ('user_place', 'place')

    def create(self, validated_data):
        user_place = UserPlaces(**validated_data)
        user_place.save()
        return user_place


class CreatePlaceRating(serializers.ModelSerializer):
    class Meta:
        model = PlacesRating
        fields = ('rating', 'place_rating', 'user_place')

    def create(self, validated_data):
        rating = PlacesRating(**validated_data)
        rating.save()
        return rating


class CreatePlaceComment(serializers.ModelSerializer):
    class Meta:
        model = PlacesComments
        fields = ('comment', 'place_comment', 'user_comment')

    def create(self, validated_data):
        comment = PlacesComments(**validated_data)
        comment.save()
        return comment


class UpdateUserPlace(serializers.ModelSerializer):
    class Meta:
        model = UserPlaces
        fields = ('user_place', 'place', 'favorite')

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CreateUserPlaceFavorite(serializers.ModelSerializer):
    class Meta:
        model = UserPlaces
        fields = ('user_place', 'place', 'favorite')

    def create(self, validated_data):
        user_place = UserPlaces(**validated_data)
        user_place.save()
        return user_place


class UpdatePlaceComment(serializers.ModelSerializer):
    class Meta:
        model = PlacesComments
        fields = ['comment']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UpdatePlaceRating(serializers.ModelSerializer):
    class Meta:
        model = PlacesRating
        fields = ['rating']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CreateCity(serializers.ModelSerializer):
    class Meta:
        model = PlacesCity
        fields = ['city', 'placeState']

    def create(self, validated_data):
        city = PlacesCity(**validated_data)
        city.save()
        return city


class CreateState(serializers.ModelSerializer):
    class Meta:
        model = PlacesStates
        fields = ['state']

    def create(self, validated_data):
        state = PlacesStates(**validated_data)
        state.save()
        return state


class UpdatePlacesCityState(serializers.ModelSerializer):

    class Meta:
        model = Places
        fields = ('city', 'state')

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UpdateMediumRating(serializers.ModelSerializer):
    class Meta:
        model = Places
        fields = ['medium_rating']

    def update(self, instance, validated_data):
        instance.medium_rating = validated_data.get(
            'medium_rating', instance.medium_rating)
        instance.save()
        return instance
