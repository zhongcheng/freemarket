from django.contrib.auth.models import User
from django.db import models
from PIL import Image, ExifTags
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver


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

        # auto rotate image based on EXIF data
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break

            exif = dict(img._getexif().items())

            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)

        except (AttributeError, KeyError, IndexError):
            # cases: image don't have getexif
            pass

        output = BytesIO()
        img.save(output, format='JPEG', quality=30)
        output.seek(0)
        self.photo = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.photo.name.split('.')[0], 'image/jpeg', sys.getsizeof(output), None)
        super(Item, self).save()

    def __str__(self):
        return self.item_name


# remove the corresponding image file after deleting an Item object
@receiver(post_delete, sender=Item)
def item_photo_file_delete(sender, instance, **kwargs):
    instance.photo.delete(False)

