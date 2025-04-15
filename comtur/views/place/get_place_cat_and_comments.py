from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import PlaceCategories, PlacesComments, PlacesRating
from ...models import Category, UserPlaces, UserName, Names, NormalUser
import jwt
from dotenv import load_dotenv
import os
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_place_lists(request, slug):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get('id')
    except Exception:
        user_id = None
    try:
        category_sr_id = PlaceCategories.objects.filter(place__slug=slug)
        category_formated = []

        for category in category_sr_id:
            category_db = Category.objects.get(id=category.category)
            category_formated.append(category_db.category)

        comments_formated = []
        comments = PlacesComments.objects.filter(
            place_comment__slug=slug)
        for comment in comments:
            user_place = UserPlaces.objects.get(id=comment.user_comment.id)
            user_rating = PlacesRating.objects.get(
                user_place=user_place.id)
            if user_id:
                if (user_id == user_place.user_place.id):
                    user_has_comment = True
                else:
                    user_has_comment = False
            # Obter o nome do usuário
            user_name_record = UserName.objects.filter(
                user_id=user_place.user_place.id)  # Acesso ao ID do usuário
            full_name = []
            photo = NormalUser.objects.get(id=user_place.user_place.id)
            # Verifica se o usuário tem foto
            if photo.photo:
                user_photo = user_place.photo = photo.photo.url
            else:
                user_photo = user_place.photo = None
            for user_name_ in user_name_record:
                user_name = Names.objects.get(id=user_name_.name_id)
                full_name.append(user_name.name)
            full_name = " ".join(full_name)
            comments_formated.append({
                "username": full_name,
                "photo": user_photo,
                "comment": comment.comment,
                "date": comment.created_at,
                "rating": user_rating.rating if user_rating else None,
                "userHasComment": user_has_comment,
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
