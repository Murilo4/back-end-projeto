from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import PlaceCategories, PlacesComments
from ...models import Category, UserPlaces, UserName, Names


@api_view(['GET'])
def get_place_lists(request, place_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        category_sr_id = PlaceCategories.objects.filter(place=place_id)
        category_formated = []

        for category in category_sr_id:
            category_db = Category.objects.get(id=category.category)
            category_formated.append(category_db.category)

        comments_formated = []
        comments = PlacesComments.objects.filter(place_comment=place_id)
        for comment in comments:
            user_place = UserPlaces.objects.get(id=comment.user_comment.id)

            # Obter o nome do usuário
            user_name_record = UserName.objects.get(
                user_id=user_place.user_place.id)  # Acesso ao ID do usuário
            full_name = []
            for user_name_ in user_name_record:
                user_name = Names.objects.get(id=user_name_.name_id)
                full_name.append(user_name.name)

            comments_formated.append({
                "username": full_name,
                "comment": comment.comment,
                "rating": user_place.rating
            })

        place_json = {
                "categories": category_formated,
                "comments": comments_formated,
            }
    except (PlacesComments.DoesNotExist,
            Category.DoesNotExist):
        pass

    return JsonResponse({
        "success": True,
        "message": "Local encontrado",
        "place": place_json,
    })
