from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Places, PlacesPhotos, PlaceCategories, PlacesComments
from ...models import Category, UserPlaces, UserName, Names, PlacesCity
from ...models import PlacesStates, Address, neighborhoodAddress, Neighborhood
from ...models import addressStreet, Street, City, HouseNumber, State


@api_view(['GET'])
def get_place(request, place_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        place = Places.objects.get(id=place_id)

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
        photos = PlacesPhotos.objects.filter(place_photo=place_id)
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
        photos = PlacesPhotos.objects.filter(
            place_photo=place.id)
        photos_url = []
        for photo in photos:
            photo_url = photo.img_url.url if photo.img_url else None
            photos_url.append(photo_url)

        try:
            address = Address.objects.get(place=place_id)
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
                "description": place.description,
                "type": place.type,
                "locationX": place.locationX,
                "locationY": place.locationY,
                "workStart": place.work_start,
                "workStop": place.work_stop,
                "about": place.about,
                "rating": place.rating_number if place.rating_number else 0,
                "placeName": full_name,
                "photos": photos_url,
                "categories": category_formated,
                'addressType': address.address_type,
                'addressName': full_name_address,
                "street": full_street_formated,
                "state": state.state,
                "number": number.number,
                "neighborhood": full_neighbor_formated,
                "city": city.city,
                "cep": address.postal,
                "comments": comments_formated,
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
