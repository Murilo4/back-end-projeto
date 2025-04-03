from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import ComumDoubs
import jwt
import os
from django.db import transaction
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ADDRESS_API_URL = os.getenv('ADDRESS_API_URL')


@api_view(['DELETE'])
def delete_doub(request, doubId):
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
        doubid = doubId

        with transaction.atomic():
            doub_to_dlt = ComumDoubs.objects.get(id=doubid)
            doub_to_dlt.delete()
            if not doub_to_dlt:
                return JsonResponse({"sucess": False,
                                     "message":
                                     "Não foi possivel deletar a pergunta"},
                                    status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({'success': True,
                             'message': 'pergunta deletada com sucesso!'},
                            status=status.HTTP_200_OK)

    except jwt.ExpiredSignatureError:
        return JsonResponse({'success': False,
                             'message': 'Token expirado.'},
                            status=status.HTTP_401_UNAUTHORIZED)

    except jwt.InvalidTokenError:
        return JsonResponse({'success': False,
                             'message': 'Token inválido.'},
                            status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro interno no servidor.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
