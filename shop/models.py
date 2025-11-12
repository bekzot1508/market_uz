from django.core.validators import FileExtensionValidator
from django.db import models
import json
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='products/', default='no_image.jpg', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'heic', 'heif'])])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    extra_data = models.TextField(blank=True, default="{}")
    average_rating = models.FloatField(default=0)
    review_count = models.PositiveIntegerField(default=0)

    def get_extra_data_dict(self):
        try:
            return json.loads(self.extra_data)
        except json.JSONDecodeError:
            return {}

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_discounted_price(self):
        return self.discount_price or self.price

    def __str__(self):
        return self.name
