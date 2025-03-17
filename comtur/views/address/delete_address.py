from rest_framework.decorators import api_view  # , throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import Address, addressStreet, neighborhoodAddress
from ...models import UserName, Street, Neighborhood, Names
import jwt
import os
# from ...throttles import DailyRateThrottle, HourlyRateThrottle
# from ...throttles import MinuteRateThrottle
from django.db import transaction
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['DELETE'])
def delete_address(request, token):
    if request.method != 'DELETE':
        return JsonResponse({'success': False,
                             'message': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        # Decodifica o token JWT para obter o address_id
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"],
                                   options={"verify_signature": False})
        address_id = decoded_token.get('address_id')

        # Busca o endereço para exclusão
        try:
            address_to_delete = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Endereço não encontrado.'
            }, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            try:
                address_names = addressStreet.objects.filter(
                    address=address_to_delete)
                for old_name in address_names:
                    if addressStreet.objects.filter(
                            street=old_name.street).count() == 1:
                        addressStreet.objects.get(
                                street=old_name.id).delete()
                        Street.objects.get(id=old_name.id).delete()
                    else:
                        addressStreet.objects.get(
                            street=old_name.id).delete()

                neighborhood_addresses = neighborhoodAddress.objects.filter(
                    address=address_to_delete)
                for old_neigh in neighborhood_addresses:
                    neighbor = old_neigh.neighborhood
                    if neighborhoodAddress.objects.filter(
                        neighborhood=neighbor
                         ).count() == 1:
                        neighborhoodAddress.objects.get(
                            street=old_neigh.id).delete()
                        Neighborhood.objects.get(id=old_neigh.id).delete()
                    else:
                        neighborhoodAddress.objects.get(
                            street=old_neigh.id).delete()

                # Excluindo as associações de UserName
                address_names = UserName.objects.filter(
                    address=address_to_delete)
                for old_name in address_names:
                    name = old_name.name_id
                    if UserName.objects.filter(name_id=name).count() == 1:
                        UserName.objects.get(name=old_name.id).delete()
                        Names.objects.get(id=old_name.id).delete()
                    else:
                        UserName.objects.get(name=old_name.id).delete()

            except (addressStreet.DoesNotExist,
                    neighborhoodAddress.DoesNotExist,
                    UserName.DoesNotExist):
                pass
                
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
