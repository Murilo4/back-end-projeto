from django.db import models


class Names(models.Model):
    id = models.IntegerField(null=True)
    name = models.CharField(max_length=255, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Names'


class NormalUser(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=45, unique=True, null=True)
    cnpj = models.CharField(max_length=45, unique=True, null=True)
    user_type = models.CharField(max_length=45)
    phone = models.CharField(max_length=25)
    password = models.CharField(max_length=255)
    photo = models.CharField(max_length=255, null=True)
    is_validated = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'NormalUser'


class UserName(models.Model):
    id = models.IntegerField(primary_key=True)
    name_id = models.IntegerField()
    user_id = models.IntegerField()
    create_order = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'UserName'


class userSession(models.Model):
    id = models.IntegerField(primary_key=True)
    user_session = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    session_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'UserSession'


class Subscription(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10)
    subscription_data = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'Subscription'


class Plans(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=255)
    price = models.IntegerField()
    Subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Plans'


class PlansConfig(models.Model):
    id = models.IntegerField(primary_key=True)
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE)
    number_images = models.IntegerField()
    videos_allowed = models.BooleanField()
    number_videos = models.IntegerField()
    points_multiplier = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'PlansConfig'


class State(models.Model):
    id = models.IntegerField(primary_key=True)
    state = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'State'


class HouseNumber(models.Model):
    id = models.IntegerField(primary_key=True)
    number = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'HouseNumber'


class Address(models.Model):
    id = models.IntegerField(primary_key=True)
    user_address = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    neighborhood = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postal = models.CharField(max_length=255)
    neighborhood = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Address'


class StateAddress(models.Model):
    id = models.IntegerField(primary_key=True)
    state = models.IntegerField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'StateAddress'


class NumberAddress(models.Model):
    id = models.IntegerField(primary_key=True)
    house_number = models.IntegerField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'NumberAddress'


class Places(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.TextField()
    rating = models.IntegerField()
    rating_number = models.IntegerField()
    type = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    locationX = models.IntegerField()
    locationY = models.IntegerField()
    work_start = models.TimeField()
    work_stop = models.TimeField()
    about = models.TextField()
    enterprise = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Places'


class PlacesPhotos(models.Model):
    id = models.IntegerField(primary_key=True)
    img_url = models.TextField()
    description = models.CharField(max_length=255)
    place = models.ForeignKey(Places, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'PlacesPhotos'


class PlacesComments(models.Model):
    id = models.IntegerField(primary_key=True)
    comment = models.TextField()
    place_comment = models.ForeignKey(Places, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'PlacesComments'


class UserPlaces(models.Model):
    id = models.IntegerField(primary_key=True)
    user_place = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    place_user = models.ForeignKey(Places, on_delete=models.CASCADE)
    favorite = models.BooleanField()
    comments = models.ForeignKey(PlacesComments, on_delete=models.CASCADE)
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'userPlaces'


class PlaceCategories(models.Model):
    id = models.IntegerField(primary_key=True)
    category = models.IntegerField()
    place = models.ForeignKey(Places, on_delete=models.CASCADE)


class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    category = models.CharField(max_length=100)
