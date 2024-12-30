from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ....models import Address, addressStreet, neighborhoodAddress
from ....models import UserName
import jwt
import os
from ....throttles import DailyRateThrottle, HourlyRateThrottle
from ....throttles import MinuteRateThrottle
from django.db import transaction
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['DELETE'])
@throttle_classes([MinuteRateThrottle, HourlyRateThrottle, DailyRateThrottle])
def delete_address(request):
    if request.method != 'DELETE':
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

        address = request.data.get('addressId')
        try:
            address_to_delete = Address.objects.get(id=address)
        except Address.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Endereço não encontrado.'
            }, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            try:
                address_name = addressStreet.objects.filter(address=address)
                for old_name in address_name:
                    name = old_name.street
                    if addressStreet.objects.filter(
                                                    street=name).count() == 1:
                        old_name.delete()
                        name.delete()
                    else:
                        old_name.delete()

                # Handle deletion for neighborhoodAddress
                neighborhood_addresses = neighborhoodAddress.objects.filter(
                    address=address)
                for old_neigh in neighborhood_addresses:
                    neighbor = old_neigh.neighborhood
                    if neighborhoodAddress.objects.filter(
                                                         neighborhood=neighbor
                                                         ).count() == 1:
                        old_neigh.delete()
                        neighbor.delete()
                    else:
                        old_neigh.delete()

                address_name = UserName.objects.filter(address=address)
                for old_name in address_name:
                    name = old_name.name_id
                    if UserName.objects.filter(
                                                name_id=name).count() == 1:
                        old_name.delete()
                        name.delete()
                    else:
                        old_name.delete()
                if address_to_delete:
                    address_to_delete.delete()

            except (addressStreet.DoesNotExist,
                    neighborhoodAddress.DoesNotExist):
                pass
        return JsonResponse({'success': True,
                             'message': 'Endereço deletado com sucesso!'},
                            status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError:
        return JsonResponse({'success': False,
                             'message': 'Token expirado.'},
                            status=status.HTTP_401_UNAUTHORIZED)

    except jwt.InvalidTokenError:
        return JsonResponse({'success': False,
                             'message': 'Token inválido.'},
                            status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro interno no servidor.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
