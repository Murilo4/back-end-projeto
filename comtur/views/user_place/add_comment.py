from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from ...models import UserPlaces, PlacesComments, Places
from ...serializers.place import CreatePlaceComment
from ...serializers.place import UpdatePlacesUsers, CreateUserPlace
import os
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
def create_comment(request, placeId):
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
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get('id')
    try:
        place_id = placeId
        comment = request.data.get('comment', None)
        if not user_id or not place_id:
            return JsonResponse({'success': False,
                                'message':
                                 'Campos obrigatórios não preenchidos'},
                                status=status.HTTP_400_BAD_REQUEST)

        exist_user_place = UserPlaces.objects.filter(user_place=user_id,
                                                     place_id=place_id
                                                     ).exists()
        place = Places.objects.get(id=place_id)
    except (Places.DoesNotExist):
        return JsonResponse({"success": False,
                             "message": "Local não localizado"},
                            status=status.HTTP_400_BAD_REQUEST)
    with transaction.atomic():
        if comment is not None:
            if exist_user_place:
                user_place = UserPlaces.objects.get(user_place=user_id,
                                                    place_id=place_id)
                serializer = CreatePlaceComment(
                    data={"place_comment": place_id,
                          "comment": comment,
                          "user_comment": user_place.id})
                if not serializer.is_valid(raise_exception=True):
                    return JsonResponse({"success": False,
                                         "message":
                                        "Erro ao salvar comentario"},
                                        status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                comments_number = PlacesComments.objects.filter(
                    place_comment=place_id).count()
                update_place = UpdatePlacesUsers(
                    place,
                    data={
                        'comments_number': comments_number},
                    partial=True)
                if not update_place.is_valid(raise_exception=True):
                    return JsonResponse({"success": False,
                                         "message":
                                        "Erro ao salvar comentario"},
                                        status=status.HTTP_400_BAD_REQUEST)
                update_place.save()

                return JsonResponse({'success': True,
                                    'message':
                                     'comentario adicionado com sucesso'},
                                    status=status.HTTP_200_OK)

            else:
                new_user_place = CreateUserPlace(data={
                    'user_place': user_id,
                    'place': place_id})
                if not new_user_place.is_valid(raise_exception=True):
                    return JsonResponse({"success": False,
                                         "message":
                                         "erro ao criar comentario"},
                                        status=status.HTTP_400_BAD_REQUEST)
                new_user_place.save()
                get_user_place = UserPlaces.objects.get(user_place=user_id,
                                                        place_id=place_id)
                serializer = CreatePlaceComment(
                    data={"place_comment": place_id,
                          "comment": comment,
                          "user_comment": get_user_place.id})
                if not serializer.is_valid(raise_exception=True):
                    return JsonResponse({"success": False,
                                         "message":
                                        "Erro ao criar comentario"},
                                        status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                comments_number = PlacesComments.objects.filter(
                    place_comment=place_id).count()
                update_place = UpdatePlacesUsers(
                    place,
                    data={
                        'comments_number': comments_number},
                    partial=True)
                if not update_place.is_valid(raise_exception=True):
                    return JsonResponse({"success": False,
                                         "message":
                                         "erro ao criar comentario"},
                                        status=status.HTTP_400_BAD_REQUEST)
                update_place.save()

                return JsonResponse({
                    'success': True,
                    'message':
                    'comentario adicionado com sucesso'},
                    status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success': False,
                                 'message': 'comentario invalido'},
                                status=status.HTTP_400_BAD_REQUEST)
