from rest_framework import serializers
from ..models import Names, UserName


class CreateNames(serializers.ModelSerializer):
    class Meta:
        model = Names
        fields = ['name']

    def create(self, validated_data):
        name = Names(**validated_data)
        name.save()
        return name


class CreateUserName(serializers.ModelSerializer):
    class Meta:
        model = UserName
        fields = ['name', 'user', 'create_order']

    def create(self, validated_data):
        username = UserName(**validated_data)
        username.save()
        return username
