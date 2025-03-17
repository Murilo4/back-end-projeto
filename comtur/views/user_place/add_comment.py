from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from ...models import UserPlaces, PlacesComments, Places
from ...serializers.place import CreatePlaceComment
from ...serializers.place import UpdatePlacesUsers, CreateUserPlace


@api_view(['POST'])
def create_comment(request):
    if request.method != 'POST':
        return JsonResponse({'success': False,
                             'message': 'metodo invalido'},
                            status=status.HTTP_400_BAD_REQUEST)

    user_id = request.data.get('userId')
    place_id = request.data.get('placeId')
    comment = request.data.get('comment', None)

    if not user_id or not place_id:
        return JsonResponse({'success': False,
                             'message': 'Campos obrigatórios não preenchidos'},
                            status=status.HTTP_400_BAD_REQUEST)

    exist_user_place = UserPlaces.objects.filter(user_place=user_id,
                                                 place_id=place_id).exists()
    place = Places.objects.get(id=place_id)
    with transaction.atomic():
        if comment is not None:
            if exist_user_place:
                user_place = UserPlaces.objects.get(user_place=user_id,
                                                    place_id=place_id)
                serializer = CreatePlaceComment(
                    data={"place_comment": place_id,
                          "comment": comment,
                          "user_comment": user_place.id})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()

                comments_number = PlacesComments.objects.filter(
                    place_comment=place_id).count()
                update_place = UpdatePlacesUsers(
                        place,
                        data={
                            'comments_number': comments_number},
                        partial=True)
                if update_place.is_valid(raise_exception=True):
                    update_place.save()

                    return JsonResponse({'success': True,
                                        'message':
                                         'comentario adicionado com sucesso'},
                                        status=status.HTTP_200_OK)
                else:
                    return JsonResponse({'success': False,
                                        'message': 'comment invalido'},
                                        status=status.HTTP_400_BAD_REQUEST)
            else:
                new_user_place = CreateUserPlace(data={
                                                'user_place': user_id,
                                                'place': place_id})
                if new_user_place.is_valid(raise_exception=True):
                    new_user_place.save()
                    get_user_place = UserPlaces.objects.get(user_place=user_id,
                                                            place_id=place_id)
                    serializer = CreatePlaceComment(
                            data={"place_comment": place_id,
                                  "comment": comment,
                                  "user_comment": get_user_place.id})
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        comments_number = PlacesComments.objects.filter(
                            place_comment=place_id).count()
                        update_place = UpdatePlacesUsers(
                                    place,
                                    data={
                                        'comments_number': comments_number},
                                    partial=True)
                        if update_place.is_valid(raise_exception=True):
                            update_place.save()

                            return JsonResponse({
                                'success': True,
                                'message':
                                'comentario adicionado com sucesso'},
                                status=status.HTTP_200_OK)
            return JsonResponse({'success': True,
                                'message':
                                 'comentario criado com sucesso'},
                                status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success': False,
                                 'message': 'comentario invalido'},
                                status=status.HTTP_400_BAD_REQUEST)
