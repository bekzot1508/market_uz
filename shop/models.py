from django.utils import timezone
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify
from user.models import CustomUser


class StoreSettings(models.Model):
    store_name = models.CharField(max_length=200, default="My Store")
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # Home content
    homepage_title = models.CharField(max_length=255, blank=True)
    homepage_subtitle = models.CharField(max_length=255, blank=True)
    homepage_banner = models.ImageField(upload_to='settings/', blank=True, null=True)

    # Order settings
    free_delivery_min = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # General
    maintenance_mode = models.BooleanField(default=False)  # site ni vaqtincha o‘chirish
    items_per_page = models.PositiveIntegerField(default=12)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Store Settings"

    class Meta:
        verbose_name = "Store Settings"
        verbose_name_plural = "Store Settings"




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

    # ✅ JSONField instead of TextField
    extra_data = models.JSONField(blank=True, default=dict)
    average_rating = models.FloatField(default=0)
    review_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_discounted_price(self):
        return self.discount_price or self.price

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        upload_to="products/gallery/",
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'heic', 'heif']
        )]
    )

    def __str__(self):
        return f"Image for {self.product.name}"


# --- Order & OrderItemSnapshot ---
class OrderItemSnapshot(models.Model):
    product_id = models.IntegerField()
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255)
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
    items = models.JSONField(default=dict)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    full_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    snapshots = models.ManyToManyField(OrderItemSnapshot, blank=True)

    def __str__(self):
        return f"Buyurtma #{self.id} - {self.user.username}"


class ProductReview(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    stars_given = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        reviews = ProductReview.objects.filter(product=self.product)
        self.product.review_count = reviews.count()
        self.product.average_rating = reviews.aggregate(models.Avg('stars_given'))['stars_given__avg'] or 0
        self.product.save()

    def __str__(self):
        return f'{self.stars_given} stars for {self.product.name} by {self.user.username}'
