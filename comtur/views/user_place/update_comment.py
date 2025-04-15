from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from ...models import PlacesComments, UserPlaces
from ...serializers.place import UpdatePlaceComment
import os
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['PUT'])
def update_comment(request, placeId):
    if request.method != 'PUT':
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
    comment = request.data.get('comment', None)

    if not user_id or not place_id:
        return JsonResponse({'success': False,
                             'message': 'Campos obrigatórios não preenchidos'},
                            status=status.HTTP_400_BAD_REQUEST)
    user_place = UserPlaces.objects.get(user_place=user_id,
                                        place_id=place_id)
    place_comment = PlacesComments.objects.get(user_comment=user_place.id,
                                               place_comment=place_id)

    with transaction.atomic():
        if comment is not None:
            serializer = UpdatePlaceComment(place_comment,
                                            data={"comment": comment},
                                            partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return JsonResponse({'success': True,
                                'message':
                                 'comentario atualizado com sucesso'},
                                status=status.HTTP_200_OK)
        else:
            return JsonResponse({'success': False,
                                 'message': 'comment invalido'},
                                status=status.HTTP_400_BAD_REQUEST)
