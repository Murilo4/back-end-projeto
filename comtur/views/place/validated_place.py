from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import NormalUser, Places
from ...serializers.place import UpdateValidatedPlace
import os
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
def validate_place(request, slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'},
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

        user = NormalUser.objects.get(id=user_id)
        if user.is_staff == 0:
            return JsonResponse({
                "success": False,
                "message": "Usuário não autorizado."
            }, status=status.HTTP_403_FORBIDDEN)
    except jwt.ExpiredSignatureError:
        return JsonResponse({
            "success": False,
            "message": "Token JWT expirado."
        }, status=status.HTTP_401_UNAUTHORIZED)

    try:
        place = Places.objects.get(slug=slug)
    except Places.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Local não encontrado."
        }, status=status.HTTP_404_NOT_FOUND)

    update_place = UpdateValidatedPlace(place,
                                        data={"is_place_valid": 1},
                                        partial=True)
    if update_place.is_valid():
        update_place.save()
        return JsonResponse({"success": True,
                             "message": "Local validado com sucesso."},
                            status=status.HTTP_200_OK)
    else:
        return JsonResponse({"success": False,
                             "message": "Erro ao validar o local."},
                            status=status.HTTP_400_BAD_REQUEST)
