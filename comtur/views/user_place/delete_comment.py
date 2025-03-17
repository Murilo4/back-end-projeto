from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.db import transaction
from ...models import PlacesComments, UserPlaces


@api_view(['DELETE'])
def delete_comment(request):
    if request.method != 'DELETE':
        return JsonResponse({'success': False,
                             'message': 'metodo invalido'},
                            status=status.HTTP_400_BAD_REQUEST)

    user_id = request.data.get('userId')
    place_id = request.data.get('placeId')
    comment_id = request.data.get('commentId', None)

    if not user_id or not place_id or not comment_id:
        return JsonResponse({'success': False,
                             'message': 'Campos obrigatórios não preenchidos'},
                            status=status.HTTP_400_BAD_REQUEST)
    user_place = UserPlaces.objects.get(user_place=user_id,
                                        place_id=place_id)

    with transaction.atomic():
        if comment_id is not None:
            try:
                place_comment = PlacesComments.objects.get(
                                                id=comment_id,
                                                user_comment=user_place.id,
                                                place_comment=place_id)
                place_comment.delete()
                return JsonResponse({'success': True,
                                    'message':
                                     'comentario deletado com sucesso'},
                                    status=status.HTTP_200_OK)
            except PlacesComments.DoesNotExist:
                return JsonResponse({'success': False,
                                     'message': 'comentario não existe'},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'success': False,
                                 'message': 'comment invalido'},
                                status=status.HTTP_400_BAD_REQUEST)
