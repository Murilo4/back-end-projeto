from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...serializers.doub import DoubCreate


@api_view(['POST'])
def create_doub(request):
    if request.method != 'POST':
        return JsonResponse({'success': False,
                             'message': 'Método http invalido'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    doub = request.data.get("doub")
    doub_answer = request.data.get("doubAnswer")
    doub_photo = request.FILES.get("photo")

    if not doub and not doub_answer:
        return JsonResponse({"success": False,
                             "message": "dados necessarios não informados"},
                            status=status.HTTP_400_BAD_REQUEST)
    new_doub = {
        "doub": doub,
        "doub_answer": doub_answer,
        "doub_photo": doub_photo
    }

    serializer = DoubCreate(data=new_doub)

    if not serializer.is_valid():
        return JsonResponse({"success": False,
                             "message": "Não foi possivel criar a pergunta"},
                            status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return JsonResponse({"success": True,
                         "message": "Pergunta criada com sucesso"},
                        status=status.HTTP_201_CREATED)
