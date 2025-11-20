from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from phonenumber_field.modelfields import PhoneNumberField

from django.db import models

# Create your models here.


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='users/', default='no_image_user.png', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'heic', 'heif'])])
    phone_number = PhoneNumberField(blank=True, null=True, unique=False)

    def __str__(self):
        # Odatda email yoki full name qaytariladi
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username