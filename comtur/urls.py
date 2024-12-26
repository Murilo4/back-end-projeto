from django.urls import path
from .views.account.user_creation import create_user
from .views.account.login_user import login_user_with_cpf
from .views.account.get_user import get_user_profile
from .views.account.send_validation_code import email_validation
from .views.account.send_validation_code import verify_email_code
from .views.account.update_account import update_user
from .views.account.delete_account import delete_user
# from .views.account.address.add_address import create_address
# from .views.account.address.get_address import get_one_address
# from .views.account.address.update_address import update_address
# from .views.account.address.delete_address import delete_address
from .views.account.update_account import password_reset
from .views.account.update_account import PasswordResetConfirm
from .views.place.create_place import create_place
# from .views.place.delete_place import delete_place
from .views.place.get_place import get_place
from .views.place.update_place import update_place
from .views.place.delete_place import delete_place


urlpatterns = [
    # User
    path('create/',
         create_user, name="create_user"),
    path('login/',
         login_user_with_cpf, name="login_cpf"),
    path("user-profile/",
         get_user_profile, name="get-user-profile"),
    path("email-validation/",
         email_validation, name="email-validation"),
    path("verify-email-code/",
         verify_email_code, name="verify-email-code"),
    path("update-user/",
         update_user, name="update-user"),
    path("delete-user/",
         delete_user, name="delete_user"),
    # Address
#     path("create-address/",
#          create_address, name="create_address"),
#     path("get-address/",
#          get_one_address, name="get_one_address"),
#     path("update-address/",
#          update_address, name="update_address"),
#     path("delete-address/",
#          delete_address, name="delete_address"),
    # Password Reset
    path('request-reset/',
         password_reset, name='request-reset'),
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirm, name='password-reset-confirm'),
    path('create-place/',
         create_place, name="create_place"),
    # path('delete-place/', delete_place, name="delete_place"),
    path('get-place/',
         get_place, name="get_place"),
    path('update-place/',
         update_place, name="update_place"),
    path('delete-place/', delete_place, name="delete_place"),

]
