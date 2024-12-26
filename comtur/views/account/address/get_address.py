# from rest_framework.decorators import api_view, throttle_classes
# from django.http import JsonResponse
# from rest_framework import status
# from ....models import Address, StateAddress, State, NumberAddress, HouseNumber
# import jwt
# import os
# from ....throttles import DailyRateThrottle, HourlyRateThrottle
# from ....throttles import MinuteRateThrottleAnon
# from dotenv import load_dotenv
# load_dotenv()
# SECRET_KEY = os.getenv('JWT_SECRET_KEY')


# @api_view(['GET'])
# @throttle_classes([
#     MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
# def get_one_address(request):
#     if request.method != 'GET':
#         return JsonResponse({'success': False,
#                             'message': 'Invalid request method'},
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
#         # address_id = request.HEADERS.get('addressId')
#         address_id = request.data.get('addressId')
#         try:
#             address = Address.objects.get(id=address_id, user_address=user_id)
#         except Address.DoesNotExist:
#             return JsonResponse({'success': False,
#                                  'message': 'Endereço não encontrado.'},
#                                 status=status.HTTP_404_NOT_FOUND)
#         try:
#             state_address = StateAddress.objects.get(address=address.id)
#             state = State.objects.get(id=state_address.state)
#         except StateAddress.DoesNotExist:
#             return JsonResponse({'success': False,
#                                  'message': 'Estado não encontrado.'},
#                                 status=status.HTTP_404_NOT_FOUND)
#         except State.DoesNotExist:
#             return JsonResponse({'success': False,
#                                  'message': 'Estado não encontrado.'},
#                                 status=status.HTTP_404_NOT_FOUND)
#         try:
#             number_address = NumberAddress.objects.get(address=address.id)
#             number = HouseNumber.objects.get(id=number_address.house_number)
#         except NumberAddress.DoesNotExist:
#             return JsonResponse({'success': False,
#                                  'message': 'Número não encontrado.'},
#                                 status=status.HTTP_404_NOT_FOUND)
#         except HouseNumber.DoesNotExist:
#             return JsonResponse({'success': False,
#                                  'message': 'Número não encontrado.'},
#                                 status=status.HTTP_404_NOT_FOUND)
#         address_data = {
#             "street": address.street,
#             "state": state.state,
#             "number": number.number,
#             "neighborhood": address.neighborhood,
#             "city": address.city,
#             "postal": address.postal,
#         }
#         return JsonResponse({"success": True,
#                              "message": "Endereço retornado com sucesso",
#                              "address": address_data},
#                             status=status.HTTP_200_OK)

#     except jwt.ExpiredSignatureError:
#         return JsonResponse({'success': False,
#                             'message': 'Token expirado.'},
#                             status=status.HTTP_401_UNAUTHORIZED)
