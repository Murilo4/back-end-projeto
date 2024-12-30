from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ....models import Address, neighborhoodAddress, City, HouseNumber, State
from ....models import addressStreet, Neighborhood, Street, UserName, Names
import jwt
import os
from ....throttles import DailyRateThrottle, HourlyRateThrottle
from ....throttles import MinuteRateThrottleAnon
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
@throttle_classes([
    MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
def get_one_address(request):
    if request.method != 'GET':
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
        # address_id = request.HEADERS.get('addressId')
        address_id = request.data.get('addressId')
        try:
            address = Address.objects.get(id=address_id, user_address=user_id)
        except Address.DoesNotExist:
            return JsonResponse({'success': False,
                                 'message': 'Endereço não encontrado.'},
                                status=status.HTTP_404_NOT_FOUND)
        try:
            neighbor_address = neighborhoodAddress.objects.filter(
                address=address.id).order_by('neighbor_order')
            new_neighbor = []
            for name in neighbor_address:
                try:
                    name_obj = Neighborhood.objects.get(
                        id=name.neighborhood.id)
                    new_neighbor.append(name_obj.neighborhood)
                except Neighborhood.DoesNotExist:
                    continue
            full_neighbor_formated = " ".join(new_neighbor)

        except (neighborhoodAddress.DoesNotExist, Neighborhood.DoesNotExist):
            return JsonResponse({'success': False,
                                 'message': 'Bairro não encontrado.'},
                                status=status.HTTP_404_NOT_FOUND)
        try:
            name_address = addressStreet.objects.filter(
                address=address.id).order_by('street_order')
            full_name = []
            for name in name_address:
                try:
                    name_obj = Street.objects.get(
                        id=name.street.id)
                    full_name.append(name_obj.street)
                except Street.DoesNotExist:
                    continue
            full_street_formated = " ".join(full_name)
        except (Street.DoesNotExist, addressStreet.DoesNotExist):
            return JsonResponse({'success': False,
                                 'message': 'Rua não encontrado.'},
                                status=status.HTTP_404_NOT_FOUND)

        try:
            name_address = UserName.objects.filter(
                address=address.id).order_by('create_order')
            full_name = []
            for name in name_address:
                try:
                    name_obj = Names.objects.get(
                        id=name.name_id)
                    full_name.append(name_obj.name)
                except Names.DoesNotExist:
                    continue

            full_name_address = " ".join(full_name)
        except (Names.DoesNotExist, UserName.DoesNotExist):
            return JsonResponse({'success': False,
                                 'message': 'Nome não encontrado.'},
                                status=status.HTTP_404_NOT_FOUND)

        try:
            city = City.objects.get(id=address.city.id)
            number = HouseNumber.objects.get(id=address.number.id)
            state = State.objects.get(id=address.state.id)
        except (City.DoesNotExist, HouseNumber.DoesNotExist):
            return JsonResponse({'success': False,
                                 'message':
                                 'Não foi possivel retornar o endereço'},
                                status=status.HTTP_404_NOT_FOUND)
        address_data = {
            'type': address.address_type,
            'name': full_name_address,
            "street": full_street_formated,
            "state": state.state,
            "number": number.number,
            "neighborhood": full_neighbor_formated,
            "city": city.city,
            "postal": address.postal,
        }
        return JsonResponse({"success": True,
                             "message": "Endereço retornado com sucesso",
                             "address": address_data},
                            status=status.HTTP_200_OK)

    except jwt.ExpiredSignatureError:
        return JsonResponse({'success': False,
                            'message': 'Token expirado.'},
                            status=status.HTTP_401_UNAUTHORIZED)
