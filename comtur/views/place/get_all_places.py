from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from ...models import Places, PlacesPhotos, PlaceCategories, PlacesComments
from ...models import Category, UserPlaces, UserName, Names
from ...throttles import DailyRateThrottle, HourlyRateThrottle
from ...throttles import MinuteRateThrottleAnon
from ...serializers.place import PlaceGetSerializer
from django.db.models import Q


@api_view(['GET'])
@throttle_classes(
    [MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
def get_places(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    # Filtros de pesquisa
    categories = request.GET.getlist('category')
    place_types = request.GET.getlist('place_type')
    search_text = request.GET.get('search', '')

    # Paginação
    paginator = PageNumberPagination()
    paginator.page_size = 20

    places_query = Places.objects.all()

    # Aplicar filtro de categoria
    if categories:
        places_query = places_query.filter(
            placecategories__category__in=categories
        ).distinct()

    if place_types:
        places_query = places_query.filter(
            place_type__in=place_types
        ).distinct()

    if search_text:
        places_query = places_query.filter(
            Q(
                name__icontains=search_text) | Q(
                    description__icontains=search_text))

    result_page = paginator.paginate_queryset(places_query, request)
    serializer = PlaceGetSerializer(result_page, many=True)

    places_data = []
    for place in result_page:
        place_data = serializer.data
        place_id = place.id

        try:
            photos = PlacesPhotos.objects.filter(place_photo=place_id)
            photo_formated = [photo.img_url for photo in photos]

            category_sr_id = PlaceCategories.objects.filter(place=place_id)
            category_formated = []

            for category in category_sr_id:
                category_db = Category.objects.get(id=category.category)
                category_formated.append(category_db.category)

            comments_formated = []
            comments = PlacesComments.objects.filter(place_comment=place_id)
            for comment in comments:
                user_place = UserPlaces.objects.get(comments=comment.id)

                user_name_record = UserName.objects.get(
                    user_id=user_place.user_place.id)
                user_name = Names.objects.get(id=user_name_record.name_id)

                comments_formated.append({
                    "username": user_name.name,
                    "comment": comment.comment,
                    "rating": user_place.rating
                })

            places_data.append({
                "place": place_data,
                "photos": photo_formated,
                "categories": category_formated,
                "comments": comments_formated
            })

        except (PlacesPhotos.DoesNotExist,
                PlacesComments.DoesNotExist,
                Category.DoesNotExist,
                PlacesComments.DoesNotExist):
            pass

    return paginator.get_paginated_response(places_data)
