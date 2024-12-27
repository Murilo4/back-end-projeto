from rest_framework import serializers
from ..models import Address, HouseNumber, addressStreet
from ..models import State, City, Street, neighborhoodAddress
from ..models import Neighborhood


class CreateAddress(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = ('user_address', 'number', 'state', 'city', 'postal')

    def create(self, validated_data):
        address = Address(**validated_data)
        address.save()
        return address


class UpdateAddress(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('city', 'postal',
                  'number', 'state')

    def update(self, instance, validated_data):

        instance.number = validated_data.get('number', instance.number)
        instance.city = validated_data.get('city', instance.city)
        instance.postal = validated_data.get('postal', instance.postal)
        instance.state = validated_data.get('state', instance.state)
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

    def create(self, validated_data):
        city = City(**validated_data)
        city.save()
        return city


class CreateStreet(serializers.ModelSerializer):
    class Meta:
        model = Street
        fields = ['street']

    def create(self, validated_data):
        street = Street(**validated_data)
        street.save()
        return street


class CreateStreetAddress(serializers.ModelSerializer):
    class Meta:
        model = addressStreet
        fields = ['street', 'address', 'street_order']

    def create(self, validated_data):
        AddressStreet = addressStreet(**validated_data)
        AddressStreet.save()
        return AddressStreet


class CreateNeighborhood(serializers.ModelSerializer):
    class Meta:
        model = Neighborhood
        fields = ['neighborhood']

    def create(self, validated_data):
        neighbor = Neighborhood(**validated_data)
        neighbor.save()
        return neighbor


class CreateNeighborAddress(serializers.ModelSerializer):
    class Meta:
        model = neighborhoodAddress
        fields = ['neighborhood', 'address', 'neighbor_order']

    def create(self, validated_data):
        neighboraddress = neighborhoodAddress(**validated_data)
        neighboraddress.save()
        return neighboraddress
