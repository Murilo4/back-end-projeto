from django.db import models


class Names(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        managed = False
        db_table = 'Names'


class NormalUser(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=45)
    phone = models.CharField(max_length=25)
    password = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'NormalUser'


class UserName(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.ForeignKey(Names, on_delete=models.CASCADE)
    user = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    create_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'UserName'


class userSession(models.Model):
    id = models.IntegerField(primary_key=True)
    user_session = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    session_token = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'UserSession'


# class EnterpriseUser(models.Model):
#     username = models.ForeignKey(Names, on_delete=models.CASCADE)
#     email = models.EmailField(unique=True)
#     cnpj = models.IntegerField(primary_key=True)
#     password = models.CharField(max_length=255)

#     class Meta:
#         db_table = 'EnterpriseUser'
