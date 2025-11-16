from django.utils import timezone

from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db import models
import json
from django.utils.text import slugify

from user.models import CustomUser


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
    image = models.ImageField(
        upload_to='products/',
        default='no_image.jpg',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'png', 'jpeg', 'heic', 'heif']
        )]
    )
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


# 🆕 O‘chirilgan mahsulotlar uchun snapshot
class OrderItemSnapshot(models.Model):
    product_id = models.IntegerField()             # O‘sha vaqtdagi Product ID
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255)       # Image URL yoki file path
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} x {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('confirmed', 'Tasdiqlandi'),
        ('shipped', 'Yuborildi'),
        ('delivered', 'Yetkazildi'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.JSONField(default=dict)  # Savat (product_id: quantity)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Yetkazib berish ma’lumotlari
    full_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    note = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    # 🆕 Snapshotlarni bog‘lash
    snapshots = models.ManyToManyField(OrderItemSnapshot, blank=True)

    def __str__(self):
        return f"Buyurtma #{self.id} - {self.user.username}"


class ProductReview(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    stars_given = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update average rating and review count
        reviews = ProductReview.objects.filter(product=self.product)
        self.product.review_count = reviews.count()
        self.product.average_rating = reviews.aggregate(models.Avg('stars_given'))['stars_given__avg'] or 0
        self.product.save()

    def __str__(self):
        return f'{self.stars_given} stars for {self.product.name} by {self.user.username}'
