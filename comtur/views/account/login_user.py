from rest_framework.decorators import api_view  # , throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import NormalUser
from ...serializers.session import CreateSession
from datetime import datetime, timedelta, timezone
import re
import jwt
from django.conf import settings
# from ...throttles import DailyRateThrottle, HourlyRateThrottle
# from ...throttles import MinuteRateThrottleAnon
from ...jwt.generate_jwt import generate_jwt_session, generate_jwt
from django.db import transaction
import bcrypt


@api_view(['POST'])
# @throttle_classes([
#     MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
def login_user_with_cpf(request):
    if request.method != 'POST':
        return JsonResponse({
            "success": False,
            "message": "Invalid request method"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    cpf = request.data.get("cpf")
    cnpj = request.data.get("cnpj")
    password = request.data.get("password")
    # token_data = request.data.get('token')
    # if not token_data:
    #     return JsonResponse({"success": False,
    #                          "message": "Token is missing"},
    #                          status=status.HTTP_400_BAD_REQUEST)
    # payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    # password = payload.get('password')
    # cpf = payload.get('cpf')
    # cnpj = payload.get('cnpj')
    if not cpf and not cnpj:
        return JsonResponse({
            "success": False,
            "message": "CPF ou CNPJ é obrigatório."
        }, status=status.HTTP_400_BAD_REQUEST)

    if not password:
        return JsonResponse({
            "success": False,
            "message": "Senha é obrigatória."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        if cpf:
            numeros_cpf = re.sub(r'\D', '', cpf)
            user = NormalUser.objects.get(cpf=numeros_cpf)
        elif cnpj:
            numeros_cnpj = re.sub(r'\D', '', cnpj)
            user = NormalUser.objects.get(cnpj=numeros_cnpj)
        else:
            return JsonResponse({"sucess": False,
                                 "message": "Cpf e cnpj não localizado"},
                                status=status.HTTP_400_BAD_REQUEST)
    except NormalUser.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Usuário não encontrado."
        }, status=status.HTTP_401_UNAUTHORIZED)

    validated_password = validate_password(password, user.password)
    if not validated_password:
        return JsonResponse({
            "success": False,
            "message": "Senha incorreta."
        }, status=status.HTTP_401_UNAUTHORIZED)

    try:
        user_validaded = user.is_validated
        if user_validaded == 0:
            token = generate_jwt_(user.email)
            return JsonResponse({
                "success": False,
                "message": "Usuário não validado. Valide seu email.",
                "token": token
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        with transaction.atomic():
            refresh = generate_jwt_session(user)
            access = generate_jwt(user)

            new_session = CreateSession(data={
                'user_session': user.id,
                'session_token': refresh
            })

            if new_session.is_valid(raise_exception=True):
                new_session.save()

        return JsonResponse({
            'success': True,
            'message': 'Login realizado com sucesso.',
            'refresh': refresh,
            'access': access
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message":
            "Erro interno no servidor. Por favor, tente novamente mais tarde.",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
# @throttle_classes([
#     MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
def login_user_with_email(request):
    if request.method != 'POST':
        return JsonResponse({
            "success": False,
            "message": "Invalid request method"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    email = request.data.get('email')
    password = request.data.get("password")
    # token_data = request.data.get('token')
    # if not token_data:
    #     return JsonResponse({"success": False,
    #                          "message": "Token is missing"},
    #                          status=status.HTTP_400_BAD_REQUEST)
    # payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    # password = payload.get('password')
    # cpf = payload.get('cpf')
    # cnpj = payload.get('cnpj')
    if not email:
        return JsonResponse({
            "success": False,
            "message": "CPF ou CNPJ é obrigatório."
        }, status=status.HTTP_400_BAD_REQUEST)

    if not password:
        return JsonResponse({
            "success": False,
            "message": "Senha é obrigatória."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        if email:
            r = re.compile(r'^[\w-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')
            if r.match(email):
                user = NormalUser.objects.get(email=email)
        else:
            return JsonResponse({"sucess": False,
                                 "message": "Cpf e cnpj não localizado"},
                                status=status.HTTP_400_BAD_REQUEST)
    except NormalUser.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Usuário não encontrado."
        }, status=status.HTTP_401_UNAUTHORIZED)

    validated_password = validate_password(password, user.password)
    if not validated_password:
        return JsonResponse({
            "success": False,
            "message": "Senha incorreta."
        }, status=status.HTTP_401_UNAUTHORIZED)

    try:
        user_validaded = user.is_validated
        if user_validaded == 0:
            token = generate_jwt_(user.email)
            return JsonResponse({
                "success": False,
                "message": "Usuário não validado. Valide seu email.",
                "token": token
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        with transaction.atomic():
            refresh = generate_jwt_session(user)
            access = generate_jwt(user)

            new_session = CreateSession(data={
                'user_session': user.id,
                'session_token': refresh
            })

            if new_session.is_valid(raise_exception=True):
                new_session.save()

        return JsonResponse({
            'success': True,
            'message': 'Login realizado com sucesso.',
            'refresh': refresh,
            'access': access
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message":
            "Erro interno no servidor. Por favor, tente novamente mais tarde.",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def validate_password(password, user_password):
    if bcrypt.checkpw(password.encode('utf-8'), user_password.encode('utf-8')):
        return True
    else:
        return False


def generate_jwt_(email):
    payload = {
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=10)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token
