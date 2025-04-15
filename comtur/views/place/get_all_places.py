from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.core.paginator import Paginator
from ...models import Places, PlacesPhotos, PlaceCategories, PlacesComments
from ...models import Category, PlacesRating, UserName, Names
from ...serializers.place import PlaceGetSerializer
from django.db.models import Q, Max, Min
from datetime import datetime


@api_view(['GET'])
def get_places(request, page_number):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    # Filtros de pesquisa
    categories = request.GET.get('category', None)
    # Use getlist to handle multiple types
    place_types = request.GET.getlist('type', None)
    search_text = request.GET.get('search', None)
    lower_price = request.GET.get('lowerPrice', None)
    higher_price = request.GET.get('higherPrice', None)

    try:
        lower_price = int(lower_price) if lower_price is not None else None
    except ValueError:
        lower_price = None

    try:
        higher_price = int(higher_price) if higher_price is not None else None
    except ValueError:
        higher_price = None

    min_stars = request.GET.get('minStars', 0)
    max_stars = request.GET.get('maxStars', 0)
    order_by = request.GET.get('orderBy', None)
    city = request.GET.get('city', None)
    state = request.GET.get('state', None)
    open_now = request.GET.get('openNow', None)

    if categories:
        categories = categories.split(',')

    # Calculate overall min and max prices before applying filters
    overall_price_min = Places.objects.aggregate(
        Min('lower_price')).get('lower_price__min', 0)
    overall_price_max = Places.objects.aggregate(
        Max('higher_price')).get('higher_price__max', 0)

    places_query = Places.objects.all()
    # Aplicar filtro de estado
    places_query = places_query.filter(
        is_place_valid=1
    )
    if state:
        places_query = places_query.filter(
            placesStates__state=state
        ).distinct()

    # Aplicar filtro de cidade
    if city:
        places_query = places_query.filter(
            city__city__icontains=city
        ).distinct()

    if categories:
        places_query = places_query.filter(
            placecategories__category__in=categories
        ).distinct()

    if place_types:
        places_query = places_query.filter(
            type__in=place_types
        ).distinct()

    if search_text:
        normalized_search_text = search_text.lower()
        places_query = places_query.filter(
            Q(username__name_id__in=Names.objects.filter(
                name__icontains=normalized_search_text).values_list(
                    'id', flat=True)) |
            Q(username__name_id__in=Names.objects.filter(
                # Handle pluralization
                name__icontains=normalized_search_text.rstrip(
                    's')).values_list('id', flat=True)) |
            Q(description__icontains=normalized_search_text) |
            Q(type__icontains=normalized_search_text) |
            Q(placecategories__category__icontains=normalized_search_text)
        ).distinct()

    if lower_price is not None:
        places_query = places_query.filter(lower_price__gte=lower_price)
    if higher_price is not None:
        places_query = places_query.filter(higher_price__lte=higher_price)
    if min_stars and min_stars != 0:
        places_query = places_query.filter(
            medium_rate__gte=min_stars)
    if max_stars and max_stars != 0:
        places_query = places_query.filter(
            medium_rate__lte=max_stars)
    if open_now and open_now.lower() == 'true':
        current_time = datetime.now().strftime('%H:%M')
        places_query = places_query.filter(
            work_start__lte=current_time,
            work_stop__gte=current_time
        ).distinct()
    if order_by:
        if order_by == 'name':
            places_query = places_query.order_by('name')
        elif order_by == 'price':
            places_query = places_query.order_by('price')
        elif order_by == 'rating':
            places_query = places_query.order_by('-userplaces__rating')
        elif order_by == 'date':
            places_query = places_query.order_by('-created_at')

    result_page = Paginator(places_query, 15)
    page_obj = result_page.get_page(page_number)

    places_data = []
    for place in page_obj:
        serializer = PlaceGetSerializer(place)
        place_data = serializer.data
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
        place_id = place.id

        try:
            photo = PlacesPhotos.objects.filter(place_photo=place_id).first()
            photo_formated = photo.img_url.url if photo else None

            category_sr_id = PlaceCategories.objects.filter(place=place_id)
            category_formated = []

            for category in category_sr_id:
                category_db = Category.objects.get(id=category.category)
                category_formated.append(category_db.category)

            comments = PlacesComments.objects.filter(
                place_comment=place_id).first()
            place_rating = 0
            try:
                place_rating_bd = PlacesRating.objects.filter(
                    place_rating=place_id)
                value = 0
                for place_rate in place_rating_bd:
                    if place_rate.rating is not None:
                        value += place_rate.rating
                        if place.rating_number != 0:
                            place_rating = (value) / place.rating_number
            except PlacesRating.DoesNotExist:
                pass

            places_data.append({
                "place": place_data,
                "placeName": full_name,
                "photo": photo_formated,
                "categories": category_formated,
                "comment": comments.comment if comments else None,
                "rating": place_rating,
            })
        except (PlacesPhotos.DoesNotExist,
                PlacesComments.DoesNotExist,
                Category.DoesNotExist,
                PlacesComments.DoesNotExist):
            pass

    return JsonResponse({"success": True,
                         "message": "Locais retornados",
                         "places": places_data,
                         "count": page_obj.paginator.count,
                         "hasNext": page_obj.has_next(),
                         "hasPrevious": page_obj.has_previous(),
                         "page": page_obj.number,
                         "totalPages": page_obj.paginator.num_pages,
                         "minPrice": overall_price_min,
                         "maxPrice": overall_price_max},
                        status=status.HTTP_200_OK)
