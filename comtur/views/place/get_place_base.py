from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Places, PlacesPhotos, PlacesComments
from ...models import Category, UserName, Names


@api_view(['GET'])
def get_place_base(request, slug):
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

    except Places.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Local não encontrado"},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        photos = PlacesPhotos.objects.filter(place_photo=place.id)
        photos = PlacesPhotos.objects.filter(
            place_photo=place.id)
        photos_url = []
        for photo in photos:
            photo_url = photo.img_url.url if photo.img_url else None
            photos_url.append(photo_url)
        place_json = {
                "description": place.description,
                "type": place.type,
                "workStart": place.work_start,
                "workStop": place.work_stop,
                "about": place.about,
                "rating": place.rating_number if place.rating_number else 0,
                "placeName": full_name,
                "mediumRate": place.medium_rate,
                "photos": photos_url,
                "lowerPrice": place.lower_price,
                "higherPrice": place.higher_price,
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
