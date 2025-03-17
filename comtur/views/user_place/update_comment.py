from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from ...models import PlacesComments, UserPlaces
from ...serializers.place import UpdatePlaceComment


@api_view(['PUT'])
def update_comment(request):
    if request.method != 'PUT':
        return JsonResponse({'success': False,
                             'message': 'metodo invalido'},
                            status=status.HTTP_400_BAD_REQUEST)

    user_id = request.data.get('userId')
    place_id = request.data.get('placeId')
    comment = request.data.get('comment', None)
    comment_id = request.data.get('commentId', None)

    if not user_id or not place_id or not comment_id:
        return JsonResponse({'success': False,
                             'message': 'Campos obrigatórios não preenchidos'},
                            status=status.HTTP_400_BAD_REQUEST)
    user_place = UserPlaces.objects.get(user_place=user_id,
                                        place_id=place_id)
    place_comment = PlacesComments.objects.get(id=comment_id,
                                               user_comment=user_place.id,
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
