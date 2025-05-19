from django.db import models
from django.contrib.auth.models import User


class Doc(models.Model):
    server_id = models.IntegerField()
    file_type = models.TextField(max_length=20)
    size = models.IntegerField()


class UserToDoc(models.Model):
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Price(models.Model):
    file_type = models.CharField(max_length=20)
    price = models.FloatField()

    def __str__(self):
        return f'{self.id}: {self.file_type} - {self.price}/Kb'


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    order_price = models.FloatField()
    payment = models.BooleanField(default=False)
