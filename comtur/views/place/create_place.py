from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import Category, NormalUser, Subscription, Plans, PlansConfig
from ...serializers.place import CreatePlace, CreateCategory, CreatePlaceCat
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
    try:
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

        description = request.data.get('description')
        type = request.data.get('type')
        work_start = request.data.get('workStart')
        work_stop = request.data.get("workStop")

        if not description and type:
            return JsonResponse({'error': 'Invalid data'},
                                status=status.HTTP_400_BAD_REQUEST)
        if not work_start and not work_stop:
            return JsonResponse({'sucess': False,
                                'message':
                                 'horario de funcionamento não informado'},
                                status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            new_place = {
                "description": description,
                "type": type,
                "localizationX": request.data.get('localizationX', ''),
                "localizationY": request.data.get('localizationY', ''),
                "work_start": work_start,
                "work_stop": work_stop,
                "enterprise": enterprise,
                "about": request.data.get("about", '')
                }
            place_create = CreatePlace(data=new_place)
            if place_create.is_valid():
                place_create.save()
            else:
                return JsonResponse({'error': 'Invalid data'},
                                    status=status.HTTP_400_BAD_REQUEST)

            categories = request.data.get("categories")

            is_categories_valid = get_or_create_category(
                place_create, categories)
            if is_categories_valid is False:
                return JsonResponse({"success": False,
                                     "message": "Não foi criar as categorias"},
                                    status=status.HTTP_400_BAD_REQUEST)
            number_images = 3
            try:
                user_sub = Subscription.objects.get(user=user)
                user_pan = Plans.objects.get(subscription=user_sub.id)
                plan_config = PlansConfig.objects.get(plan=user_pan)
                number_images = plan_config.number_images
            except Subscription.DoesNotExist:
                pass
            except Plans.DoesNotExist:
                pass
            except PlansConfig.DoesNotExist:
                pass

            photos: list = request.data.get('photos', [])
            qtt_photos = photos.count
            if qtt_photos > number_images:
                return JsonResponse({'success': False,
                                    'message':
                                     'Você excedeu o número de imagens'},
                                    status=status.HTTP_400_BAD_REQUEST)

            is_photos_valid = get_or_create_photos(
                place_create, photos, number_images)

            if is_photos_valid is False:
                return JsonResponse({"success": False,
                                     "message": "Não foi criar as fotos"},
                                    status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({"success": True,
                                 "message": "Local criado com sucesso"},
                                status=status.HTTP_200_OK)
    except Exception:
        return JsonResponse({'error': 'Internal Server Error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_or_create_category(place_create, categories):
    category_valid = True
    for category in categories:
        categories_ids = []
        try:
            category_exists = Category.objects.get(category=category)
            categories_ids.append(category_exists.id)
        except Category.DoesNotExist:
            create_category = CreateCategory(
                data={'category': category})
            if create_category.is_valid():
                create_category.save()
                categories_ids.append(create_category.id)
            else:
                category_valid = False

    for category_id in categories_ids:
        create_placeCat = CreatePlaceCat(data={
                                        'category': category_id,
                                        'place': place_create.id})
        if create_placeCat.is_valid():
            create_placeCat.save()
        else:
            category_valid = False
    return category_valid


def get_or_create_photos(place_create, photos):
    photos_valid = True
    for photo in photos:
        photos_ids = []
        create_category = CreateCategory(
            data={'img_url': photo.url,
                  'place': place_create.id,
                  'description': photo.description})
        if create_category.is_valid():
            create_category.save()
            photos_ids.append(create_category.id)
        else:
            photos_valid = False
    return photos_valid
