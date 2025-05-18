from django.db import models
from django.contrib.auth.models import User

from django_project import settings


class Doc(models.Model):
    file_path = models.TextField()
    size = models.IntegerField()


class UserToDoc(models.Model):
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    username = models.CharField(max_length=50)


class Price(models.Model):
    file_type = models.CharField(max_length=20)
    price = models.FloatField()


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    order_price = models.FloatField()
    payment = models.BooleanField(default=False)
