from rest_framework import serializers
from ..models import NormalUser


class CreateNormalUser(serializers.ModelSerializer):

    class Meta:
        model = NormalUser
        fields = 'email', 'password', 'cpf', 'phone', 'cnpj', 'photo'

    def create(self, validated_data):
        user = NormalUser(**validated_data)
        user.save()
        return user


class UpdateNormalUser(serializers.ModelSerializer):
    class Meta:
        model = NormalUser
        fields = 'email', 'cpf', 'phone', 'cnpj', 'photo'

    def update(self, instance, validated_data):
        instance.email = validated_data.get(
            'email', instance.email)
        instance.cpf = validated_data.get(
            'cpf', instance.cpf)
        instance.phone = validated_data.get(
            'phone', instance.phone)
        instance.photo = validated_data.get(
            'photo', instance.photo)
        instance.cnpj = validated_data.get(
            'cnpj', instance.cnpj)

        instance.save()

        return instance


class UpdateValidationNormalUser(serializers.ModelSerializer):
    class Meta:
        model = NormalUser
        fields = 'is_validated'

    def update(self, instance, validated_data):
        instance.is_validated = validated_data.get(
            'is_validated', instance.is_validated)

        instance.save()

        return instance
