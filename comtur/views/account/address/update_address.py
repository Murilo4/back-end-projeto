from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from dotenv import load_dotenv
from ....models import Address, HouseNumber, Neighborhood, neighborhoodAddress
from ....models import Street, addressStreet
from ....serializers.address import UpdateAddress, CreateHouseNumber
from ....serializers.address import State, CreateNeighborhood, CreateStreet
from ....serializers.address import CreateState, CreateNeighborAddress
from ....serializers.address import CreateStreetAddress
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
        numbers = request.data.get('number')

        try:
            address = Address.objects.get(id=address_id, user_address=user_id)
        except Address.DoesNotExist:
            return JsonResponse({'success': False,
                                 'message': 'Endereço não encontrado.'},
                                status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            number_updated, ref_number = update_numbers(
                numbers, address_id)
            state_updated, need_update, ref_state = update_state(
                state, address_id)
            if number_updated:
                update_address = UpdateAddress(address,
                                               data=ref_number, partial=True)
            if update_address.is_valid():
                update_address.save()
            else:
                return JsonResponse({'success': False,
                                     'message': 'Invalid data'},
                                    status=status.HTTP_400_BAD_REQUEST)

        if need_update:
            update_address = UpdateAddress(address,
                                           data=ref_state, partial=True)
            if update_address.is_valid():
                update_address.save()
            else:
                return JsonResponse({'success': False,
                                     'message': 'Invalid data'},
                                    status=status.HTTP_400_BAD_REQUEST)
        if state_updated is False:
            return JsonResponse({'success': False,
                                 'message': 'Estado não encontrado.'},
                                status=status.HTTP_404_NOT_FOUND)

        neighbor_update = update_neighbor(neighborhood, address_id)
        if neighbor_update is False:
            return JsonResponse({'success': False,
                                 'message': 'Bairro não encontrado.'},
                                status=status.HTTP_404_NOT_FOUND)

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
    referencia = []
    try:
        number_obj = HouseNumber.objects.get(number=numbers)
        number = Address.objects.filter(number=number_obj.id,
                                        id=address_id).exists()
        if number:
            pass
        else:
            referencia.append(number_obj.id)
    except HouseNumber.DoesNotExist:
        serializer = CreateHouseNumber(data={"number": numbers})
        if serializer.is_valid():
            new_name_obj = serializer.save()
            referencia.append(new_name_obj.id)
        else:
            is_updated = False

    return is_updated, referencia


def update_state(state, address_id):
    is_errors = True
    need_update = False
    referencias = []
    try:
        state_obj = State.objects.get(state=state)
        address = Address.objects.filter(state=state_obj.id,
                                         id=address_id).exists()
        if address:
            pass
        else:
            referencias.append(state_obj.id)
            need_update = True
    except (State.DoesNotExist, Address.DoesNotExist):
        state_data = {"state": state}
        serializer = CreateState(data=state_data)
        if serializer.is_valid():
            new_state_obj = serializer.save()
            referencias.append(new_state_obj.id)
            need_update = True
        else:
            is_errors = False
    return is_errors, need_update, referencias


def update_neighbor(neighbor, address_id):
    is_updated = True
    referencias = []
    for n in neighbor:
        try:
            neigh = Neighborhood.objects.get(neighborhood=n)
            address_neigh = neighborhoodAddress.objects.filter(
                                                neighbor=neigh.id,
                                                address=address_id).exists()
            if address_neigh:
                pass
            else:
                referencias.append(neigh.id)
        except (Neighborhood.DoesNotExist, neighborhoodAddress.DoesNotExist):
            serializer = CreateNeighborhood(data={"neighborhood": n})
            if serializer.is_valid():
                new_state_obj = serializer.save()
                referencias.append(new_state_obj.id)
            else:
                is_updated = False

    for ref in referencias:
        neighborhoodAddress.objects.filter(address=address_id).delete()
        order = 1
        serializer_state = CreateNeighborAddress(
            data={
                'neighbor': ref,
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
    for street in streets:
        try:
            street_db = Street.objects.get(street=street)
            address_street = addressStreet.objects.filter(
                                                street=street_db.id,
                                                address=address_id).exists()
            if address_street:
                pass
            else:
                referencias.append(street_db.id)
        except (Street.DoesNotExist, addressStreet.DoesNotExist):
            serializer = CreateStreet(data={"street": street})
            if serializer.is_valid():
                new_state_obj = serializer.save()
                referencias.append(new_state_obj.id)
            else:
                is_updated = False

    for ref in referencias:
        addressStreet.objects.filter(address=address_id).delete()
        order = 1
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
