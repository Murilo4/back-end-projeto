from rest_framework import serializers
from ..models import Address, HouseNumber, addressStreet
from ..models import State, City, Street, neighborhoodAddress
from ..models import Neighborhood


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


class CreateState(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['state']

    def create(self, validated_data):
        state = State(**validated_data)
        state.save()
        return state


class createCity(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['city']


class CreateStreet(serializers.ModelSerializer):
    class Meta:
        model = Street
        fields = ['street']


class CreateStreetAddress(serializers.ModelSerializer):
    class Meta:
        model = addressStreet
        fields = ['street', 'address']


class CreateNeighborhood(serializers.ModelSerializer):
    class Meta:
        model = Neighborhood
        fields = ['neighborhood']


class CreateNeighborAddress(serializers.ModelSerializer):
    class Meta:
        model = neighborhoodAddress
        fields = ['neighborhood', 'address']
