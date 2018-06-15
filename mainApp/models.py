from django.contrib.auth.models import User
from django.db import models
from PIL import Image, ExifTags
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import os
from django.dispatch import receiver
from django.db.models.signals import post_save


# do not forget to update database (migrate) after changing the structure of a class


class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=20)
    description = models.TextField(max_length=500, blank=True)
    city = models.CharField(max_length=20)
    contact_info = models.TextField(max_length=200)
    photo = models.FileField()
    time = models.DateField(auto_now=True)
    photo_width = models.IntegerField(null=True)
    photo_height = models.IntegerField(null=True)

    def compress_image_save(self):
        img = Image.open(self.photo)
        output = BytesIO()
        img.save(output, format='JPEG', quality=30)
        output.seek(0)
        self.photo = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.photo.name.split('.')[0], 'image/jpeg', sys.getsizeof(output), None)
        super(Item, self).save()

    def __str__(self):
        return self.item_name


@receiver(post_save, sender=Item, dispatch_uid="update_item_photo")
def auto_rotate_photo(sender, instance, **kwargs):
    if instance.photo:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = base_dir + instance.photo.url
        try:
            image = Image.open(image_path)
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break

            exif = dict(image._getexif().items())

            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
            image.save(image_path)
            image.close()
        except (AttributeError, KeyError, IndexError):
            # cases: image don't have getexif
            pass

