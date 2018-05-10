from django.contrib.auth.models import User, AbstractUser
from django.db import models


# need to update database (migrate) when change the structure of a class
class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=50)
    description = models.TextField(max_length=500, blank=True)
    city = models.CharField(max_length=50)
    contact_info = models.CharField(max_length=200)
    photo = models.FileField()

    def __str__(self):
        return self.item_name

