from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ....models import Address, NumberAddress, StateAddress
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
                delete_number = NumberAddress.objects.get(
                    address=address)
                if delete_number:
                    delete_number.delete()
                delete_state = StateAddress.objects.get(
                    address=address)
                if delete_state:
                    delete_state.delete()
            except NumberAddress.DoesNotExist:
                pass
            except StateAddress.DoesNotExist:
                pass
            if address_to_delete:
                address_to_delete.delete()

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
