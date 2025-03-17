from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Category


@api_view(['GET'])
def get_categories(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        categories = Category.objects.all()
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Categorias não encontradas'},
                            status=status.HTTP_404_NOT_FOUND)
    categories_formated = []
    for category in categories:
        categories_formated.append({
            'id': category.id,
            'category': category.category
        })
    return JsonResponse({"success": True,
                         "categories": categories_formated},
                        status=status.HTTP_200_OK)
