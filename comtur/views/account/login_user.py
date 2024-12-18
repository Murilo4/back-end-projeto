from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import NormalUser
from ...serializers.session import CreateSession
import re
from ...throttles import DailyRateThrottle, HourlyRateThrottle
from ...throttles import MinuteRateThrottleAnon
from ...jwt.generate_jwt import generate_jwt_session, generate_jwt
from django.db import transaction
import bcrypt


@api_view(['POST'])
@throttle_classes([
    MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
def login_user_with_cpf(request):
    if request.method != 'POST':
        return JsonResponse({
            "success": False,
            "message": "Invalid request method"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    cpf = request.data.get("cpf")
    cnpj = request.data.get("cnpj")
    password = request.data.get("password")

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
