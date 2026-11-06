import pathlib
import stripe
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.urls import reverse




from cfehome.env import config

STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default=None)
stripe.api_key = STRIPE_SECRET_KEY

PROTECTED_MEDIA_ROOT = settings.PROTECTED_MEDIA_ROOT

protected_storage = FileSystemStorage(location=str(PROTECTED_MEDIA_ROOT))
# Create your models here.
class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    stripe_product_id = models.CharField(max_length=220, blank=True, null=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    name = models.CharField(max_length=120)
    handle = models.SlugField(unique=True) #slug
    price = models.DecimalField(max_digits = 10, decimal_places=2, default=9.99)
    og_price = models.DecimalField(max_digits = 10, decimal_places=2, default=9.99)
    stripe_price_id = models.CharField(max_length=220, blank=True, null=True)
    stripe_price = models.IntegerField() #100*price
    price_changed_timestamp = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"handle": self.handle})

    def save(self, *args, **kwargs):
        price_changed = self.price != self.og_price
        self.stripe_price = int(self.price * 100)

        if self.name and not self.stripe_product_id:
            stripe_product_r = stripe.Product.create(name=self.name)
            self.stripe_product_id = stripe_product_r.id

        if price_changed:
            self.og_price = self.price
            self.price_changed_timestamp = timezone.now()

        if not self.stripe_price_id or price_changed:
            stripe_price_obj = stripe.Price.create(
                product=self.stripe_product_id,
                unit_amount=self.stripe_price,
                currency="usd"
            )
            self.stripe_price_id = stripe_price_obj.id
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"handle": self.handle})

    def get_manage_url(self):
        return reverse("products:manage", kwargs={"handle": self.handle})

    @property
    def display_price(self):
        return self.price

def handle_product_attachment_upload(instance, filename):
    # Customize the upload path based on your requirements
    return f'products/{instance.product.handle}/attachments/{filename}'

class ProductAttachment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file = models.FileField(upload_to=handle_product_attachment_upload,
                            storage=protected_storage)
    name = models.CharField(max_length=120, null=True, blank=True)
    # handle = models.SlugField(unique=True)
    is_free = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # ... other fields ...
    
    @property
    def display_name(self):
        return self.name

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = pathlib.Path(self.file.name).name
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        return self.name or pathlib.Path(self.file.name).name

    def get_download_url(self):
        return reverse("products:download", kwargs={"handle": self.product.handle, "pk": self.pk})