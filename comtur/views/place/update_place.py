from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Places, PlacesPhotos, Category, PlaceCategories
from ...serializers.place import UpdatePlaces, CreateCategory, CreatePlaceCat
import os
from django.db import transaction
import json
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['PUT'])
def update_place(request, placeId):
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

        place_id = placeId

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

            photo = request.data.get('photos', [])
            if photo:
                img_ids_to_keep, img_ids_to_add = process_img(
                    photo, place)
                remove_old_img(place, img_ids_to_keep)

            category = request.data.getlist('categories', [])
            if category:
                category_to_keep, category_to_add = process_cat(
                    category, place)

                remove_old_cat(place, category_to_keep)

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
        place_photo=place).values_list('img_url', flat=True))

    for image_data in existing_images:
        img_url = image_data.get('url')
        img_description = image_data.get('description', None)

        if img_url in existing_file_urls:
            img_ids_to_keep.add(img_url)
        else:
            img = PlacesPhotos(img_url=img_url, place_photo=place)
            if img_description:
                img.file_description = img_description
            img_ids_to_add.append(img)
    unique_img_ids_to_add = []
    existing_urls_in_add = set()

    for img in img_ids_to_add:
        if img.img_url not in existing_urls_in_add:
            unique_img_ids_to_add.append(img)
            existing_urls_in_add.add(img.img_url)

    if unique_img_ids_to_add:
        PlacesPhotos.objects.bulk_create(unique_img_ids_to_add)

    for image in unique_img_ids_to_add:
        existing_img = PlacesPhotos.objects.filter(
            img_url=image.img_url).first()
        if existing_img:
            img_ids_to_keep.add(existing_img.img_url)

    return img_ids_to_keep, unique_img_ids_to_add


def remove_old_img(place, exist_img_urls):
    current_img_urls = PlacesPhotos.objects.filter(
        place_photo=place
    ).values_list('img_url', flat=True)

    img_to_remove = set(current_img_urls) - set(exist_img_urls)
    if img_to_remove:
        PlacesPhotos.objects.filter(
            img_url__in=img_to_remove,
            place_photo=place).delete()


def process_cat(existing_categories, place):
    # Desserializar categorias, se necessário
    if isinstance(existing_categories, str):
        existing_categories = json.loads(existing_categories)

    category_ids_to_keep = set()
    category_ids_to_add = []

    for category_data in existing_categories:
        # Acesse o campo "category" corretamente
        category_name = category_data.get("category")
        print(category_data)

        try:
            # Tentando obter a categoria diretamente com get()
            existing_category = Category.objects.get(category=category_name)
            category_ids_to_keep.add(existing_category.id)
        except Category.DoesNotExist:
            new_category = CreateCategory(data={"category": category_name})
            if new_category.is_valid(raise_exception=True):
                new_category.save()
                get_category = Category.objects.filter(
                    category=category_name).first()
                if get_category:
                    category_ids_to_add.append(get_category.id)
                    category_ids_to_keep.add(get_category.id)

    for cat in category_ids_to_keep:
        try:
            PlaceCategories.objects.get(category=cat, place=place)
        except PlaceCategories.DoesNotExist:
            category_ids_to_add.append(cat)

    for ids in category_ids_to_add:
        New_placeCategory = CreatePlaceCat(data={
            'place': place.id, 'category': ids})
        if New_placeCategory.is_valid(raise_exception=True):
            New_placeCategory.save()

    return category_ids_to_keep, category_ids_to_add


def remove_old_cat(place, existing_category_ids):
    current_category_ids = set(
        PlaceCategories.objects.filter(place=place).values_list(
            'category', flat=True)
    )
    categories_to_remove = current_category_ids - set(existing_category_ids)

    if categories_to_remove:
        for category_id in categories_to_remove:
            PlaceCategories.objects.filter(category=category_id).delete()
