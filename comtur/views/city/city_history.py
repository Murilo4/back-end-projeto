from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import CityHistory
from ...serializers.city_history import CityHistoryCreate, CityHistoryUpdate


@api_view(['POST'])
def create_history(request, city):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    history = request.data.get("history", None)

    if not history:
        return JsonResponse({'error': 'History is required'},
                            status=status.HTTP_400_BAD_REQUEST)

    history_create = CityHistoryCreate(data={"history": history,
                                             "city": city})
    if history_create.is_valid():
        history_create.save()
        return JsonResponse({'success': True,
                             'message': 'History created successfully!'},
                            status=status.HTTP_201_CREATED)
    else:
        return JsonResponse({'error': history_create.errors},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_history(request, city):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        history = CityHistory.objects.get(city=city)
    except CityHistory.DoesNotExist:
        return JsonResponse({'error': 'History not found'},
                            status=status.HTTP_404_NOT_FOUND)

    return JsonResponse({'success': True,
                        'message': 'History retrieved successfully!',
                         'history': history.history},
                        status=status.HTTP_200_OK)


@api_view(['PUT'])
def update_history(request, city):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    history = request.data.get("history", None)

    if not history:
        return JsonResponse({'error': 'History is required'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        city_history = CityHistory.objects.get(city=city)
    except CityHistory.DoesNotExist:
        return JsonResponse({'error': 'History not found'},
                            status=status.HTTP_404_NOT_FOUND)

    update_city = CityHistoryUpdate(city_history, data={"history": history,
                                                        "city": city})
    if not update_city.is_valid():
        return JsonResponse({'error': update_city.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    update_city.save()

    return JsonResponse({'success': True,
                         'message': 'History updated successfully!'},
                        status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_history(request, city):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        city_history = CityHistory.objects.get(city=city)
        city_history.delete()
        return JsonResponse({'success': True,
                             'message': 'History deleted successfully!'},
                            status=status.HTTP_200_OK)
    except CityHistory.DoesNotExist:
        return JsonResponse({'error': 'History not found'},
                            status=status.HTTP_404_NOT_FOUND)
