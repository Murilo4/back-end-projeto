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
        # Obtém todas as fotos
        photos = SlidesPhotos.objects.all()

        # Processa as URLs das fotos
        photos_url = []
        for photo in photos:
            photo_url = photo.img_url.url if photo.img_url else None
            photos_url.append(photo_url)

        # Cria o JSON de resposta
        slides_json = {"photos": photos_url}

        return JsonResponse({"success": True,
                             "message": "Fotos retornadas com sucesso",
                             "data": slides_json},
                            status=status.HTTP_200_OK)

    except SlidesPhotos.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Fotos não encontradas"},
                            status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({"success": False,
                             "message": f"Erro interno: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
