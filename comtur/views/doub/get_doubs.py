from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import ComumDoubs


@api_view(['GET'])
def get_doub(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        questions = ComumDoubs.objects.all()
        if not questions.exists():
            return JsonResponse({
                "success": False,
                "message": "Não existem perguntas"
            }, status=status.HTTP_404_NOT_FOUND)

        # Formatar as perguntas
        formatted_questions = []
        for question in questions:
            img_doub = question.doub_photo
            photo_url = img_doub.url if img_doub else None

            formatted_question = {
                "id": question.id,
                "doub": question.doub,
                "doub_answer": question.doub_answer,
                "photo": photo_url
            }
            formatted_questions.append(formatted_question)

    except Exception as e:
        print("Erro:", e)  # Para debug
        return JsonResponse({
            "success": False,
            "message": "Erro ao buscar dúvidas"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    print(formatted_questions)
    return JsonResponse({
        "success": True,
        "message": "Dúvidas encontradas",
        "doubs": formatted_questions
    }, status=status.HTTP_200_OK)
