from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from rest_framework import status
from ..models import NormalUser
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user_cpf = request.user.email
        user = NormalUser.objects.get(cpf=user_cpf)

        user_data = {
            'email': user.email,
            'cpf': user.cpf,
            'phone': user.phone,
        }

        return JsonResponse({"sucess": True,
                             "data": user_data}, 
                            status=status.HTTP_200_OK)
    except:
        return JsonResponse({"error": "User not found"},
                            status=status.HTTP_404_NOT_FOUND)
    