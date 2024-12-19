from rest_framework.decorators import api_view, throttle_classes
from django.http import JsonResponse
from rest_framework import status
from ...models import Places, PlacesPhotos
from ...throttles import DailyRateThrottle, HourlyRateThrottle
from ...throttles import MinuteRateThrottleAnon
from ...serializers.place import PlaceGetSerializer

@api_view(['GET'])
@throttle_classes([
    MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
def create_place(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        place_id = request.data.get('placeId')
        place = Places.objects.get(id=place_id)
        place_serializer = PlaceGetSerializer(place)
    except Places.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Local não encontrado"},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        photo = PlacesPhotos.objects.get(place=place_id)
    except PlacesPhotos.DoesNotExist:
        pass

    formated_place = []
    formated_place.append(**place_serializer, )
    return JsonResponse({"success": True,
                         "message": "Local encontrado",
                         "place": place.data})
