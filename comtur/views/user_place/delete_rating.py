from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from ...models import PlacesRating, UserPlaces


@api_view(['DELETE'])
def delete_rating(request):
    if request.method != 'DELETE':
        return JsonResponse({'success': False,
                             'message': 'metodo invalido'},
                            status=status.HTTP_400_BAD_REQUEST)
    user_id = request.data.get('userId')
    place_id = request.data.get('placeId')
    rating_id = request.data.get('ratingId', None)

    if not user_id or not place_id or not rating_id:
        return JsonResponse({'success': False,
                             'message': 'Campos obrigatórios não preenchidos'},
                            status=status.HTTP_400_BAD_REQUEST)
    user_place = UserPlaces.objects.get(user_place=user_id,
                                        place_id=place_id)
    place_rating = PlacesRating.objects.get(place_rating=place_id,
                                            user_rating=user_place.id,
                                            id=rating_id)

    with transaction.atomic():
        if rating_id is not None:
            try:
                place_rating = PlacesRating.objects.get(
                                            place_rating=place_id,
                                            user_rating=user_place.id,
                                            id=rating_id)
                place_rating.delete()
                return JsonResponse({'success': True,
                                    'message':
                                     'avaliação deletado com sucesso'},
                                    status=status.HTTP_200_OK)

            except PlacesRating.DoesNotExist:
                return JsonResponse({'success': False,
                                     'message': 'Rating não encontrado'},
                                    status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse({'success': False,
                                 'message': 'avaliação invalida'},
                                status=status.HTTP_400_BAD_REQUEST)
