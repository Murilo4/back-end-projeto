from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Places, Names, UserName, PlacesCity, PlacesStates
from django.db.models import Q


@api_view(['GET'])
def search_suggestions(request):
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse({"success": False,
                             "message": "Query parameter is missing"},
                            status=status.HTTP_400_BAD_REQUEST)

    place_suggestions = Places.objects.filter(
        Q(description__icontains=query) |
        Q(id__in=UserName.objects.filter(
            name_id__in=Names.objects.filter(
                name__icontains=query).values('id')
        ).values('places_id'))
    )[:10]

    city_suggestions = PlacesCity.objects.filter(
        Q(city__icontains=query)
    )[:10]

    state_suggestions = PlacesStates.objects.filter(
        Q(state__icontains=query)
    )[:10]

    place_list = []
    for place in place_suggestions:
        try:
            user_names = UserName.objects.filter(
                places_id=place.id).order_by('create_order')
            name_parts = [Names.objects.get(
                id=user_name.name_id).name for user_name in user_names]
            name = ' '.join(name_parts)
        except UserName.DoesNotExist:
            continue
        except Names.DoesNotExist:
            continue

        place_list.append({
            "id": place.id,
            "name": name,
            "description": place.description
        })
    try:
        city_list = [{"id": city.id, "name": city.city}
                     for city in city_suggestions]
        state_list = [{"id": state.id, "name": state.state}
                      for state in state_suggestions]
    except (PlacesCity.DoesNotExist, PlacesStates.DoesNotExist):
        city_list = []
        state_list = []

    return JsonResponse({"success": True,
                         "places": place_list,
                         "cities": city_list,
                         "states": state_list},
                        status=status.HTTP_200_OK)
