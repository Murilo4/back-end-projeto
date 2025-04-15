from rest_framework.decorators import api_view
from ...models import Subscription, Plans, PlansConfig, NormalUser
from django.http import JsonResponse
from rest_framework import status
import jwt
from dotenv import load_dotenv
import os
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


@api_view(['GET'])
def get_plan_user(request):
    if request.method != 'GET':
        return JsonResponse({'success': False,
                            'message': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({"success": False,
                             "message":
                             "Token de acesso não fornecido"},
                            status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('id')
        user = NormalUser.objects.get(id=user_id)
    except jwt.ExpiredSignatureError:
        return JsonResponse({"success": False,
                             "message": "Token expirado."},
                            status=status.HTTP_401_UNAUTHORIZED)
    try:
        subscription = Subscription.objects.get(user=user.id)

        plan = Plans.objects.get(subscription=subscription.id)
        plan_config = PlansConfig.objects.get(plan=plan.id)
        plan_data = {
            'placesAllowed': plan_config.places_allowed,
        }

        return JsonResponse({'success': True,
                            'message': 'Dados retornados',
                             'plan': plan_data},
                            status=status.HTTP_200_OK)

    except (Subscription.DoesNotExist, Plans.DoesNotExist):
        return JsonResponse({'success': False,
                             'message': 'Plan not found'},
                            status=status.HTTP_404_NOT_FOUND)
