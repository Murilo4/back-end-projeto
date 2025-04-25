from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from ...models import UserPlaces, Places
from ...serializers.place import UpdateUserPlace, CreateUserPlaceFavorite
from rest_framework import exceptions
import os
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
def set_favorite(request, slug):
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
        place = Places.objects.get(slug=slug)
        if not user_id:
            return JsonResponse({'success': False,
                                 'message':
                                'Campos obrigatórios não preenchidos'},
                                status=status.HTTP_400_BAD_REQUEST)

        exist_user_place = UserPlaces.objects.filter(user_place=user_id,
                                                     place_id=place.id
                                                     ).exists()
        with transaction.atomic():
            if exist_user_place:
                user_place = UserPlaces.objects.get(user_place=user_id,
                                                    place_id=place.id)
                favorite = True
                if user_place.favorite is True:
                    favorite = False

                serializer = UpdateUserPlace(user_place,
                                             data={'favorite': favorite},
                                             partial=True)

                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return JsonResponse({'success': True,
                                         "message":
                                        'adicionado aos favoritos'},
                                        status=status.HTTP_200_OK)
            else:
                favorite = True
                new_user_place = CreateUserPlaceFavorite(
                    data={'user_place': user_id,
                          'place': place.id,
                          'favorite': favorite})
                if new_user_place.is_valid(raise_exception=True):
                    new_user_place.save()
                    return JsonResponse({'success': True,
                                         'message':
                                        'favorito adicionado com sucesso'},
                                        status=status.HTTP_200_OK)
    except exceptions.ValidationError as e:
        return JsonResponse({'success': False,
                             'message': e.detail},
                            status=status.HTTP_400_BAD_REQUEST)
