from rest_framework import serializers
from ..models import Address, HouseNumber, NumberAddress, StateAddress
from ..models import State


class CreateAddress(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = ('user_address', 'street',
                  'neighborhood', 'city', 'postal')

    def create(self, validated_data):
        address = Address(**validated_data)
        address.save()
        return address


class UpdateAddress(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('street', 'city', 'postal', 'neighborhood',)

    def update(self, instance, validated_data):

        instance.street = validated_data.get('street', instance.street)
        instance.city = validated_data.get('city', instance.city)
        instance.postal = validated_data.get('postal', instance.postal)
        instance.neighborhood = validated_data.get('neighborhood',
                                                   instance.neighborhood)
        instance.save()

        return instance


class CreateHouseNumber(serializers.ModelSerializer):
    class Meta:
        model = HouseNumber
        fields = ['number']

    def create(self, validated_data):
        print(validated_data)
        number = HouseNumber(**validated_data)
        number.save()
        return number


class CreateNumberAddress(serializers.ModelSerializer):
    class Meta:
        model = NumberAddress
        fields = ('house_number', 'address')

    def create(self, validated_data):
        number = NumberAddress(**validated_data)
        number.save()
        return number


class CreateStateAddress(serializers.ModelSerializer):
    class Meta:
        model = StateAddress
        fields = ('state', 'address')

    def create(self, validated_data):
        state = StateAddress(**validated_data)
        state.save()
        return state


class CreateState(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['state']

    def create(self, validated_data):
        state = State(**validated_data)
        state.save()
        return state
