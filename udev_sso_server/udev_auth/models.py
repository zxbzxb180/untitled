from django.db import models

# Create your models here.
class cas_client(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey('client_user', on_delete=models.CASCADE)
    access = models.BooleanField()


class client_user(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.CharField(max_length=255, unique=True)


class client_list(models.Model):
    name = models.CharField(max_length=255, unique=True)
    url = models.URLField(max_length=255, unique=True)
    callback = models.URLField(max_length=255, unique=True, null=True)
    img = models.ImageField(upload_to='images', max_length=255, null=True, blank=True)






