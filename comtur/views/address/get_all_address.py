from rest_framework.decorators import api_view  # , throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import Address, neighborhoodAddress, City, HouseNumber, State
from ...models import addressStreet, Neighborhood, Street, UserName, Names
import jwt
import os 
from datetime import datetime, timedelta
# from ...throttles import DailyRateThrottle, HourlyRateThrottle
# from ...throttles import MinuteRateThrottleAnon
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_all_address(request):
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

        try:
            # Alteração: agora 'address' é um queryset com todos os endereços do usuário
            address_list = Address.objects.filter(user_address=user_id)
        except Address.DoesNotExist:
            return JsonResponse({'success': False, 
                                 'message': 'Endereços não encontrados.'}, 
                                 status=status.HTTP_404_NOT_FOUND)
        
        # Se não houver endereços, retornamos uma resposta vazia
        if not address_list:
            return JsonResponse({'success': False,
                                 'message': 'O usuário não possui endereços cadastrados.'}, 
                                status=status.HTTP_404_NOT_FOUND)
        
        addresses_data = []  # Lista para armazenar todos os endereços

        for add in address_list:
            try:
                # Gerar um token JWT com o ID do endereço (encriptado)
                address_id_token = jwt.encode({
                    'address_id': add.id,
                    'exp': datetime.now() + timedelta(hours=1)},
                    SECRET_KEY, algorithm='HS256')

                # Buscando os bairros relacionados a este endereço
                neighbor_address = neighborhoodAddress.objects.filter(
                    address=add.id).order_by('neighbor_order')
                new_neighbor = []
                for name in neighbor_address:
                    try:
                        name_obj = Neighborhood.objects.get(id=name.neighborhood.id)
                        new_neighbor.append(name_obj.neighborhood)
                    except Neighborhood.DoesNotExist:
                        continue
                full_neighbor_formated = " ".join(new_neighbor)

                try:
                    # Buscando as ruas relacionadas a este endereço
                    name_address = addressStreet.objects.filter(address=add.id).order_by('street_order')
                    full_name = []
                    for name in name_address:
                        try:
                            name_obj = Street.objects.get(id=name.street.id)
                            full_name.append(name_obj.street)
                        except Street.DoesNotExist:
                            continue
                    full_street_formated = " ".join(full_name)
                except (Street.DoesNotExist, addressStreet.DoesNotExist):
                    return JsonResponse({'success': False, 'message': 'Rua não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

                try:
                    # Buscando os nomes relacionados ao endereço
                    name_address = UserName.objects.filter(address=add.id).order_by('create_order')
                    full_name = []
                    for name in name_address:
                        try:
                            name_obj = Names.objects.get(id=name.name_id)
                            full_name.append(name_obj.name)
                        except Names.DoesNotExist:
                            continue

                    full_name_address = " ".join(full_name)
                except (Names.DoesNotExist, UserName.DoesNotExist):
                    return JsonResponse({'success': False, 'message': 'Nome não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

                try:
                    # Buscando a cidade, número e estado relacionados ao endereço
                    city = City.objects.get(id=add.city.id)
                    number = HouseNumber.objects.get(id=add.number.id)
                    state = State.objects.get(id=add.state.id)
                except (City.DoesNotExist, HouseNumber.DoesNotExist):
                    return JsonResponse({'success': False, 'message': 'Não foi possível retornar o endereço'}, status=status.HTTP_404_NOT_FOUND)

                # Adicionando os dados do endereço na lista
                address_data = {
                    'addressType': add.address_type,
                    'addressName': full_name_address,
                    "street": full_street_formated,
                    "state": state.state,
                    "number": number.number,
                    "neighborhood": full_neighbor_formated,
                    "city": city.city,
                    "cep": add.postal,
                    "address_id_token": address_id_token  # Enviar o ID encriptado
                }

                # Adiciona o endereço à lista de endereços
                addresses_data.append(address_data)

            except (neighborhoodAddress.DoesNotExist, Neighborhood.DoesNotExist):
                return JsonResponse({'success': False, 'message': 'Bairro não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # Retorna todos os endereços encontrados com os IDs encriptados
        return JsonResponse({
            "success": True,
            "message": "Endereços retornados com sucesso",
            "addresses": addresses_data
        }, status=status.HTTP_200_OK)

    except jwt.ExpiredSignatureError:
        return JsonResponse({'success': False, 'message': 'Token expirado.'}, status=status.HTTP_401_UNAUTHORIZED)