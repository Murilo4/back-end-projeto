from django.db import models


class Names(models.Model):
    id = models.IntegerField(null=True)
    name = models.CharField(max_length=255, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Names'


class City(models.Model):
    id = models.IntegerField(primary_key=True)
    city = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'City'


class NormalUser(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=45, unique=True, null=True)
    cnpj = models.CharField(max_length=45, unique=True, null=True)
    user_type = models.CharField(max_length=45)
    phone = models.CharField(max_length=25)
    password = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='user_photos/',
                              blank=True, null=True)
    is_validated = models.BooleanField(default=0)
    last_pass_change = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    staff_city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)

    class Meta:
        managed = False
        db_table = 'NormalUser'


class lastPasswords(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.IntegerField()
    password_hash = models.CharField(max_length=255)
    changed_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'lastPasswords'


class PlacesStates(models.Model):
    id = models.IntegerField(primary_key=True)
    state = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'PlacesStates'


class PlacesCity(models.Model):
    id = models.IntegerField(primary_key=True)
    city = models.CharField(max_length=255)
    placeState = models.ForeignKey(PlacesStates, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'PlacesCity'


class Places(models.Model):
    id = models.IntegerField(primary_key=True)
    city = models.ForeignKey(PlacesCity, on_delete=models.CASCADE)
    description = models.TextField()
    rating_number = models.IntegerField(null=True, blank=True)
    comments_number = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=255)
    locationX = models.TextField(null=True, blank=True)
    locationY = models.TextField(null=True, blank=True)
    work_start = models.CharField(max_length=255)
    work_stop = models.CharField(max_length=255)
    lower_price = models.IntegerField()
    higher_price = models.IntegerField()
    about = models.TextField()
    enterprise = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    medium_rate = models.FloatField()
    slug = models.SlugField(max_length=255, unique=True)
    is_place_valid = models.BooleanField(default=0)
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


class Plans(models.Model):
    id = models.IntegerField(primary_key=True)
    price = models.IntegerField()
    plan_type = models.CharField(max_length=255)
    plan_name = models.CharField(max_length=255)
    belonging_system = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Plans'


class Subscription(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10)
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE)
    subscription_data = models.DateTimeField(auto_now=True)
    images_allowed = models.IntegerField()
    videos_allowed = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'subscription'


class PlansConfig(models.Model):
    id = models.IntegerField(primary_key=True)
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE)
    videos_allowed = models.BooleanField()
    points_multiplier = models.IntegerField()
    number_events = models.IntegerField()
    image_on_questions = models.BooleanField()
    number_images = models.IntegerField()
    number_videos = models.IntegerField()
    places_allowed = models.IntegerField()
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
    img_url = models.ImageField(upload_to='place_photos/',
                                blank=True, null=True)
    description = models.CharField(max_length=255)
    place_photo = models.ForeignKey(Places, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'PlacesPhotos'


class UserPlaces(models.Model):
    id = models.IntegerField(primary_key=True)
    user_place = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    place = models.ForeignKey(Places, on_delete=models.CASCADE)
    favorite = models.BooleanField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'userPlaces'


class PlacesComments(models.Model):
    id = models.IntegerField(primary_key=True)
    comment = models.TextField()
    place_comment = models.ForeignKey(Places, on_delete=models.CASCADE)
    user_comment = models.ForeignKey(UserPlaces, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'PlacesComments'


class PlacesRating(models.Model):
    id = models.IntegerField(primary_key=True)
    rating = models.IntegerField()
    place_rating = models.ForeignKey(Places, on_delete=models.CASCADE)
    user_place = models.ForeignKey(UserPlaces, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'PlacesRating'


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


class PlacesGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    group_name = models.CharField(max_length=255)
    # main_place = models.ForeignKey(Places, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "placesGroups"


class PlacesBranch(models.Model):
    id = models.IntegerField(primary_key=True)
    # branch = models.ForeignKey(Places, on_delete=models.CASCADE)
    # place_group = models.ForeignKey(PlacesGroups, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "placesBranch"


class PlaceTypes(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "placesTypes"


class ComumDoubs(models.Model):
    id = models.IntegerField(primary_key=True)
    doub = models.TextField()
    doub_answer = models.TextField()
    doub_photo = models.ImageField(upload_to='doub_photos/',
                                   blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ComumDoubs"


class CityHistory(models.Model):
    id = models.IntegerField(primary_key=True)
    city = models.CharField(max_length=255)
    history = models.TextField()

    class Meta:
        managed = False
        db_table = "CityHistory"
