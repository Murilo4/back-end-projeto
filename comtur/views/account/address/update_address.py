# from rest_framework.decorators import api_view, throttle_classes
# from django.http import JsonResponse
# from rest_framework import status
# from django.db import transaction
# from dotenv import load_dotenv
# from ....models import Address, NumberAddress, HouseNumber
# from ....serializers.address import UpdateAddress, CreateHouseNumber
# from ....serializers.address import CreateNumberAddress, State, StateAddress
# from ....serializers.address import CreateState, CreateStateAddress
# from ....throttles import DailyRateThrottle, HourlyRateThrottle
# from ....throttles import MinuteRateThrottleAnon
# import jwt
# import os

# load_dotenv()

# SECRET_KEY = os.getenv('JWT_SECRET_KEY')


# @api_view(['PUT'])
# @throttle_classes([
#     MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
# def update_address(request):
#     if request.method != 'PUT':
#         return JsonResponse({'success': False,
#                              'message': 'Invalid request method'},
#                             status=status.HTTP_400_BAD_REQUEST)
#     try:
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith('Bearer '):
#             return JsonResponse({
#                 "success": False,
#                 "message": "Token de acesso não fornecido ou formato inválido."
#             }, status=status.HTTP_401_UNAUTHORIZED)

#         token = auth_header.split(' ')[1]

#         payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#         user_id = payload.get('id')
#         address_id = request.data.get('addressId')
#         try:
#             address = Address.objects.get(id=address_id, user_address=user_id)
#         except Address.DoesNotExist:
#             return JsonResponse({'success': False,
#                                  'message': 'Endereço não encontrado.'},
#                                 status=status.HTTP_404_NOT_FOUND)

#         with transaction.atomic():
#             update_address = UpdateAddress(address,
#                                            data=request.data, partial=True)
#             if update_address.is_valid():
#                 update_address.save()
#             else:
#                 return JsonResponse({'success': False,
#                                      'message': 'Invalid data'},
#                                     status=status.HTTP_400_BAD_REQUEST)
#         numbers = request.data.get('number')
#         number_updated = update_numbers(numbers, address_id)

#         if number_updated is False:
#             return JsonResponse({'success': False,
#                                  'message':
#                                  'Erro ao atualizar o nome do endereço.'},
#                                 status=status.HTTP_400_BAD_REQUEST)

#         state = request.data.get('state')
#         state_updated = update_state(state, address_id)

#         if state_updated is False:
#             return JsonResponse({'success': False,
#                                  'message':
#                                  'Erro ao atualizar o estado do endereço.'},
#                                 status=status.HTTP_400_BAD_REQUEST)

#         return JsonResponse({'success': True,
#                             'message': 'Endereço atualizado com sucesso'},
#                             status=status.HTTP_200_OK)

#     except Address.DoesNotExist:
#         return JsonResponse({'success': False,
#                              'message': 'Endereço não encontrado'},
#                             status=status.HTTP_404_NOT_FOUND)

#     except Exception as e:
#         return JsonResponse({'success': False,
#                              'message': 'Erro interno no servidor.',
#                              'error': str(e)},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def update_numbers(numbers, address_id):
#     is_updated = True
#     number = NumberAddress.objects.get(address=address_id)

#     try:
#         number_obj = HouseNumber.objects.get(id=number.id)
#     except HouseNumber.DoesNotExist:
#         pass

#     update_number = numbers

#     if update_number != number_obj:
#         referencias = []
#         try:
#             number_obj = HouseNumber.objects.get(number=update_number)
#             referencias.append(number_obj.id)
#         except HouseNumber.DoesNotExist:
#             number_data = {"number": update_number}
#             serializer = CreateHouseNumber(data=number_data)
#             if serializer.is_valid():
#                 new_name_obj = serializer.save()
#                 referencias.append(new_name_obj.id)
#             else:
#                 is_updated = False
#     if referencias:
#         referencia = referencias.pop()
#         NumberAddress.objects.filter(address=address_id).delete()
#         serializer_user = CreateNumberAddress(
#                 data={'house_number': referencia,
#                       'address': address_id})
#         if serializer_user.is_valid(raise_exception=True):
#             serializer_user.save()
#         else:
#             is_updated = False

#     return is_updated


# def update_state(state, address_id):
#     is_updated = True
#     if isinstance(state, list):
#         full_number_from_db = " ".join(state).lower()
#         new_state = state.pop()
#     elif isinstance(state, str):
#         full_number_from_db = state.lower()
#         new_state = state
#     else:
#         return False
#     if new_state != full_number_from_db:
#         referencias = []
#         try:
#             number_obj = State.objects.get(state=new_state)
#             referencias.append(number_obj.id)
#         except State.DoesNotExist:
#             state_data = {"state": new_state}
#             serializer = CreateState(data=state_data)
#             if serializer.is_valid():
#                 new_state_obj = serializer.save()
#                 referencias.append(new_state_obj.id)
#             else:
#                 is_updated = False
#     if referencias:
#         referencia = referencias.pop()
#         StateAddress.objects.filter(address=address_id).delete()
#         serializer_state = CreateStateAddress(
#             data={
#                 'state': referencia,
#                 'address': address_id
#             }
#         )
#         if serializer_state.is_valid(raise_exception=True):
#             serializer_state.save()
#         else:
#             is_updated = False
#     return is_updated
