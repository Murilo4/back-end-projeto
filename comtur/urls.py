from django.urls import path
from .views.user_creation import create_user
from .views.login_user import login_user_with_cpf
from .views.get_user import get_user_profile

urlpatterns = [
    path('create/', create_user, name="create_user"),
    path('login-cpf/', login_user_with_cpf, name="login_cpf"),
    path("user-profile/", get_user_profile, name="get-user-profile"),
]
