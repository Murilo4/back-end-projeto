from rest_framework import serializers
from ..models import NormalUser


class CreateNormalUser(serializers.ModelSerializer):
    class Meta:
        model = NormalUser
        fields = 'email', 'password', 'cpf', 'phone'

    def create(self, validated_data):
        user = NormalUser(**validated_data)
        user.save()
        return user
