# Standard library imports
import io
import re

# Django imports
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models, transaction
from django.db.models.fields.files import ImageFieldFile
from django.utils import timezone
from django.db.models import Max


# Third-party library imports
from PIL import Image

class BaseModel(models.Model):
    allow_display = False
    excel_downloadable = False
    excel_uploadable = False
    last_saved = models.DateTimeField(default=timezone.now, blank=True, null=True)
    archived = models.BooleanField(default=False)
    lock = models.BooleanField(verbose_name="Khóa chỉnh sửa", default=False)

    class Meta:
        abstract = True  # Specify this model as Abstract

    def compress_image(self, image_field, max_width):
        try:
            # Open the uploaded image using PIL
            image_temp = Image.open(image_field)
        except FileNotFoundError:
            return  # Return from the method if the file is not found

        if '_compressed' in image_field.name:
            return image_field

        # Resize the image if it is wider than 600px
        if image_temp.width > max_width:
            # Calculate the height with the same aspect ratio
            height = int((image_temp.height / image_temp.width) * max_width)
            image_temp = image_temp.resize((max_width, height), Image.Resampling.LANCZOS)

        # Define the output stream for the compressed image
        output_io_stream = io.BytesIO()

        # Save the image to the output stream with desired quality
        image_temp.save(output_io_stream, format='WEBP', quality=80)
        output_io_stream.seek(0)

        # Create a Django InMemoryUploadedFile from the compressed image
        file_name = "%s_compressed.webp" % image_field.name.split('.')[0]
        output_imagefield = InMemoryUploadedFile(output_io_stream, 'ImageField', 
                                                 file_name, 
                                                 'image/webp', output_io_stream.getbuffer().nbytes, None)
        
        return output_imagefield

    def create_thumbnail(self, image_field):
        max_width = 60
        try:
            # Open the uploaded image using PIL
            image_temp = Image.open(image_field)
        except FileNotFoundError:
            return  # Return from the method if the file is not found

        height = int((image_temp.height / image_temp.width) * max_width)
        image_temp = image_temp.resize((max_width, height), Image.Resampling.LANCZOS)
        output_io_stream = io.BytesIO()

        # Save the image to the output stream with desired quality
        image_temp.save(output_io_stream, format='WEBP', quality=40)
        output_io_stream.seek(0)

        # Create a Django InMemoryUploadedFile from the compressed image
        file_name = "%s.thumbnail" % image_field.name.split('.')[0]
        output_imagefield = InMemoryUploadedFile(output_io_stream, 'ImageField', 
                                                 file_name, 
                                                 'image/webp', output_io_stream.getbuffer().nbytes, None)

        return output_imagefield

    def save(self, *args, **kwargs):
        # refine fields
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, ImageFieldFile):
                if value:  # If there's an image to compress
                    compressed_image = self.compress_image(value, 1000)
                    setattr(self, field.name, compressed_image)

                    if not Thumbnail.objects.filter(reference_url=value.url).exists():
                        thumbnail_image = self.create_thumbnail(value)
                        thumbnail = Thumbnail.objects.create(
                            reference_url=value.url,
                            thumbnail=None
                        )
                        setattr(thumbnail, 'thumbnail', thumbnail_image)
                        thumbnail.save()

            elif isinstance(value, str):
                # Remove leading and trailing whitespaces
                value = value.strip()
                # Replace multiple spaces with a single space
                value = re.sub(r' +', ' ', value)
                setattr(self, field.name, value)

        super().save(*args, **kwargs)

        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, ImageFieldFile):
                if value:  # If there's an image to create thumbnail
                    if not Thumbnail.objects.filter(reference_url=value.url).exists():
                        thumbnail_image = self.create_thumbnail(value)
                        thumbnail = Thumbnail.objects.create(
                            reference_url=value.url,
                            thumbnail=None
                        )
                        setattr(thumbnail, 'thumbnail', thumbnail_image)
                        thumbnail.save()

    @classmethod
    def get_vietnamese_name(cls):
        if hasattr(cls, 'vietnamese_name'):
            return cls.vietnamese_name
        else:
            return cls.__name__

    def save_lock(self):
        # Tránh tính toán thừa mà chỉ lock thôi
        super().save()

class Thumbnail(models.Model):
    reference_url = models.CharField(max_length=255, blank=True, null=True)
    thumbnail  = models.ImageField(upload_to='images/thumbnails/', blank=True, null=True)

class SecondaryIDMixin(models.Model):
    secondary_id = models.IntegerField(blank=True, null=True)
    class Meta:
        abstract = True  # This makes it a mixin, not a standalone model

    def save(self, *args, **kwargs):
        if self._state.adding and hasattr(self, 'project'):
            with transaction.atomic():
                highest_id = self.__class__.objects.filter(
                    project=self.project
                ).aggregate(max_secondary_id=Max('secondary_id'))['max_secondary_id'] or 0
                self.secondary_id = highest_id + 1
        super().save(*args, **kwargs)
