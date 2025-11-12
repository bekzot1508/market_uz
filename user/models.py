from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models

# Create your models here.


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='users/', default='no_image_user.png', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'heic', 'heif'])])
    state = models.CharField(max_length=150)
    region = models.CharField(max_length=150)
    street  = models.CharField(max_length=150)
    house = models.CharField(max_length=150)