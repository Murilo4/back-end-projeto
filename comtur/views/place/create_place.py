from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import Category, NormalUser, Subscription
from ...models import Places
from ...serializers.place import CreatePlace, CreateCategory, CreatePlaceCat
from ...serializers.place import CreatePhotos
from django.db import transaction
from ...throttles import DailyRateThrottle, HourlyRateThrottle
from ...throttles import MinuteRateThrottleAnon


@api_view(['POST'])
@throttle_classes([
    MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
def create_place(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
    enterprise = request.data.get('enterpriseId')
    if not enterprise:
        return JsonResponse({"success": False,
                            "message": "Empresa não encontrada"},
                            status=status.HTTP_400_BAD_REQUEST)

    user = NormalUser.objects.get(id=enterprise)
    if user.cnpj is None and user.cpf:
        return JsonResponse({"success": False,
                            "message": "A conta precisa ser empresarial"},
                            status=status.HTTP_401_UNAUTHORIZED)
    has_place = Places.objects.filter(enterprise=enterprise).exists()
    if has_place:
        return JsonResponse({"success": False,
                             "message": "Você já tem um local cadastrado"},
                            status=status.HTTP_400_BAD_REQUEST)

    description = request.data.get('description')
    type = request.data.get('type')
    work_start = request.data.get('workStart')
    work_stop = request.data.get("workStop")

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
    with transaction.atomic():
        new_place = {
                "description": description,
                "type": type,
                "locationX": request.data.get('locationX', ''),
                "locationY": request.data.get('locationY', ''),
                "work_start": work_start,
                "work_stop": work_stop,
                "enterprise": enterprise,
                "about": request.data.get("about", '')
                }
        place_create = CreatePlace(data=new_place)
        if place_create.is_valid(raise_exception=True):
            place_create.save()

        # is_categories_valid = False
        categories = request.data.get("categories", [])
        get_place = Places.objects.get(enterprise=enterprise)
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
            number_images = user_sub.number_images
        except Subscription.DoesNotExist:
            pass

        photos: list = request.data.get('photos', [])
        qtt_photos = len(photos)
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

        return JsonResponse({"success": True,
                            "message": "Local criado com sucesso"},
                            status=status.HTTP_200_OK)


def get_or_create_category(place_create, categories):
    category_valid = True
    categories_ids = []
    for category in categories:
        try:
            category_exists = Category.objects.get(category=category)
            categories_ids.append(category_exists.id)
        except Category.DoesNotExist:
            create_category = CreateCategory(
                data={'category': category})
            if create_category.is_valid():
                create_category.save()
                get_category = Category.objects.get(
                    category=category)
                categories_ids.append(get_category.id)
            else:
                category_valid = False
    for category_id in categories_ids:
        create_placeCat = CreatePlaceCat(data={
                                        'category': category_id,
                                        'place': place_create})
        if create_placeCat.is_valid():
            create_placeCat.save()
        else:
            category_valid = False
    return category_valid


def get_or_create_photos(place_create, photos):
    photos_valid = True
    for photo in photos:
        photo_url = photo.get('url')
        photo_desc = photo.get('description')
        create_photo = CreatePhotos(
            data={'img_url': photo_url,
                  'place_photo': place_create,
                  'description': photo_desc})
        if create_photo.is_valid(raise_exception=True):
            create_photo.save()
        else:
            photos_valid = False
    return photos_valid
