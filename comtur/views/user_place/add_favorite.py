from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from ...models import UserPlaces
from ...serializers.place import UpdateUserPlace, CreateUserPlaceFavorite
from rest_framework import exceptions


@api_view(['POST'])
def set_favorite(request):
    if request.method != 'POST':
        return JsonResponse({'success': False,
                             'message': 'metodo invalido'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user_id = request.data.get('userId')
        place_id = request.data.get('placeId')
        entrance_favorite = request.data.get('favorite', None)
        if not user_id or not place_id:
            return JsonResponse({'success': False,
                                 'message':
                                'Campos obrigatórios não preenchidos'},
                                status=status.HTTP_400_BAD_REQUEST)
        if not entrance_favorite:
            return JsonResponse({'success': False,
                                 'message': 'favorito invalido'},
                                status=status.HTTP_400_BAD_REQUEST)
        favorite = bool(entrance_favorite)
        exist_user_place = UserPlaces.objects.filter(user_place=user_id,
                                                     place_id=place_id
                                                     ).exists()
        with transaction.atomic():
            if exist_user_place:
                user_place = UserPlaces.objects.get(user_place=user_id,
                                                    place_id=place_id)
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
                new_user_place = CreateUserPlaceFavorite(
                    data={'user_place': user_id,
                          'place': place_id,
                          'favorite': favorite})
                if new_user_place.is_valid(raise_exception=True):
                    serializer.save()
                    return JsonResponse({'success': True,
                                         'message':
                                        'favorito adicionado com sucesso'},
                                        status=status.HTTP_200_OK)
    except exceptions.ValidationError as e:
        return JsonResponse({'success': False,
                             'message': e.detail},
                            status=status.HTTP_400_BAD_REQUEST)
