from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import Places, PlacesPhotos, Category
from ...serializers.place import UpdatePlaces
import os
from ...throttles import DailyRateThrottle, HourlyRateThrottle
from ...throttles import MinuteRateThrottleAnon
from django.db import transaction
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['PUT'])
@throttle_classes([MinuteRateThrottleAnon,
                   HourlyRateThrottle, DailyRateThrottle])
def update_place(request):
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

        place_id = request.data.get('placeId')

        place = Places.objects.get(id=place_id)

        with transaction.atomic():
            update_place = UpdatePlaces(place,
                                        data=request.data, partial=True)
            if update_place.is_valid():
                update_place.save()
            else:
                return JsonResponse({'success': False,
                                     'message': 'Invalid data'},
                                    status=status.HTTP_400_BAD_REQUEST)

            img_ids_to_keep, img_ids_to_add = process_img(
                    request.data.get('photos', []), place)
            category_to_keep, category_to_add = process_cat(
                request.data.get('categorys', []), place)

            remove_old_cat(place, category_to_keep)
            remove_old_img(place, img_ids_to_keep)

        return JsonResponse({'success': True,
                            'message': 'Usuário atualizado com sucesso'},
                            status=status.HTTP_200_OK)

    except Places.DoesNotExist:
        return JsonResponse({'success': False,
                             'message': 'Usuário não encontrado'},
                            status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({'success': False,
                             'message': 'Erro interno no servidor.',
                             'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def process_img(existing_images, place):
    img_ids_to_keep = set()
    img_ids_to_add = []

    existing_file_urls = set(PlacesPhotos.objects.filter(
        place=place).values_list('file_url', flat=True))

    for image_data in existing_images:
        img_url = image_data.get('fileUrl')
        img_description = image_data.get('description', None)

        if img_url in existing_file_urls:
            img_ids_to_keep.add(img_url)
        else:
            img = PlacesPhotos(img_url=img_url, place=place.id)
            if img_description:
                img.file_description = img_description
            img_ids_to_add.append(img)
    unique_img_ids_to_add = []
    existing_urls_in_add = set()

    for img in img_ids_to_add:
        if img.file_url not in existing_urls_in_add:
            unique_img_ids_to_add.append(img)
            existing_urls_in_add.add(img.file_url)

    if unique_img_ids_to_add:
        PlacesPhotos.objects.bulk_create(unique_img_ids_to_add)

    for image in unique_img_ids_to_add:
        existing_img = PlacesPhotos.objects.filter(
            img_url=image.file_url).first()
        if existing_img:
            img_ids_to_keep.add(existing_img.file_url)

    return img_ids_to_keep, unique_img_ids_to_add


def remove_old_img(place, exist_img_urls):
    current_img_urls = PlacesPhotos.objects.filter(
        img_url=place
    ).values_list('file_url', flat=True)

    img_to_remove = set(current_img_urls) - set(exist_img_urls)
    if img_to_remove:
        PlacesPhotos.objects.filter(
            img_url__in=img_to_remove,
            place=place).delete()


def process_cat(existing_categories, place):
    category_ids_to_keep = set()
    category_ids_to_add = []

    # Obter as categorias já associadas ao place
    existing_category_ids = set(
        place.categories.values_list('id', flat=True)
    )

    for category_data in existing_categories:
        category_id = category_data.get('id')

        if category_id in existing_category_ids:
            category_ids_to_keep.add(category_id)
        else:
            # Se não estiver, prepara para adicionar essa categoria
            category = Category.objects.get(id=category_id)
            category_ids_to_add.append(category)

    if category_ids_to_add:
        place.categories.add(*category_ids_to_add)

    category_ids_to_keep.update(
        category.id for category in category_ids_to_add
    )

    return category_ids_to_keep, category_ids_to_add


def remove_old_cat(place, existing_category_ids):
    current_category_ids = set(
        place.categories.values_list('id', flat=True)
    )
    categories_to_remove = current_category_ids - set(existing_category_ids)

    if categories_to_remove:
        place.categories.remove(*categories_to_remove)
