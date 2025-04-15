from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Places, UserName, Names, PlacesCity, Neighborhood
from ...models import PlacesStates, Address, neighborhoodAddress, State
from ...models import addressStreet, Street, City, HouseNumber


@api_view(['GET'])
def get_place_address(request, slug):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        place = Places.objects.get(slug=slug)

        city = PlacesCity.objects.get(id=place.city.id)
        state = PlacesStates.objects.get(id=city.placeState.id)
    except Places.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Local não encontrado"},
                            status=status.HTTP_404_NOT_FOUND)

    try:
        address = Address.objects.get(place=place.id)
    except Address.DoesNotExist:
        return JsonResponse({'success': False,
                             'message': 'Endereço não encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)

    try:
        neighbor_address = neighborhoodAddress.objects.filter(
            address=address.id).order_by('neighbor_order')
        new_neighbor = []
        for name in neighbor_address:
            try:
                name_obj = Neighborhood.objects.get(
                    id=name.neighborhood.id)
                new_neighbor.append(name_obj.neighborhood)
            except Neighborhood.DoesNotExist:
                continue
        full_neighbor_formated = " ".join(new_neighbor)

    except (neighborhoodAddress.DoesNotExist, Neighborhood.DoesNotExist):
        return JsonResponse({'success': False,
                             'message': 'Bairro não encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        name_address = addressStreet.objects.filter(
            address=address.id).order_by('street_order')
        full_name_st = []
        for name in name_address:
            try:
                name_obj = Street.objects.get(
                    id=name.street.id)
                full_name_st.append(name_obj.street)
            except Street.DoesNotExist:
                continue
        full_street_formated = " ".join(full_name_st)
    except (Street.DoesNotExist, addressStreet.DoesNotExist):
        return JsonResponse({'success': False,
                             'message': 'Rua não encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)

    try:
        name_address = UserName.objects.filter(
            address=address.id).order_by('create_order')
        full_name_ad = []
        for name in name_address:
            try:
                name_obj = Names.objects.get(
                    id=name.name_id)
                full_name_ad.append(name_obj.name)
            except Names.DoesNotExist:
                continue

        full_name_address = " ".join(full_name_ad)
    except (Names.DoesNotExist, UserName.DoesNotExist):
        return JsonResponse({'success': False,
                             'message': 'Nome não encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)

    try:
        city = City.objects.get(id=address.city.id)
        number = HouseNumber.objects.get(id=address.number.id)
        state = State.objects.get(id=address.state.id)
    except (City.DoesNotExist, HouseNumber.DoesNotExist):
        return JsonResponse({'success': False,
                             'message':
                             'Não foi possivel retornar o endereço'},
                            status=status.HTTP_404_NOT_FOUND)
    place_json = {
        'addressName': full_name_address,
        "street": full_street_formated,
        "state": state.state,
        "number": number.number,
        "neighborhood": full_neighbor_formated,
        "city": city.city,
        "cep": address.postal,
    }

    return JsonResponse({
        "success": True,
        "message": "Local encontrado",
        "place": place_json,
    })
