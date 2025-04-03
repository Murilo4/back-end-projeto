from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import ComumDoubs
from ...serializers.doub import DoubUpdate, DoubPhotoUpdate
import os
from django.db import transaction
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['PUT'])
def update_doub(request, doubId):
    if request.method != 'PUT':
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

        doub_id = doubId

        doub = ComumDoubs.objects.get(id=doub_id)
        photo = request.data.get("photo")
        doub_req = request.data.get("doub")
        doub_answer = request.data.get("doubAnswer")

        update_doub = {
            "doub": doub_req,
            "doub_answer": doub_answer
        }
        with transaction.atomic():
            if photo:
                serializer_photo = DoubPhotoUpdate(doub,
                                                   data={"doub_photo": photo},
                                                   partial=True)
                if not serializer_photo.is_valid():
                    return JsonResponse({"success": False,
                                         "message":
                                         "Não foi possivel atualizar a foto"},
                                        status=status.HTTP_400_BAD_REQUEST)
            update_doub = DoubUpdate(doub,
                                     data=update_doub, partial=True)
            if update_doub.is_valid():
                update_doub.save()
            else:
                return JsonResponse({'success': False,
                                     'message': 'Invalid data'},
                                    status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({'success': True,
                            'message': 'Usuário atualizado com sucesso'},
                            status=status.HTTP_200_OK)

    except ComumDoubs.DoesNotExist:
        return JsonResponse({'success': False,
                             'message': 'Usuário não encontrado'},
                            status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({'success': False,
                             'message': 'Erro interno no servidor.',
                             'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
