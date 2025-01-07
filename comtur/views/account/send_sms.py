# from rest_framework.decorators import api_view
# from twilio.rest import Client
# from django.http import JsonResponse
# import os
# from rest_framework import status
# from dotenv import load_dotenv
# load_dotenv()

# account_sid = os.getenv('SID')
# auth_token = os.getenv('AUTH_CODE')
# number = os.getenv('NUMBER')


# @api_view(['POST'])
# def send_sms_msg(request):
#     client = Client(account_sid, auth_token)

#     destinatario = "+5516991286532"
#     mensagem = "Mensagem de teste"

#     try:
#         message = client.messages.create(
#             body=mensagem,
#             from_=number,
#             to=destinatario
#         )
#         return JsonResponse({"success": True,
#                             "message":
#                              f"SMS enviado com sucesso! SID: {
# message.body}"},
#                             status=status.HTTP_200_OK)
#     except Exception as e:
#         return JsonResponse({"message": f"Erro ao enviar SMS: {str(e)}"})
