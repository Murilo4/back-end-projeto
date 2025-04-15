from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import UserPlaces, PlacesRating, Places
import os
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_rating(request, slug):
    if request.method != 'GET':
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

    if not user_id:
        return JsonResponse({'success': False,
                             'message': 'Campos obrigatórios não preenchidos'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        place = Places.objects.get(slug=slug)
        user_place = UserPlaces.objects.get(user_place=user_id,
                                            place_id=place.id)
        UserPlaces.objects.get(user_place=user_id,
                               place_id=place.id)
    except (UserPlaces.DoesNotExist, Places.DoesNotExist):
        return JsonResponse({"sucess": False,
                             "message": "Local não existe"},
                            status=status.HTTP_400_BAD_REQUEST)
    except UserPlaces.DoesNotExist:
        pass

        user_rating = None
    try:
        user_rating = PlacesRating.objects.get(
            user_place=user_place.id)
        place_rating = {
            "rating": user_rating.rating
        }

        return JsonResponse({"success": True,
                             "message": "Avaliação encontrada",
                             "rating": place_rating},
                            status=status.HTTP_200_OK)

    except PlacesRating.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "avaliação não existe"},
                            status=status.HTTP_400_BAD_REQUEST)
