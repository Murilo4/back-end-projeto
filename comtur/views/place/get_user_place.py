from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Places, PlacesPhotos, PlaceCategories, PlacesComments
from ...models import Category, UserName, Names, PlacesCity
from ...models import PlacesStates
import os
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_place_user(request):
    if request.method != 'GET':
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
    try:
        place = Places.objects.filter(enterprise=cnpj)
        thread_response = get_number_places(cnpj)

    except Places.DoesNotExist:
        return JsonResponse({"success": False,
                            "message": "Local não encontrado"},
                            status=status.HTTP_404_NOT_FOUND)
    places_formated = []
    for p in place:
        username_list = UserName.objects.filter(
            places=p.id).order_by('create_order')
        names = []
        for username in username_list:
            try:
                name_obj = Names.objects.get(id=username.name_id)
                names.append(name_obj.name)
            except Names.DoesNotExist:
                continue

        full_name = " ".join(names)
        city = PlacesCity.objects.get(id=p.city.id)
        state = PlacesStates.objects.get(id=city.placeState.id)

        try:
            # Obter as fotos
            photos = PlacesPhotos.objects.filter(
                place_photo=p.id)
            photos_url = []
            for photo in photos:
                photo_url = photo.img_url.url if photo.img_url else None
                photos_url.append(photo_url)
            # Obter as categorias
            category_sr_id = PlaceCategories.objects.filter(
                                                            place=p.id)
            category_formated = []

            for category in category_sr_id:
                category_db = Category.objects.get(id=category.category)
                category_formated.append(category_db.category)

            place_json = {
                "id": p.id,
                "description": p.description,
                "type": p.type,
                "locationX": p.locationX,
                "locationY": p.locationY,
                "workStart": p.work_start,
                "workStop": p.work_stop,
                "enterprise": p.enterprise.id,
                "about": p.about,
                "ratingNumber": p.rating_number if p.rating_number else 0,
                "placeName": full_name,
                "city": city.city,
                "state": state.state,
                "slug": p.slug,
            }
            places_formated.append({
                "place": place_json,
                "photos": photos_url,
                "categories": category_formated,
            })
        except (PlacesPhotos.DoesNotExist,
                PlacesComments.DoesNotExist,
                Category.DoesNotExist,
                PlacesComments.DoesNotExist):
            pass

    return JsonResponse({
        "success": True,
        "message": "Local encontrado",
        "place": places_formated,
        "numberPlaces": thread_response,
    }, status=status.HTTP_200_OK)


def get_number_places(cnpj):
    try:
        place = Places.objects.filter(enterprise=cnpj).count()
        return place
    except Places.DoesNotExist:
        place = 0
