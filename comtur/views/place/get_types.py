from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import PlaceTypes


@api_view(['GET'])
def get_types(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        types = PlaceTypes.objects.all()
    except PlaceTypes.DoesNotExist:
        return JsonResponse({'error': 'Categorias não encontradas'},
                            status=status.HTTP_404_NOT_FOUND)
    types_formated = []
    for type in types:
        types_formated.append({
            'id': type.id,
            'type': type.type
        })
    return JsonResponse({"success": True,
                         "tipos": types_formated},
                        status=status.HTTP_200_OK)
