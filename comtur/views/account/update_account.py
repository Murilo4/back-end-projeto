from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import Names, NormalUser, UserName
from ...serializers.Names import CreateNames, CreateUserName
from ...serializers.NormalUser import UpdateNormalUser
import jwt
import os
from ...throttles import DailyRateThrottle, HourlyRateThrottle
from ...throttles import MinuteRateThrottleAnon
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import transaction
from .user_creation import validate_cnpj, validate_cpf, validate_phoneNumber
from .user_creation import validate_useremail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['PUT'])
@throttle_classes([MinuteRateThrottleAnon,
                   HourlyRateThrottle, DailyRateThrottle])
def update_user(request):
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

        token = auth_header.split(' ')[1]

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get('id')

        user = NormalUser.objects.get(id=user_id)
        phone = request.data.get('phone', None)
        if phone:
            validate = validate_phoneNumber(phone)
            if not validate:
                return JsonResponse({"success": False,
                                    "message": "Número de telefone inválido."
                                     }, status=status.HTTP_400_BAD_REQUEST)

        cpf = request.data.get('cpf', None)
        if cpf:
            validate = validate_cpf(cpf)
            if not validate:
                return JsonResponse({"success": False,
                                     "message": "CPF inválido."
                                     }, status=status.HTTP_400_BAD_REQUEST)
        cnpj = request.data.get('cnpj', None)
        if cnpj:
            validate = validate_cnpj(cnpj)
            if not validate:
                return JsonResponse({"success": False,
                                    "message": "CNPJ inválido."},
                                    status=status.HTTP_400_BAD_REQUEST)
        email = request.data.get('email', None)
        if email:
            validate = validate_useremail(email)
            if not validate:
                return JsonResponse({"success": False,
                                     "message": "E-mail inválido."
                                     }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            update_user = UpdateNormalUser(user,
                                           data=request.data, partial=True)
            if update_user.is_valid():
                update_user.save()
            else:
                return JsonResponse({'success': False,
                                     'message': 'Invalid data'},
                                    status=status.HTTP_400_BAD_REQUEST)
            username_list = UserName.objects.filter(
                user_id=user.id).order_by('create_order')

            names = []
            for username in username_list:
                try:
                    name_obj = Names.objects.get(id=username.name_id)
                    names.append(name_obj.name)
                except Names.DoesNotExist:
                    continue

            update_name = request.data.get('username')

            full_name_from_db = " ".join(names).lower().strip()
            update_name = request.data.get('username', '').lower().strip()

            if update_name != full_name_from_db:
                db_names = full_name_from_db.split()
                names_list = update_name.split()

                df_name = [name for name in names_list if name not in db_names]

                referencias = []
                for new_name in df_name:
                    try:
                        name_obj = Names.objects.get(name=new_name)
                        referencias.append(name_obj.id)
                    except Names.DoesNotExist:
                        name_data = {"name": new_name}
                        serializer = CreateNames(data=name_data)
                        if serializer.is_valid():
                            new_name_obj = serializer.save()
                            referencias.append(new_name_obj.id)
                        else:
                            return JsonResponse({
                                'success': False,
                                'message': 'Erro ao criar novo nome',
                                'error': serializer.errors
                            }, status=status.HTTP_400_BAD_REQUEST)

                if referencias:
                    UserName.objects.filter(user_id=user.id).delete()
                    order = 1
                    for referencia in referencias:
                        serializer_user = CreateUserName(
                            data={'name_id': referencia,
                                  'user_id': user.id,
                                  'create_order': order})
                        if serializer_user.is_valid():
                            serializer_user.save()
                            order += 1
                        else:
                            return JsonResponse({
                                'success': False,
                                'message': 'Erro ao criar nome do usuário',
                                'error': serializer_user.errors
                            }, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({'success': True,
                            'message': 'Usuário atualizado com sucesso'},
                            status=status.HTTP_200_OK)

    except NormalUser.DoesNotExist:
        return JsonResponse({'success': False,
                             'message': 'Usuário não encontrado'},
                            status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({'success': False,
                             'message': 'Erro interno no servidor.',
                             'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@throttle_classes([
    MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
def password_reset(request):
    if request.method != 'POST':
        return JsonResponse({'success': False,
                             'message': 'Método não permitido'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        email = request.data.get('email')
        user = NormalUser.objects.get(email=email)
        token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"https://your-frontend-url/reset-password/{uid}/{token}/"

        send_mail(
            'Reset your password',
            f'Use the link to reset your password: {reset_url}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )
        return JsonResponse({"message": "Password reset link sent!"},
                            status=status.HTTP_200_OK)
    except NormalUser.DoesNotExist:
        return JsonResponse({"message": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.password}"


account_activation_token = TokenGenerator()


@api_view(['POST'])
def PasswordResetConfirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = NormalUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, NormalUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        new_password = request.data.get('password')
        user.set_password(new_password)
        user.save()
        return JsonResponse({"message": "Password has been reset!"},
                            status=status.HTTP_200_OK)
    else:
        return JsonResponse({"message": "Invalid token"},
                            status=status.HTTP_400_BAD_REQUEST)
