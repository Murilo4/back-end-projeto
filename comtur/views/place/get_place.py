from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Places, PlacesPhotos, PlaceCategories, PlacesComments
from ...models import Category, UserName, Names, PlacesCity, Address, City
from ...models import PlacesStates, State


@api_view(['GET'])
def get_place(request, slug):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        place = Places.objects.get(slug=slug)

        username_list = UserName.objects.filter(
            places=place.id).order_by('create_order')

        names = []
        for username in username_list:
            try:
                name_obj = Names.objects.get(id=username.name_id)
                names.append(name_obj.name)
            except Names.DoesNotExist:
                continue

        full_name = " ".join(names)

        city = PlacesCity.objects.get(id=place.city.id)
        state = PlacesStates.objects.get(id=city.placeState.id)
    except Places.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Local não encontrado"},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        photos = PlacesPhotos.objects.filter(place_photo=place.id)
        category_sr_id = PlaceCategories.objects.filter(place=place.id)
        category_formated = []

        for category in category_sr_id:
            category_db = Category.objects.get(id=category.category)
            category_formated.append(category_db.category)

        photos = PlacesPhotos.objects.filter(
            place_photo=place.id)
        photos_url = []
        for photo in photos:
            photo_url = photo.img_url.url if photo.img_url else None
            photos_url.append(photo_url)

        try:
            address = Address.objects.get(place=place.id)
        except Address.DoesNotExist:
            return JsonResponse({'success': False,
                                 'message': 'Endereço não encontrado.'},
                                status=status.HTTP_404_NOT_FOUND)
        try:
            city = City.objects.get(id=address.city.id)
            state = State.objects.get(id=address.state.id)
        except City.DoesNotExist:
            return JsonResponse({'success': False,
                                 'message':
                                 'Não foi possivel retornar o endereço'},
                                status=status.HTTP_404_NOT_FOUND)
        place_json = {
                "description": place.description,
                "type": place.type,
                "slug": place.slug,
                "locationX": place.locationX,
                "locationY": place.locationY,
                "workStart": place.work_start,
                "workStop": place.work_stop,
                "about": place.about,
                "rating": place.rating_number if place.rating_number else 0,
                "placeName": full_name,
                "photos": photos_url,
                "lowerPrice": place.lower_price,
                "higherPrice": place.higher_price,
                "categories": category_formated,
                "state": state.state,
                "city": city.city,
            }
    except (PlacesPhotos.DoesNotExist,
            PlacesComments.DoesNotExist,
            Category.DoesNotExist,
            PlacesComments.DoesNotExist):
        pass

    return JsonResponse({
        "success": True,
        "message": "Local encontrado",
        "place": place_json,
    })
