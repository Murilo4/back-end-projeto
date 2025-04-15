from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import NormalUser, Subscription, Names, PlacesCity
from ...models import PlacesStates, Places, Category, Plans, PlansConfig
from ...serializers.place import CreatePlace, CreatePlaceCat, CreateCategory
from ...serializers.place import CreatePhotos, CreateCity, CreateState
from ...serializers.Names import CreateNames, CreateUserNamePlace
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify
import time
from django.db import transaction
import os
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['POST'])
def create_place(request):
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
        cnpj = payload.get('id')
    except Exception:
        return JsonResponse({
            "success": False,
            "message": "Token JWT inválido ou expirado."
        }, status=status.HTTP_401_UNAUTHORIZED)
    enterprise = cnpj
    if not enterprise:
        return JsonResponse({"success": False,
                            "message": "Empresa não encontrada"},
                            status=status.HTTP_400_BAD_REQUEST)

    user = NormalUser.objects.get(id=enterprise)
    if user.cnpj is None and user.cpf:
        return JsonResponse({"success": False,
                            "message": "A conta precisa ser empresarial"},
                            status=status.HTTP_401_UNAUTHORIZED)

    description = request.data.get('description')
    type = request.data.getlist('tipos[]')
    work_start = request.data.get('workStart')
    work_stop = request.data.get("workStop")
    placeName: str = request.data.get("placeName")
    city = request.data.get("city")
    state = request.data.get("state")
    placeName = placeName.strip()
    categories = request.data.getlist('categories[]')
    lower_price = request.data.get('lowerPrice')
    higher_price = request.data.get('higherPrice')

    name = [n.lower().strip() for n in placeName.split() if n.strip()]
    if not description and type:
        return JsonResponse({'success': False,
                            'message':
                             'Campos obrigatórios não preenchidos'},
                            status=status.HTTP_400_BAD_REQUEST)
    if not work_start and not work_stop:
        return JsonResponse({'success': False,
                            'message':
                             'horario de funcionamento não informado'},
                            status=status.HTTP_400_BAD_REQUEST)
    if not name:
        return JsonResponse({"success": False,
                             "message": "Nome não enviado"},
                            status=status.HTTP_400_BAD_REQUEST)
    with transaction.atomic():

        created_state, state_reference = create_state(state)
        if created_state is False:
            return JsonResponse({
                "success": False,
                "message": "Erro ao criar estado",
            }, status=status.HTTP_400_BAD_REQUEST)

        created_city, city_reference = create_city(city, state_reference[0])
        if created_city is False:
            return JsonResponse({
                "success": False,
                "message": "Erro ao criar cidade",
            }, status=status.HTTP_400_BAD_REQUEST)
        timestamp = str(int(time.time()))
        hash_string = f"{placeName}-{timestamp}"
        slug = slugify(hash_string, allow_unicode=True)

        new_place = {
            "description": description,
            "type": type[0],
            "locationX": request.data.get('locationX', ''),
            "locationY": request.data.get('locationY', ''),
            "work_start": work_start,
            "work_stop": work_stop,
            "enterprise": enterprise,
            "city": city_reference[0],
            "about": request.data.get("about", ''),
            "lower_price": lower_price,
            "higher_price": higher_price,
            "slug": slug,
        }
        place_create = CreatePlace(data=new_place)
        if not place_create.is_valid(raise_exception=True):
            return JsonResponse({'success': False,
                                'message':
                                 'Erro ao criar local'},
                                status=status.HTTP_400_BAD_REQUEST)
        place_create.save()
        get_place = Places.objects.filter(enterprise=enterprise, type=type[0]
                                          ).order_by('-created_at').first()
        is_categories_valid = get_or_create_category(
            get_place.id, categories)

        if is_categories_valid is False:
            return JsonResponse({"success": False,
                                 "message":
                                "Não foi possivel criar as categorias"},
                                status=status.HTTP_400_BAD_REQUEST)

        number_images = 3
        try:
            user_sub = Subscription.objects.get(user=user)
            plan = Plans.objects.get(id=user_sub.plan.id)
            plan_config = PlansConfig.objects.get(plan=plan.id)
            number_images = plan_config.number_images
        except Subscription.DoesNotExist:
            pass
        photos = request.FILES.getlist('photos')
        qtt_photos = 2
        if qtt_photos > number_images:
            return JsonResponse({'success': False,
                                'message':
                                 'Você excedeu o número de imagens'},
                                status=status.HTTP_400_BAD_REQUEST)
        is_photos_valid = get_or_create_photos(
            get_place.id, photos)

        if is_photos_valid is False:
            return JsonResponse({"success": False,
                                 "message":
                                "Não foi possivel criar as fotos"},
                                status=status.HTTP_400_BAD_REQUEST)
        placeName = placeName.strip()

        name = [n.lower().strip() for n in placeName.split() if n.strip()]

        created_names, referencias = create_names(name)

        if created_names is False:
            return JsonResponse({
                "success": False,
                "message": "Erro ao criar nome",
            }, status=status.HTTP_400_BAD_REQUEST)
        order = 1
        for referencia in referencias:
            link_name = Names.objects.get(id=referencia)
            serializer_user = CreateUserNamePlace(
                data={'name_id': link_name.id,
                      'places': get_place.id,
                      'create_order': order})

            if serializer_user.is_valid(raise_exception=True):
                serializer_user.save()
                order += 1
            else:
                return JsonResponse({"success": False,
                                     "message":
                                     "Erro ao criar nome do usuario"},
                                    status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({"success": True,
                            "message": "Local criado com sucesso",
                             "placeId": get_place.id},
                            status=status.HTTP_200_OK)


def get_or_create_category(place_create, categories):
    category_valid = True
    categories_ids = []

    for category in categories:
        try:
            # Verificar se a categoria já existe
            category_exists = Category.objects.get(category=category)
            categories_ids.append(category_exists.id)
        except Category.DoesNotExist:
            # Criar nova categoria se não existir
            create_category = CreateCategory(data={'category': category})
            if create_category.is_valid(raise_exception=True):
                create_category.save()
                categories_ids.append(create_category.instance.id)
            else:
                category_valid = False

    for category_id in categories_ids:
        create_placeCat = CreatePlaceCat(data={
            'category': category_id,
            'place': place_create
        })
        if create_placeCat.is_valid(raise_exception=True):
            create_placeCat.save()
        else:
            category_valid = False

    return category_valid


def get_or_create_photos(place_create, photos):
    photos_valid = True
    for photo in photos:
        # Verifique se o photo é realmente um arquivo
        if isinstance(photo, InMemoryUploadedFile):
            create_photo = CreatePhotos(
                data={
                    'img_url': photo,
                    'place_photo': place_create,
                    'description': "Foto do local"
                }
            )
            if not create_photo.is_valid(raise_exception=True):
                print(create_photo.errors)
                photos_valid = False
            else:
                create_photo.save()
        else:
            photos_valid = False
            print("Erro: O dado não é um arquivo válido.")
    return photos_valid


def create_names(name):
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
            if serializer.is_valid(raise_exception=True):
                obj = serializer.save()
                new_name = Names.objects.get(name=obj.name)
                referencias.append(new_name.id)
            else:
                created_names = False
    return created_names, referencias


def create_city(city, state_reference):
    referencias = []
    created_city = True
    city_lower = city.lower()
    try:
        obj = PlacesCity.objects.get(city=city_lower,
                                     placeState=state_reference)
        referencias.append(obj.id)
    except PlacesCity.DoesNotExist:
        test_data = {"city": city_lower,
                     "placeState": state_reference}
        serializer = CreateCity(data=test_data)
        if serializer.is_valid(raise_exception=True):
            obj = serializer.save()
            new_city = PlacesCity.objects.get(city=obj.city)
            referencias.append(new_city.id)
        else:
            created_city = False
    return created_city, referencias


def create_state(state):
    referencias = []
    created_state = True
    state_lower = state.lower()
    try:
        obj = PlacesStates.objects.get(state=state_lower)
        referencias.append(obj.id)
    except PlacesStates.DoesNotExist:
        test_data = {"state": state_lower}
        serializer = CreateState(data=test_data)
        if serializer.is_valid(raise_exception=True):
            obj = serializer.save()
            new_state = PlacesStates.objects.get(state=obj.state)
            referencias.append(new_state.id)
        else:
            created_state = False
    return created_state, referencias
