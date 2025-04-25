from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from django.core.mail import send_mail
from ...models import Places, NormalUser, City, PlacesCity
from dotenv import load_dotenv
import os
load_dotenv()
EMAIL = os.getenv('EMAIL')


@api_view(['POST'])
def send_validation_to_admin(request, placeId):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        # Obtém o local pelo placeId
        place = Places.objects.get(id=placeId)
        place_city = PlacesCity.objects.get(id=place.city)
        city = City.objects.get(city=place_city.city)
        if city:
            # Filtra os usuários administradores vinculados à mesma cidade
            admins = NormalUser.objects.filter(
                city_staff=city.id, is_staff=True)
        else:
            admins = NormalUser.objects.filter(is_staff=True)

        # Gera o link com o slug do local
        link = f'http://localhost:3000/validation-place/{place.slug}'

        # Texto pré-definido do e-mail
        subject = "Validação necessária para o local"
        message = f"Olá,\n\nPor favor, valide o local '{place.name}' acessando o link abaixo:\n\n{link}\n\nObrigado!"

        # Envia o e-mail para cada administrador
        for admin in admins:
            send_mail(
                subject,
                message,
                EMAIL,  # Substitua pelo e-mail do remetente
                [admin.email],
                fail_silently=False,
            )

        return JsonResponse({'success': True,
                             'message': 'E-mails enviados com sucesso!'},
                            status=status.HTTP_200_OK)

    except Places.DoesNotExist:
        return JsonResponse({'success': False,
                             'message': 'Local não encontrado'},
                            status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'success': False,
                             'message': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def process_place_approval(request, slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        # Obtém os dados do request
        slug = slug
        is_approved = request.data.get('is_approved')
        observation = request.data.get('observation', '')

        # Obtém o local pelo slug
        place = Places.objects.get(slug=slug)

        # Obtém o criador do local (enterprise)
        creator = NormalUser.objects.get(id=place.enterprise)

        # Define o assunto e a mensagem do e-mail com base na aprovação
        if is_approved:
            subject = "Local aprovado"
            message = f"Olá,\n\nO local '{place.name}' foi aprovado e está tudo certo. \nObservações: {observation}\n!"
        else:
            subject = "Alterações necessárias no local"
            message = f"Olá,\n\nO local '{place.name}' não foi aprovado. Por favor, revise as informações e faça as alterações necessárias.\n\nMotivo: {observation}\n!"

        # Envia o e-mail para o criador do local
        send_mail(
            subject,
            message,
            EMAIL,  # Substitua pelo e-mail do remetente
            [creator.email],
            fail_silently=False,
        )

        return JsonResponse({'success': True,
                             'message': 'e-mail enviado com sucesso!'},
                            status=status.HTTP_200_OK)

    except Places.DoesNotExist:
        return JsonResponse({'success': False,
                             'message': 'Local não encontrado'},
                            status=status.HTTP_404_NOT_FOUND)
    except NormalUser.DoesNotExist:
        return JsonResponse({'success': False,
                             'message': 'Criador do local não encontrado'},
                            status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'success': False,
                             'message': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
