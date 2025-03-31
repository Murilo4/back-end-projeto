from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import Places, PlacesPhotos, PlaceCategories, PlacesComments
import os
from django.db import transaction
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['DELETE'])
def delete_place(request, placeId):
    if request.method != 'DELETE':
        return JsonResponse({'success': False,
                             'message': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                "success": False,
                "message": "Token de acesso não fornecido ou formato inválido."
            }, status=status.HTTP_401_UNAUTHORIZED)

        place_id = placeId

        place = Places.objects.get(id=place_id)

        with transaction.atomic():
            try:
                categories = PlaceCategories.objects.filter(
                    place=place_id).values_list('id', flat=True)

                for cat in categories:
                    PlaceCategories.objects.filter(id=cat).delete()

                photos = PlacesPhotos.objects.filter(
                    place_photo=place_id).values_list('id', flat=True)

                for photo in photos:
                    PlacesPhotos.objects.filter(id=photo).delete()

                comments = PlacesComments.objects.filter(
                    place_comment=place_id).values_list('id', flat=True)

                for comment in comments:
                    PlacesComments.objects.filter(id=comment).delete()
            except (PlaceCategories.DoesNotExist,
                    PlacesPhotos.DoesNotExist,
                    PlacesComments.DoesNotExist):
                pass

            place.delete()

            return JsonResponse({"success": True,
                                 "message": "Local excluido com sucesso"},
                                status=status.HTTP_200_OK)
    except Places.DoesNotExist:
        return JsonResponse({'success': False,
                             'message': 'Local não encontrado'},
                            status=status.HTTP_404_NOT_FOUND)
