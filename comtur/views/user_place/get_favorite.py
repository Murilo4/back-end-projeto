from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import UserPlaces
from rest_framework import exceptions
import os
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
def get_favorite(request, placeId):
    if request.method != 'POST':
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
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get('id')
    except Exception:
        return JsonResponse({
            "success": False,
            "message": "Token JWT inválido ou expirado."
        }, status=status.HTTP_401_UNAUTHORIZED)
    try:
        place_id = placeId
        if not user_id or not place_id:
            return JsonResponse({'success': False,
                                 'message':
                                'Campos obrigatórios não preenchidos'},
                                status=status.HTTP_400_BAD_REQUEST)

        exist_user_place = UserPlaces.objects.filter(user_place=user_id,
                                                     place_id=place_id
                                                     ).exists()
        if exist_user_place:
            userplace = UserPlaces.objects.get(user_place=user_id,
                                               place_id=place_id)
            if userplace.favorite is True:
                return JsonResponse({"success": True,
                                     "message": "É favorito",
                                     "favorite": True},
                                    status=status.HTTP_200_OK)
            else:
                return JsonResponse({"success": False,
                                     "message": "Não é favorito"},
                                    status=status.HTTP_400_BAD_REQUEST)
    except exceptions.ValidationError as e:
        return JsonResponse({'success': False,
                             'message': e.detail},
                            status=status.HTTP_400_BAD_REQUEST)
