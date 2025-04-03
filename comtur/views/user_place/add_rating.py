from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from ...models import UserPlaces, PlacesRating, Places
from ...serializers.place import CreateUserPlace, UpdatePlacesUsers
from ...serializers.place import CreatePlaceRating, UpdateMediumRating
import threading
import os
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
def create_rating(request):
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
    place_id = request.data.get('placeId')
    str_rating = request.data.get('rating', None)

    if not user_id or not place_id:
        return JsonResponse({'success': False,
                             'message': 'Campos obrigatórios não preenchidos'},
                            status=status.HTTP_400_BAD_REQUEST)
    rating = int(str_rating)
    if rating > 5:
        return JsonResponse({'success': False,
                             'message': 'avaliação invalida'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user_place = UserPlaces.objects.get(user_place=user_id,
                                            place_id=place_id)
        place = Places.objects.get(id=place_id)

        get_user_place = UserPlaces.objects.get(user_place=user_id,
                                                place_id=place_id)
    except Places.DoesNotExist:
        return JsonResponse({"sucess": False,
                             "message": "Local não existe"},
                            status=status.HTTP_400_BAD_REQUEST)
    except UserPlaces.DoesNotExist:
        pass

    with transaction.atomic():
        if rating is not None:
            user_rating = PlacesRating.objects.get(
                            user_place=user_place.id)
            if user_rating:
                add_rating = False
            else:
                add_rating = True

            if user_place:
                serializer = CreatePlaceRating(
                    data={"place_rating": place_id,
                          "rating": rating,
                          "user_place": user_place.id})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                else:
                    return JsonResponse({'success': False,
                                        'message': 'avaliação invalida'},
                                        status=status.HTTP_400_BAD_REQUEST)

                if not user_rating:
                    rating_number = PlacesRating.objects.filter(
                        place_rating=place_id).count()
                    update_place = UpdatePlacesUsers(
                            place,
                            data={
                                'rating_number': rating_number + 1},
                            partial=True)
                    if update_place.is_valid(raise_exception=True):
                        update_place.save()

                return JsonResponse({'success': True,
                                    'message':
                                     'avaliação adicionado com sucesso'},
                                    status=status.HTTP_200_OK)
            else:
                new_user_place = CreateUserPlace(data={
                                                'user_place': user_id,
                                                'place': place_id})
                if new_user_place.is_valid(raise_exception=True):
                    new_user_place.save()
                    get_user_place = UserPlaces.objects.get(user_place=user_id,
                                                            place_id=place_id)
                    serializer = CreatePlaceRating(
                            data={"place_rating": place_id,
                                  "rating": rating,
                                  "user_rating": get_user_place.id})
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        rating_number = PlacesRating.objects.filter(
                            place_rating=place_id).count()
                        update_place = UpdatePlacesUsers(
                                    place,
                                    data={
                                        'rating_number': rating_number},
                                    partial=True)
                        if update_place.is_valid(raise_exception=True):
                            update_place.save()
            threading.Thread(
                        target=update_place_rating, args=(
                            rating, place_id, add_rating)).start()

            return JsonResponse({'success': True,
                                'message':
                                 'avaliação criado com sucesso'},
                                status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success': False,
                                 'message': 'avaliação invalido'},
                                status=status.HTTP_400_BAD_REQUEST)


def update_place_rating(rating, place_id, add_rating):
    try:
        place = Places.objects.get(id=place_id)
    except Places.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Local não localizado"},
                            status=status.HTTP_400_BAD_REQUEST)

    place_rating = PlacesRating.objects.filter(place_rating=place_id)
    value = 0
    for place_rate in place_rating:
        value += place_rate.rating
    if place.rating_number == 0:
        return JsonResponse({"success": False,
                             "message": "não é possivel adicionar a media"},
                            status=status.HTTP_400_BAD_REQUEST)
    if add_rating is True:
        place_rating = (value + rating) / place.rating_number
    else:
        place_rating = value / place.rating_number

    rating_update = UpdateMediumRating(place,
                                       data={"medium_rating": place_rating},
                                       partial=True)
    if not rating_update.is_valid():
        return JsonResponse({"success": False,
                             "message":
                             "Não foi possivel atualizar as avaliações"},
                            status=status.HTTP_400_BAD_REQUEST)
    rating_update.save()

    return JsonResponse({"success": True,
                         "message": "Avaliação adicionada com sucesso"},
                        status=status.HTTP_201_CREATED)
