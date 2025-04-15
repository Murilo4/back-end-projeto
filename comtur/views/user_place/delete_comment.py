from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from ...models import PlacesComments, UserPlaces
import os
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['DELETE'])
def delete_comment(request, placeId):
    if request.method != 'DELETE':
        return JsonResponse({'success': False,
                             'message': 'metodo invalido'},
                            status=status.HTTP_400_BAD_REQUEST)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({
            "success": False,
            "message": "Token de acesso não fornecido ou formato inválido."
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get('id')
    place_id = placeId

    if not user_id or not place_id:
        return JsonResponse({'success': False,
                             'message': 'Campos obrigatórios não preenchidos'},
                            status=status.HTTP_400_BAD_REQUEST)
    user_place = UserPlaces.objects.get(user_place=user_id,
                                        place_id=place_id)

    with transaction.atomic():
        try:
            place_comment = PlacesComments.objects.get(
                                            user_comment=user_place.id,
                                            place_comment=place_id)
            place_comment.delete()
            return JsonResponse({'success': True,
                                'message':
                                 'comentario deletado com sucesso'},
                                status=status.HTTP_200_OK)
        except PlacesComments.DoesNotExist:
            return JsonResponse({'success': False,
                                 'message': 'comentario não existe'},
                                status=status.HTTP_400_BAD_REQUEST)
