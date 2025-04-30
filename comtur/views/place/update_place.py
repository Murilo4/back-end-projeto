from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Places, PlacesPhotos, Category, PlaceCategories, Names
from ...models import UserName, Subscription, Plans, PlansConfig, NormalUser
from ...serializers.place import UpdatePlaces, CreateCategory, CreatePlaceCat
from ...serializers.place import UpdateSlug
from ...serializers.Names import CreateNames, CreateUserNamePlace
import os
import time
import json
import jwt
from django.utils.text import slugify
from django.db import transaction
from dotenv import load_dotenv
from django.conf import settings
from django.core.files.storage import default_storage

load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['PUT'])
def update_place(request, slug):
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
        # Validate and process the 'type' field
        place_type = request.data.get("type")
        if not place_type or not isinstance(place_type, str):
            return JsonResponse({'success': False,
                                 'message':
                                 'Invalid type field.'},
                                status=status.HTTP_400_BAD_REQUEST)

        place = Places.objects.get(slug=slug)
        with transaction.atomic():
            # Ensure 'type' is included in the data to be updated
            update_data = request.data.copy()
            update_data["type"] = place_type.strip()  # Clean up the type field
            update_place = UpdatePlaces(place, data=update_data, partial=True)
            if update_place.is_valid():
                update_place.save()
            else:
                return JsonResponse({'success': False,
                                     'message': 'Invalid data',
                                     'errors': update_place.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

            username_list = UserName.objects.filter(
                places=place.id).order_by('create_order')
            names = []
            for username in username_list:
                try:
                    name_obj = Names.objects.get(id=username.name_id)
                    names.append(name_obj.name)
                except Names.DoesNotExist:
                    continue

            full_name_from_db = " ".join(names).lower().strip()
            update_name = request.data.get('placeName', '').lower().strip()

            if update_name != full_name_from_db:
                name_list = update_name.split()
                new_names = [name for name in name_list]
                timestamp = str(int(time.time()))
                hash_string = f"{update_name}-{timestamp}"
                slug = slugify(hash_string, allow_unicode=True)
                slug = UpdateSlug(place, data={'slug': slug})
                if slug.is_valid():
                    slug.save()
                else:
                    pass
                referencias = []
                for new_name in new_names:
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

                try:
                    UserName.objects.filter(places=place.id,
                                            ).delete()
                except UserName.DoesNotExist:
                    pass

                if referencias:
                    order = 1
                    for referencia in referencias:
                        serializer_user = CreateUserNamePlace(
                            data={'name_id': referencia,
                                  'places': place.id,
                                  'create_order': order})
                        if serializer_user.is_valid(raise_exception=True):
                            serializer_user.save()
                            order += 1
                        else:
                            return JsonResponse({
                                'success': False,
                                'message': 'Erro ao criar nome do usuário',
                                'error': serializer_user.errors
                            }, status=status.HTTP_400_BAD_REQUEST)

            photo = request.data.getlist('photos', [])
            number_images = 3
            try:
                user_sub = Subscription.objects.get(user=user)
                plan = Plans.objects.get(id=user_sub.plan.id)
                plan_config = PlansConfig.objects.get(plan=plan.id)
                number_images = plan_config.number_images
            except Subscription.DoesNotExist:
                pass
            try:
                qtt_photos = len(photo)
            except Exception:
                qtt_photos = 2
            if qtt_photos > number_images:
                return JsonResponse({'success': False,
                                    'message':
                                     'Você excedeu o número de imagens'},
                                    status=status.HTTP_402_PAYMENT_REQUIRED)
            if photo:
                img_ids_to_keep = process_img(
                    photo, place.id)
                remove_old_img(place.id, img_ids_to_keep)

            category = request.data.getlist('categories', [])
            if category:
                category_to_keep, category_to_add = process_cat(
                    category, place.id)

                remove_old_cat(place.id, category_to_keep)

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

    for image_data in existing_images:
        if isinstance(image_data, str) and image_data.startswith('/media/'):
            image_data = image_data.replace('/media/', '', 1)
            try:
                img = PlacesPhotos.objects.get(
                    img_url=image_data, place_photo=place)
                img_ids_to_keep.add(img.id)
            except PlacesPhotos.DoesNotExist:
                continue
        elif hasattr(image_data, 'file'):
            try:
                file_path = default_storage.save(
                    os.path.join('place_photos', image_data.name),
                    image_data
                )
                relative_path = file_path.replace(
                    settings.MEDIA_ROOT + '/', '')

                # Directly create the PlacesPhotos object
                img = PlacesPhotos.objects.create(
                    img_url=relative_path,
                    place_photo_id=place,
                    description="imagem"
                )
                get_img = PlacesPhotos.objects.filter(
                    img_url=relative_path).first()
                img_ids_to_keep.add(get_img.id)
            except Exception:
                continue
    return img_ids_to_keep


def remove_old_img(place, img_ids_to_keep):
    current_img_ids = set(
        PlacesPhotos.objects.filter(
            place_photo=place).values_list('id', flat=True)
    )
    img_to_remove = current_img_ids - img_ids_to_keep
    if img_to_remove:
        PlacesPhotos.objects.filter(id__in=img_to_remove).delete()


def process_cat(existing_categories, place):
    category_ids_to_keep = set()
    category_ids_to_add = []

    for category_list in existing_categories:
        try:
            # Parse the category list (if it's a JSON string)
            categories = json.loads(category_list) if isinstance(
                category_list, str) else category_list
            for category_data in categories:
                category_name = category_data.get(
                    "category")  # Access the "category" field
                if not category_name:
                    continue

                try:
                    # Try to get the existing category
                    existing_category = Category.objects.get(
                        category=category_name)
                    category_ids_to_keep.add(existing_category.id)
                except Category.DoesNotExist:
                    # Create a new category if it doesn't exist
                    new_category = CreateCategory(
                        data={"category": category_name})
                    if new_category.is_valid(raise_exception=True):
                        new_category.save()
                        get_category = Category.objects.filter(
                            category=category_name).first()
                        if get_category:
                            category_ids_to_add.append(get_category.id)
                            category_ids_to_keep.add(get_category.id)

        except Exception:
            continue

    for cat in category_ids_to_keep:
        try:
            PlaceCategories.objects.get(category=cat, place=place)
        except PlaceCategories.DoesNotExist:
            category_ids_to_add.append(cat)

    for ids in category_ids_to_add:
        New_placeCategory = CreatePlaceCat(data={
            'place': place, 'category': ids})
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
            PlaceCategories.objects.filter(
                category=category_id, place=place).delete()
