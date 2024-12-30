from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from dotenv import load_dotenv
from ....models import Address, HouseNumber, Neighborhood, neighborhoodAddress
from ....models import Street, addressStreet, City
from ....serializers.address import UpdateAddress, CreateHouseNumber
from ....serializers.address import State, CreateNeighborhood, CreateStreet
from ....serializers.address import CreateState, CreateNeighborAddress
from ....serializers.address import UpdateAddressState, createCity
from ....serializers.address import CreateStreetAddress, UpdateAddressNumber
from ....serializers.address import UpdateAddressCity
from ....throttles import DailyRateThrottle, HourlyRateThrottle
from ....throttles import MinuteRateThrottleAnon
import jwt
import os

load_dotenv()

SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['PUT'])
@throttle_classes([
    MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
def update_address(request):
    if request.method != 'PUT':
        return JsonResponse({'success': False,
                             'message': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                "success": False,
                "message": "Token de acesso não fornecido ou formato inválido."
            }, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get('id')
        address_id = request.data.get('addressId')

        state = request.data.get('state')
        neighborhood = request.data.get('neighborhood')
        street = request.data.get('street')
        numbers = request.data.get('number')
        city = request.data.get('city')

        try:
            address = Address.objects.get(id=address_id, user_address=user_id)
        except Address.DoesNotExist:
            return JsonResponse({'success': False,
                                 'message': 'Endereço não encontrado.'},
                                status=status.HTTP_404_NOT_FOUND)

        up_address = {
            'postal': request.data.get('postal'),
            'address_type': request.data.get('addressType')
        }
        with transaction.atomic():
            update_address_base = UpdateAddress(address,
                                                data=up_address,
                                                partial=True)
            if update_address_base.is_valid(raise_exception=True):
                update_address_base.save()

            number_updated, ref_number = update_numbers(
                numbers, address_id)
            state_updated, ref_state = update_state(
                state, address_id)
            city_updated, ref_city = update_city(
                city, address_id)

            if number_updated:
                update_address = UpdateAddressNumber(address,
                                                     data={
                                                         'number': ref_number},
                                                     partial=True)
                if update_address.is_valid(raise_exception=True):
                    update_address.save()
                else:
                    return JsonResponse({'success': False,
                                        'message': 'Numero invalido'},
                                        status=status.HTTP_400_BAD_REQUEST)

            if city_updated:
                update_address = UpdateAddressCity(address,
                                                   data={
                                                    'city': ref_city},
                                                   partial=True)
                if update_address.is_valid(raise_exception=True):
                    update_address.save()
                else:
                    return JsonResponse({'success': False,
                                        'message': 'Numero invalido'},
                                        status=status.HTTP_400_BAD_REQUEST)
            if state_updated:
                update_address = UpdateAddressState(address,
                                                    data={'state': ref_state},
                                                    partial=True)
                if update_address.is_valid(raise_exception=True):
                    update_address.save()
                else:
                    return JsonResponse({'success': False,
                                        'message': 'Invalid data'},
                                        status=status.HTTP_400_BAD_REQUEST)

            userName = neighborhood.strip()

            update_neigh = [
                n.lower().strip() for n in userName.split() if n.strip()]
            update_neighbor(update_neigh, address_id)

            street_ = street.strip()
            new_street = [
                s.lower().strip() for s in street_.split() if s.strip()]
            update_street(new_street, address_id)

            return JsonResponse({'success': True,
                                'message': 'Endereço atualizado com sucesso'},
                                status=status.HTTP_200_OK)

    except Address.DoesNotExist:
        return JsonResponse({'success': False,
                             'message': 'Endereço não encontrado'},
                            status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({'success': False,
                             'message': 'Erro interno no servidor.',
                             'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def update_numbers(numbers, address_id):
    is_updated = True
    referencia = None
    try:
        number_obj = HouseNumber.objects.get(number=numbers)
        number = Address.objects.filter(number=number_obj.id,
                                        id=address_id).exists()
        if number:
            is_updated = False
            return is_updated, referencia
        else:
            referencia = number_obj.id
            print("salvou o numero")
    except HouseNumber.DoesNotExist:
        serializer = CreateHouseNumber(data={"number": numbers})
        if serializer.is_valid():
            new_name_obj = serializer.save()
            referencia = new_name_obj.id
        else:
            is_updated = False

    return is_updated, referencia


def update_city(city, address_id):
    is_updated = True
    referencia = None
    try:
        city_obj = City.objects.get(city=city)
        city_exists = Address.objects.filter(city=city_obj.id,
                                             id=address_id).exists()
        print("buscou")
        if city_exists:
            is_updated = False
            return is_updated, referencia
        else:
            print("chegou antes de salvar a referencia")
            referencia = city_obj.id
            print("salvou a cidade")
    except City.DoesNotExist:
        print("chegou cidade")
        serializer = createCity(data={"city": city})
        if serializer.is_valid(raise_exception=True):
            new_name_obj = serializer.save()
            referencia = new_name_obj.id
        else:
            is_updated = False

    return is_updated, referencia


def update_state(state, address_id):
    is_updated = True
    referencias = None
    try:
        state_obj = State.objects.get(state=state)
        address = Address.objects.filter(state=state_obj.id,
                                         id=address_id).exists()
        if address:
            is_updated = False
            return is_updated, referencias
        else:
            referencias = state_obj.id
            print("salvou o estado")
    except (State.DoesNotExist, Address.DoesNotExist):
        print("chegou no state")
        serializer = CreateState(data={"state": state})
        if serializer.is_valid(raise_exception=True):
            new_state_obj = serializer.save()
            referencias = new_state_obj.id
        else:
            is_updated = False
    return is_updated, referencias


def update_neighbor(neighbor, address_id):
    is_updated = True
    referencias = []
    to_keep = []
    for n in neighbor:
        try:
            neigh = Neighborhood.objects.get(neighborhood=n)
            address_neigh = neighborhoodAddress.objects.filter(
                                                neighborhood=neigh.id,
                                                address=address_id).exists()
            if address_neigh:
                to_keep.append(neigh.id)
                pass
            else:
                referencias.append(neigh.id)
        except Neighborhood.DoesNotExist:
            print(n)
            serializer = CreateNeighborhood(data={"neighborhood": n})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                new_neighbor = Neighborhood.objects.get(neighborhood=n)
                referencias.append(new_neighbor.id)
            else:
                is_updated = False

    if referencias:
        neighborhoodAddress.objects.filter(
            address=address_id
        ).exclude(
            neighborhood__in=to_keep
        ).delete()
        order = 1
        for ref in referencias:
            print(ref)
            serializer_state = CreateNeighborAddress(
                data={
                    'neighborhood': ref,
                    'address': address_id,
                    'neighbor_order': order
                }
            )
            if serializer_state.is_valid(raise_exception=True):
                serializer_state.save()
                order += 1
            else:
                is_updated = False

    return is_updated


def update_street(streets, address_id):
    is_updated = True
    referencias = []
    to_keep = []
    for street in streets:
        try:
            street_db = Street.objects.get(street=street)
            address_street = addressStreet.objects.filter(
                                                street=street_db.id,
                                                address=address_id).exists()
            if address_street:
                to_keep.append(street_db.id)
            else:
                referencias.append(street_db.id)
        except (Street.DoesNotExist, addressStreet.DoesNotExist):
            serializer = CreateStreet(data={"street": street})
            if serializer.is_valid():
                serializer.save()
                new_street = Street.objects.get(street=street)
                referencias.append(new_street.id)
            else:
                is_updated = False

    if referencias:
        addressStreet.objects.filter(
            address=address_id
        ).exclude(
            street__in=to_keep
        ).delete()
        order = 1
        for ref in referencias:
            print(ref)
            serializer_state = CreateStreetAddress(
                data={
                    'street': ref,
                    'address': address_id,
                    'street_order': order
                }
            )
            if serializer_state.is_valid(raise_exception=True):
                serializer_state.save()
                order += 1
            else:
                is_updated = False

    return is_updated
