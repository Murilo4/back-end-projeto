from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from ...models import UserPlaces, PlacesRating, Places
from ...serializers.place import CreateUserPlace, UpdatePlacesUsers
from ...serializers.place import CreatePlaceRating


@api_view(['POST'])
def create_rating(request):
    if request.method != 'POST':
        return JsonResponse({'success': False,
                             'message': 'metodo invalido'},
                            status=status.HTTP_400_BAD_REQUEST)
    user_id = request.data.get('userId')
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

    exist_user_place = UserPlaces.objects.filter(user_place=user_id,
                                                 place_id=place_id).exists()
    place = Places.objects.get(id=place_id)

    get_user_place = UserPlaces.objects.get(user_place=user_id,
                                            place_id=place_id)
    exist_rating = PlacesRating.objects.filter(place_rating=place_id,
                                               user_rating=get_user_place.id
                                               ).exists()
    if exist_rating:
        return JsonResponse({'success': False,
                             'message': 'Você já avaliou esse lugar'},
                            status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        if rating is not None:
            if exist_user_place:
                user_place = UserPlaces.objects.get(user_place=user_id,
                                                    place_id=place_id)
                serializer = CreatePlaceRating(
                    data={"place_rating": place_id,
                          "rating": rating,
                          "user_rating": user_place.id})
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

                    return JsonResponse({'success': True,
                                        'message':
                                         'avaliação adicionado com sucesso'},
                                        status=status.HTTP_200_OK)
                else:
                    return JsonResponse({'success': False,
                                        'message': 'avaliação invalida'},
                                        status=status.HTTP_400_BAD_REQUEST)
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

                            return JsonResponse({
                                'success': True,
                                'message':
                                'avaliação adicionado com sucesso'},
                                status=status.HTTP_200_OK)
            return JsonResponse({'success': True,
                                'message':
                                 'avaliação criado com sucesso'},
                                status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success': False,
                                 'message': 'avaliação invalido'},
                                status=status.HTTP_400_BAD_REQUEST)
