from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from ...models import PlacesRating, UserPlaces
from ...serializers.place import UpdatePlaceRating


@api_view(['PUT'])
def update_rating(request):
    if request.method != 'PUT':
        return JsonResponse({'success': False,
                             'message': 'metodo invalido'},
                            status=status.HTTP_400_BAD_REQUEST)
    user_id = request.data.get('userId')
    place_id = request.data.get('placeId')
    str_rating = request.data.get('rating', None)
    rating_id = request.data.get('ratingId', None)

    if not user_id or not place_id or not rating_id:
        return JsonResponse({'success': False,
                             'message': 'Campos obrigatórios não preenchidos'},
                            status=status.HTTP_400_BAD_REQUEST)
    rating = int(str_rating)
    if rating > 5:
        return JsonResponse({'success': False,
                             'message': 'avaliação invalida'},
                            status=status.HTTP_400_BAD_REQUEST)
    user_place = UserPlaces.objects.get(user_place=user_id,
                                        place_id=place_id)
    place_rating = PlacesRating.objects.get(place_rating=place_id,
                                            user_rating=user_place.id,
                                            id=rating_id)

    with transaction.atomic():
        if rating is not None:
            serializer = UpdatePlaceRating(place_rating,
                                           data={"rating": rating},
                                           partial=True)

            if serializer.is_valid(raise_exception=True):
                serializer.save()

                return JsonResponse({'success': True,
                                    'message':
                                     'avaliação adicionado com sucesso'},
                                    status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success': False,
                                 'message': 'avaliação invalida'},
                                status=status.HTTP_400_BAD_REQUEST)
