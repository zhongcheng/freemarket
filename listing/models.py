from django.contrib.auth.models import User
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


# need to update database (migrate) when change the structure of a class
class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=20)
    description = models.TextField(max_length=500, blank=True)
    city = models.CharField(max_length=20)
    contact_info = models.CharField(max_length=45)
    photo = models.FileField()
    time = models.DateField(auto_now=True)
    # photo_width = models.IntegerField(null=True)
    # photo_height = models.IntegerField(null=True)

    def add_item_save(self):
        img = Image.open(self.photo)
        output = BytesIO()
        img.save(output, format='JPEG', quality=60)
        output.seek(0)
        self.photo = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.photo.name.split('.')[0], 'image/jpeg', sys.getsizeof(output), None)
        super(Item, self).save()

    def __str__(self):
        return self.item_name

