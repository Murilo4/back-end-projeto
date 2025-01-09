from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...serializers.address import CreateAddress, CreateHouseNumber
from ...serializers.address import CreateState, createCity, CreateNeighborhood
from ...serializers.address import CreateStreetAddress, CreateStreet
from ...serializers.address import CreateNeighborAddress
from ...serializers.Names import CreateNames, CreateUserNameAddress
from django.db import transaction
import jwt
import os
from ...throttles import DailyRateThrottle, HourlyRateThrottle
from ...throttles import MinuteRateThrottleAnon
from ...models import HouseNumber, Address, State, City, Street, Neighborhood
from ...models import Names
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

        place_id = request.data.get('placeId', None)

        with transaction.atomic():
            number = request.data.get('number')
            state = request.data.get('state')
            city = request.data.get('city')
            street = request.data.get('street')
            neighbor = request.data.get('neighborhood')
            address_type = request.data.get('addressType')
            names = request.data.get('addressName')

            name = [n.strip() for n in names.split() if n.strip()]
            state = state.lower()
            formated_street = [n.strip() for n in street.split() if n.strip()]
            format_neigh = [n.strip() for n in neighbor.split() if n.strip()]
            created_number, referencia_number = create_numbers(number)
            created_state, referencia_state = create_state(state)
            created_city, referencia_city = create_city(city)

            if created_state is False:
                return JsonResponse({'success': False,
                                     'message': 'Estado não encontrado'},
                                    status=status.HTTP_404_NOT_FOUND)

            if created_number is False:
                return JsonResponse({
                    "success": False,
                    "message": "Erro ao criar nome",
                }, status=status.HTTP_400_BAD_REQUEST)

            if created_city is False:
                return JsonResponse({
                    "success": False,
                    "message": "Erro ao criar cidade",
                    }, status=status.HTTP_400_BAD_REQUEST)

            postal = request.data.get('postal')
            try:
                link_number = HouseNumber.objects.get(id=referencia_number)
                get_state = State.objects.get(id=referencia_state)
                get_city = City.objects.get(id=referencia_city)
            except (HouseNumber.DoesNotExist, State.DoesNotExist):
                return JsonResponse({"success": False,
                                    "message": "Erro ao criar Endereço"},
                                    status=status.HTTP_400_BAD_REQUEST)
            if place_id is None:
                new_address = {
                    'user_address': user_id,
                    'city': get_city.id,
                    'address_type': address_type,
                    'state': get_state.id,
                    'number': link_number.id,
                    'postal': postal
                }
            if place_id:
                new_address = {
                    'place': place_id,
                    'address_type': address_type,
                    'city': get_city.id,
                    'state': get_state.id,
                    'number': link_number.id,
                    'postal': postal
                }
            create = CreateAddress(data=new_address)
            if create.is_valid(raise_exception=True):
                create.save()

                get_address = Address.objects.get(
                    user_address=user_id, city=get_city.id, postal=postal,
                    number=link_number.id, state=get_state.id)
                address_id = get_address.id
                created_street = create_street(
                    formated_street, address_id)

                created_neighborhood = create_neighborhood(
                    format_neigh, address_id)

                created_name = create_names(name, address_id)

                if created_name is False:
                    return JsonResponse({'success': False,
                                        'message': 'Nome inválido'},
                                        status=status.HTTP_400_BAD_REQUEST)

                if created_neighborhood is False:
                    return JsonResponse({"success": False,
                                        "message": "Erro ao criar bairro"},
                                        status=status.HTTP_400_BAD_REQUEST)

                if created_street is False:
                    return JsonResponse({"success": False,
                                        "message": "Erro ao criar rua"},
                                        status=status.HTTP_400_BAD_REQUEST)

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
    created_numbers = True
    try:
        obj = HouseNumber.objects.get(number=numbers)
        referencia = obj.id
    except HouseNumber.DoesNotExist:
        data = {"number": numbers}
        serializer = CreateHouseNumber(data=data)
        if serializer.is_valid(raise_exception=True):
            obj = serializer.save()
            new_name = HouseNumber.objects.get(number=obj.number)
            referencia = new_name.id
        else:
            created_numbers = False
    return created_numbers, referencia


def create_state(state):
    created_state = True
    try:
        obj = State.objects.get(state=state)
        referencias_state = obj.id
    except State.DoesNotExist:
        test_data = {"state": state}
        serializer = CreateState(data=test_data)
        if serializer.is_valid(raise_exception=True):
            obj = serializer.save()
            new_state = State.objects.get(state=obj.state)

            referencias_state = new_state.id
        else:
            created_state = False
    return created_state, referencias_state


def create_city(city):
    created_city = True
    try:
        obj = City.objects.get(city=city)
        referencias_city = obj.id
    except City.DoesNotExist:
        new_city = {"city": city}
        serializer = createCity(data=new_city)
        if serializer.is_valid(raise_exception=True):
            obj = serializer.save()
            new_city = City.objects.get(city=obj.city)
            referencias_city = new_city.id
        else:
            created_city = False
    return created_city, referencias_city


def create_street(streets, address):
    created_street = True
    referencias_street = []

    for street in streets:
        try:
            # Tenta obter a rua existente
            obj = Street.objects.get(street=street)
            referencias_street.append(obj.id)
        except Street.DoesNotExist:
            # Caso não exista, cria uma nova rua
            new_street = {"street": street}
            serializer = CreateStreet(data=new_street)
            if serializer.is_valid(raise_exception=True):
                obj = serializer.save()  # Salva a nova rua
                new_street = Street.objects.get(street=street)
                referencias_street.append(new_street.id)

    order = 1
    for referencia in referencias_street:
        address_street = CreateStreetAddress(data={
            'address': address,
            'street': referencia,
            'street_order': order
        })
        if address_street.is_valid(raise_exception=True):
            address_street.save()
            order += 1
        else:
            created_street = False

    return created_street


def create_neighborhood(neighborhood, address):
    created_neighborhood = True
    referencias_neighborhood = []
    for neigh in neighborhood:
        try:
            obj = Neighborhood.objects.get(neighborhood=neigh)
            referencias_neighborhood.append(obj.id)
        except Neighborhood.DoesNotExist:
            new_neighborhood = {"neighborhood": neigh}
            serializer = CreateNeighborhood(data=new_neighborhood)
            if serializer.is_valid(raise_exception=True):
                obj = serializer.save()
                new_neighborhood = Neighborhood.objects.get(
                    neighborhood=neigh)
                referencias_neighborhood.append(new_neighborhood.id)
            else:
                created_neighborhood = False
    order = 1
    for referencia in referencias_neighborhood:
        address_neighborhood = CreateNeighborAddress(
                                                data={
                                                    'address': address,
                                                    'neighborhood': referencia,
                                                    'neighbor_order': order
                                                    })
        if address_neighborhood.is_valid(raise_exception=True):
            address_neighborhood.save()
            order += 1
        else:
            created_neighborhood = False
    return created_neighborhood


def create_names(name, address):
    referencias = []
    created_names = True
    for nome in name:
        nome_lower = nome.lower().strip()
        try:
            obj = Names.objects.get(name=nome_lower)
            referencias.append(obj.id)
        except Names.DoesNotExist:
            test_data = {"name": nome_lower}
            serializer = CreateNames(data=test_data)
            if serializer.is_valid():
                obj = serializer.save()
                new_name = Names.objects.get(name=nome)
                referencias.append(new_name.id)
            else:
                created_names = False
    order = 1
    for referencia in referencias:
        username = CreateUserNameAddress(data={
                                'address': address,
                                'name_id': referencia,
                                'create_order': order
                                })
        if username.is_valid(raise_exception=True):
            username.save()
            order += 1
        else:
            created_names = False
    return created_names
