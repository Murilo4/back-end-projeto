from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ..models import NormalUser
from ..serializers.session import CreateSession
import re
from ..jwt.generate_jwt import generate_jwt_session, generate_jwt
from django.db import transaction

import bcrypt


@api_view(['POST'])
def login_user_with_cpf(request):
    if request.method != 'POST':
        return JsonResponse({"sucess": False,
                             "message": "Invalid request method"},
                            status=status.HTTP_400_BAD_REQUEST)

    cpf = request.data.get("cpf") or None
    cnpj = request.data.get("cnpj") or None
    if cpf is None and cnpj is None:
        return JsonResponse({"sucess": False,
                             "message": "Nenhum cpf ou cnpj localizado"},
                            status=status.HTTP_400_BAD_REQUEST)

    password = request.data.get("password")
    if password is None:
        return JsonResponse({"sucess": False,
                             "message": "Password is required"},
                            status=status.HTTP_400_BAD_REQUEST)

    if cpf:
        numeros_cpf = re.sub(r'\D', '', cpf)
        user = NormalUser.objects.get(cpf=numeros_cpf)
        print(user)
        validated_password = validate_password(password, user.password)

        if validated_password:
            with transaction.atomic():
                refresh = generate_jwt_session(user)
                access = generate_jwt(user)

                new_session = CreateSession(data={'user_session': user.id,
                                                  'session_token': refresh})

                if new_session.is_valid(raise_exception=True):
                    new_session.save()
                    JsonResponse({'success': True,
                                  'message':
                                  'Login realizado com sucesso',
                                  'refresh': refresh,
                                  'access': access})
        return JsonResponse({"error": "deu ruim"})
    return JsonResponse({'error': 'Usuário ou senha incorretos.'}, status=401)


def validate_password(password, user_password):
    if bcrypt.checkpw(password.encode('utf-8'), user_password.encode('utf-8')):
        return True
    else:
        return False
