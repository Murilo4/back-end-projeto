from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import status
from ...models import SlidesPhotos


@csrf_exempt
@api_view(['GET'])
def get_slides(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        photos = SlidesPhotos.objects.all()

    except SlidesPhotos.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Local não encontrado"},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        photos_url = []
        for photo in photos:
            photo_url = photo.img_url.url if photo.img_url else None
            photos_url.append(photo_url)
        slides_json = {
            "photos": photos_url,
        }
    except (SlidesPhotos.DoesNotExist):
        return JsonResponse({"success": False,
                             "message": "Fotos não encontrados"},
                            status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({"success": True,
                        "message": "fotos retornados",
                         "photos": slides_json},
                        status=status.HTTP_200_OK)
