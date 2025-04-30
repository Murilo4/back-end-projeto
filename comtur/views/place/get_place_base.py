from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Places, PlacesPhotos, PlacesComments
from ...models import Category, UserName, Names, Partness


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


@api_view(['GET'])
def get_place_base_slides(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        # Busca os locais com base em medium_rate em ordem decrescente, limitando a 8
        places = Places.objects.all().order_by('-medium_rate')[:8]

        places_list = []
        for place in places:
            # Obtém o nome completo do local
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

            # Obtém as fotos do local
            photos = PlacesPhotos.objects.filter(place_photo=place.id)
            photos_url = [photo.img_url.url for photo in photos if photo.img_url]

            # Adiciona o local ao JSON de resposta
            places_list.append({
                "description": place.description,
                "workStart": place.work_start,
                "workStop": place.work_stop,
                "rating": place.medium_rate if place.medium_rate else 1,
                "placeName": full_name,
                "photos": photos_url,
                "slug": place.slug,
                "lowerPrice": place.lower_price,
            })

        return JsonResponse({
            "success": True,
            "message": "Locais retornados com sucesso",
            "places": places_list,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({"success": False,
                             "message": f"Erro interno: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_place_base_reviews(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        places = Places.objects.all().order_by('-rating_number')[:8]

        places_list = []
        for place in places:
            # Obtém o nome completo do local
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

            # Obtém as fotos do local
            photos = PlacesPhotos.objects.filter(place_photo=place.id)
            photos_url = [photo.img_url.url for photo in photos if photo.img_url]

            # Adiciona o local ao JSON de resposta
            places_list.append({
                "description": place.description,
                "workStart": place.work_start,
                "workStop": place.work_stop,
                "rating": place.medium_rate if place.medium_rate else 1,
                "placeName": full_name,
                "photos": photos_url,
                "slug": place.slug,
                "lowerPrice": place.lower_price,
            })

        return JsonResponse({
            "success": True,
            "message": "Locais retornados com sucesso",
            "places": places_list,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({"success": False,
                             "message": f"Erro interno: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_partness(request):
    if request.method != "GET":
        return JsonResponse({"success": False,
                             "message": "Método não permitido"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        get_partness = Partness.objects.all()
        partners = []
        for partner in get_partness:
            photo_url = partner.photo.url if partner.photo else None
            partners.append({
                "photo": photo_url,
                "name": partner.name,
                "facebook": partner.facebook,
                "instagram": partner.instagram,
                "x": partner.x,
                "linkedin": partner.linkedin
            })
    except Partness.DoesNotExist:
        return JsonResponse({"success": True,
                             "message": "Parceiros não localizados"},
                            status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"success": True,
                         "message": "Dados retornados",
                         "partness": partners},
                        status=status.HTTP_200_OK)
