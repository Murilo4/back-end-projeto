from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import Places, PlacesPhotos, PlaceCategories, PlacesComments
from ...models import Category, UserPlaces, UserName, Names
from ...throttles import DailyRateThrottle, HourlyRateThrottle
from ...throttles import MinuteRateThrottleAnon
from ...serializers.place import PlaceGetSerializer


@api_view(['GET'])
@throttle_classes(
    [MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
def get_place(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    place_id = request.data.get('placeId')
    try:
        place = Places.objects.get(id=place_id)
        place_serializer = PlaceGetSerializer(place)
    except Places.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Local não encontrado"},
                            status=status.HTTP_404_NOT_FOUND)

    try:
        # Obter as fotos
        photos = PlacesPhotos.objects.filter(place_photo=place_id)
        photo_formated = [photo.img_url for photo in photos]

        # Obter as categorias
        category_sr_id = PlaceCategories.objects.filter(place=place_id)
        category_formated = []

        for category in category_sr_id:
            category_db = Category.objects.get(id=category.category)
            category_formated.append(category_db.category)

        comments_formated = []
        comments = PlacesComments.objects.filter(place_comment=place_id)
        for comment in comments:
            user_place = UserPlaces.objects.get(comments=comment.id)

            # Obter o nome do usuário
            user_name_record = UserName.objects.get(
                user_id=user_place.user_place.id)  # Acesso ao ID do usuário
            user_name = Names.objects.get(id=user_name_record.name_id)

            comments_formated.append({
                "username": user_name.name,  # Nome do usuário
                "comment": comment.comment,
                "rating": user_place.rating
            })

    except (PlacesPhotos.DoesNotExist,
            PlacesComments.DoesNotExist,
            Category.DoesNotExist,
            PlacesComments.DoesNotExist):
        pass

    return JsonResponse({
        "success": True,
        "message": "Local encontrado",
        "place": place_serializer.data,
        "photos": photo_formated,
        "categories": category_formated,
        "comments": comments_formated
    })
