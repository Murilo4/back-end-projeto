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


class lastPasswords(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    password_hash = models.CharField(max_length=255)
    changed_at = models.TimeField()


class Places(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.TextField()
    rating = models.IntegerField(null=True, blank=True)
    rating_number = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=255)
    locationX = models.TextField(null=True, blank=True)
    locationY = models.TextField(null=True, blank=True)
    work_start = models.CharField(max_length=255)
    work_stop = models.CharField(max_length=255)
    about = models.TextField()
    enterprise = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Places'


class Neighborhood(models.Model):
    id = models.IntegerField(primary_key=True)
    neighborhood = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'Neighborhood'


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


class City(models.Model):
    id = models.IntegerField(primary_key=True)
    city = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'City'


class Address(models.Model):
    id = models.IntegerField(primary_key=True)
    user_address = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    postal = models.CharField(max_length=255)
    number = models.ForeignKey(HouseNumber, on_delete=models.CASCADE)
    address_type = models.CharField(max_length=255)
    place = models.ForeignKey(Places, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Address'


class UserName(models.Model):
    id = models.IntegerField(primary_key=True)
    name_id = models.IntegerField()
    user_id = models.IntegerField()
    places = models.ForeignKey(Places, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
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
    images_allowed = models.IntegerField()
    videos_allowed = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'subscription'


class Plans(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=255)
    price = models.IntegerField()
    Subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=255)
    plan_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Plans'


class PlansConfig(models.Model):
    id = models.IntegerField(primary_key=True)
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE)
    images_allowed = models.IntegerField()
    videos_allowed = models.BooleanField()
    points_multiplier = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'PlansConfig'


class neighborhoodAddress(models.Model):
    id = models.IntegerField(primary_key=True)
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    neighbor_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'neighborhoodAddress'


class Street(models.Model):
    id = models.IntegerField(primary_key=True)
    street = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'Street'


class addressStreet(models.Model):
    id = models.IntegerField(primary_key=True)
    street = models.ForeignKey(Street, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    street_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'AddressStreet'


class PlacesPhotos(models.Model):
    id = models.IntegerField(primary_key=True)
    img_url = models.TextField()
    description = models.CharField(max_length=255)
    place_photo = models.ForeignKey(Places, on_delete=models.CASCADE)
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

    class Meta:
        managed = False
        db_table = "placeCategories"


class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    category = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "category"
