from django.urls import path
from .views.account.user_creation import create_user
from .views.account.login_user import login_user_with_cpf
from .views.account.login_user import login_user_with_email
from .views.account.get_user import get_user_profile
from .views.account.send_validation_code import email_validation
from .views.account.send_validation_code import verify_email_code
from .views.account.update_account import update_user
from .views.account.delete_account import delete_user
from .views.account.update_account import update_user_photo
from .views.address.add_address import create_address
from .views.address.get_address import get_one_address
from .views.address.get_all_address import get_all_address
from .views.address.update_address import update_address
from .views.plans.get_all_plans import get_all_plans
from .views.address.delete_address import delete_address
from .views.account.update_account import password_reset
from .views.account.update_account import password_reset_confirm
from .views.account.update_account import password_forgot_change
from .views.account.update_account import forgot_password
from .views.place.create_place import create_place
from .views.place.delete_place import delete_place
from .views.account.get_place import get_place
from .views.place.update_place import update_place
from .views.user_place.add_comment import create_comment
from .views.user_place.update_comment import update_comment
from .views.user_place.delete_comment import delete_comment
from .views.place.get_user_place import get_place_user
from .views.user_place.add_rating import create_rating
from .views.user_place.update_rating import update_rating
from .views.user_place.delete_rating import delete_rating
from .views.user_place.add_favorite import set_favorite
from .views.account.user_creation import validate_jwt
from .views.account.user_creation import generate_new_token
from .views.account.send_sms import send_message
from .views.place.get_categories import get_categories
from .views.place.get_types import get_types
from .views.search_new_places.search import search_suggestions
from .views.account.account_type import get_user_type
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # User
    path('create/',
         create_user, name="create_user"),
    path('login/',
         login_user_with_cpf, name="login_cpf"),
    path('login-email/',
         login_user_with_email, name="login_email"),
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
    path("validate-token/",
         validate_jwt, name="validate_jwt"),
    path("generate-new-token/",
         generate_new_token, name="generate_new_token"),
    path("update-user-photo/",
         update_user_photo, name="update_user_photo"),
    path("get-user-type/",
         get_user_type, name="get_user_type"),
    # Address
    path("create-address/",
         create_address, name="create_address"),
    path("get-address/<token>/",
         get_one_address, name="get_one_address"),
    path("update-address/<token>/",
         update_address, name="update_address"),
    path("delete-address/<token>/",
         delete_address, name="delete_address"),
    # Password Reset
    path('request-reset/',
         password_reset, name='request-reset'),
    path('reset/',
         password_reset_confirm, name='password-reset-confirm'),
    path('forgot-password/',
         forgot_password, name='forgot-password'),
    path('forgot-password-change/',
         password_forgot_change, name='forgot-password-change'),
    # Place
    path('create-place/',
         create_place, name="create_place"),
    path('delete-place/', delete_place, name="delete_place"),
    path('get-place/<int:place_id>/',
         get_place, name="get_place"),
    path("get-all-address/",
         get_all_address, name="get_all_address"),
    path('update-place/',
         update_place, name="update_place"),
    path('get-user-places/',
         get_place_user, name="get_place_user"),
    path('delete-place/', delete_place, name="delete_place"),
    # user place
    path('create-comment/', create_comment, name='create_comment'),
    path('update-comment/', update_comment, name='update_comment'),
    path('delete-comment/', delete_comment, name='delete_comment'),
    path('create-rating/', create_rating, name='create_rating'),
    path('update-rating/', update_rating, name='update_rating'),
    path('delete-rating/', delete_rating, name='delete_rating'),
    path('set-favorite/', set_favorite, name='set_favorite'),

    # path('send-sms/', send_sms_msg, name='send_sms_msg'),
    path("send-message/", send_message, name="send_message"),
    path("get-all-plans/",
         get_all_plans, name="get_all_plans"),
    path("search-suggestions/", search_suggestions, name="search_suggestions"),
    path("get-categories/",
         get_categories, name="get_categories"),
    path("get-types/",
         get_types, name="get_types"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
