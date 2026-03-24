from django.db import models
from django.urls import reverse
from django.db.models import Avg, Count

from applications.category.models import Category
from applications.users.models import Account


class Product(models.Model):
    product_name  = models.CharField(max_length=200, unique=True)
    slug          = models.SlugField(max_length=200, unique=True)
    description   = models.TextField(max_length=500, blank=True)
    price         = models.IntegerField()
    images        = models.ImageField(upload_to='photos/products')
    stock         = models.IntegerField()
    is_available  = models.BooleanField(default=True)
    category      = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date  = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('app_store:product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    def averageReview(self):
        reviews = ReviewRating.objects.filter(
            product=self, status=True
        ).aggregate(average=Avg('rating'))
        avg = reviews['average']
        return float(avg) if avg is not None else 0

    def countReview(self):
        reviews = ReviewRating.objects.filter(
            product=self, status=True
        ).aggregate(count=Count('id'))
        count = reviews['count']
        return int(count) if count is not None else 0


# ---------------------------------------------------------------------------
# Variation
# ---------------------------------------------------------------------------

VARIATION_CATEGORY_CHOICES = (
    ('color', 'color'),
    ('size',  'size'),
)


class VariationManager(models.Manager):
    def colors(self):
        return self.filter(variation_category='color', is_active=True)

    def sizes(self):
        return self.filter(variation_category='size', is_active=True)


class Variation(models.Model):
    product            = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=VARIATION_CATEGORY_CHOICES)
    variation_value    = models.CharField(max_length=100)
    is_active          = models.BooleanField(default=True)
    created_date       = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value


# ---------------------------------------------------------------------------
# ReviewRating
# ---------------------------------------------------------------------------

class ReviewRating(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE)
    user       = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject    = models.CharField(max_length=100, blank=True)
    review     = models.TextField(max_length=500, blank=True)
    rating     = models.FloatField()
    ip         = models.CharField(max_length=20, blank=True)
    status     = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


# ---------------------------------------------------------------------------
# ProductGallery
# ---------------------------------------------------------------------------

class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image   = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name        = 'productgallery'
        verbose_name_plural = 'product gallery'
