from rest_framework import serializers
from ..models import CityHistory


class CityHistoryCreate(serializers.ModelSerializer):
    class Meta:
        model = CityHistory
        fields = ['history', 'city']

    def create(self, validated_data):
        city_history = CityHistory(**validated_data)
        city_history.save()
        return city_history


class CityHistoryUpdate(serializers.ModelSerializer):
    class Meta:
        model = CityHistory
        fields = ['history', 'city']

    def update(self, instance, validated_data):
        instance.history = validated_data.get('history', instance.history)
        instance.city = validated_data.get('city', instance.city)
        instance.save()
        return instance
