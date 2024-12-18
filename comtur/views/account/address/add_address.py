from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ....serializers.address import CreateAddress, CreateHouseNumber
from ....serializers.address import CreateNumberAddress, CreateState
from ....serializers.address import CreateStateAddress
from django.db import transaction
import jwt
import os
from ....throttles import DailyRateThrottle, HourlyRateThrottle
from ....throttles import MinuteRateThrottleAnon
from ....models import HouseNumber, Address, State
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
@throttle_classes([
    MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
def create_address(request):
    if request.method != 'POST':
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

        with transaction.atomic():
            numbers = request.data.get('number')
            state = request.data.get('state')

            number = [n.strip() for n in numbers.split() if n.strip()]
            state = state.lower()

            created_number, referencias_number = create_numbers(number)
            created_state, referencia_state = create_state(state)

            if created_state is False:
                return JsonResponse({'success': False,
                                     'message': 'Estado não encontrado'},
                                    status=status.HTTP_404_NOT_FOUND)

            if created_number is False:
                return JsonResponse({
                    "success": False,
                    "message": "Erro ao criar nome",
                }, status=status.HTTP_400_BAD_REQUEST)
            street = request.data.get('street')
            postal = request.data.get('postal')
            new_address = {
                'user_address': user_id,
                'street': street,
                'neighborhood': request.data.get('neighborhood'),
                'city': request.data.get('city'),
                'state': request.data.get('state'),
                'postal': postal
            }
            create = CreateAddress(data=new_address)
            if create.is_valid(raise_exception=True):
                create.save()

                get_address = Address.objects.get(
                    user_address=user_id, street=street, postal=postal)
                address_id = get_address.id
                order = 1
                for referencia in referencias_number:
                    link_number = HouseNumber.objects.get(id=referencia)
                    serializer_user = CreateNumberAddress(
                        data={'house_number': link_number.id,
                              'address': address_id})

                    if serializer_user.is_valid(raise_exception=True):
                        serializer_user.save()
                        order += 1
                    else:
                        return JsonResponse({"sucess": False,
                                            "message":
                                             "Erro ao criar número da casa"},
                                            status=status.HTTP_400_BAD_REQUEST)
                state_id = referencia_state.pop()
                get_state = State.objects.get(id=state_id)
                create_new_state = CreateStateAddress(
                                                    data={
                                                        'state': get_state.id,
                                                        'address': address_id
                                                        })
                if create_new_state.is_valid(raise_exception=True):
                    create_new_state.save()
                    return JsonResponse({"sucess": True,
                                         "message":
                                         "endereço criado com sucesso"},
                                        status=status.HTTP_201_CREATED)
                else:
                    return JsonResponse({"sucess": False,
                                         "message":
                                         "Não foi possivel criar o estado"},
                                        status=status.HTTP_400_BAD_REQUEST)

    except jwt.ExpiredSignatureError:
        return JsonResponse({'success': False,
                            'message': 'Token expirado.'},
                            status=status.HTTP_401_UNAUTHORIZED)


def create_numbers(numbers: int):
    referencias = []
    created_numbers = True
    for number in numbers:
        try:
            obj = HouseNumber.objects.get(number=number)
            referencias.append(obj.id)
        except HouseNumber.DoesNotExist:
            data = {"number": number}
            serializer = CreateHouseNumber(data=data)
            if serializer.is_valid(raise_exception=True):
                obj = serializer.save()
                new_name = HouseNumber.objects.get(number=obj.number)
                referencias.append(new_name.id)
            else:
                created_numbers = False
    return created_numbers, referencias


def create_state(state):
    referencias_state = []
    created_state = True
    try:
        obj = State.objects.get(state=state)
        referencias_state.append(obj.id)
    except State.DoesNotExist:
        test_data = {"state": state}
        serializer = CreateState(data=test_data)
        if serializer.is_valid(raise_exception=True):
            obj = serializer.save()
            new_state = State.objects.get(state=obj.state)

            referencias_state.append(new_state.id)
        else:
            created_state = False
    return created_state, referencias_state
