from django.db import models

# Create your models here.
class cas_client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    user = models.ForeignKey('client_user',on_delete=models.CASCADE)
    #url = models.URLField(max_length=1000)
    #img = models.CharField(max_length=1000)
    access = models.BooleanField()


class client_user(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.CharField(max_length=20, unique=True)

class client_list(models.Model):
    name = models.CharField(max_length=20, unique=True)
    url = models.URLField(max_length=1000)
    img = models.CharField(max_length=1000)
