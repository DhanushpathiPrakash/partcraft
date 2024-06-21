from decimal import Decimal
from django.db import models
import time
from user.models import User
from datetime import datetime
import random

def order_gen_id():
    timestamp = datetime.now().strftime('%m%d%Y')
    num = random.randint(10000, 99999)
    return f'{timestamp}-{num}'

# Create your models here.
class Product(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    category = models.CharField(max_length=100)
    image = models.URLField(max_length=500)
    logo = models.URLField(max_length=500)
    title = models.CharField(max_length=200)
    part_no = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=100, blank=True)
    image1 = models.ImageField(upload_to="products/", blank=True, null=True)
    full_title = models.CharField(max_length=500, blank=True)
    def __str__(self):
        return f"{self.id}{self.title}"


class Brand(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    image = models.URLField(max_length=500)
    def __str__(self):
        return self.name

class Carousel(models.Model):
    image = models.URLField(max_length=500)
    title = models.CharField(max_length=200)
    def __str__(self):
        return self.title

class Client(models.Model):
    image = models.URLField(max_length=500)
    data = models.TextField()
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

##-------shipping address -------------------------------------------------------
class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    billing_name = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=16, blank=True, null=True)
    email = models.EmailField(max_length=255)
    billing_address = models.CharField(max_length=1000)
    contact = models.CharField(max_length=13)
    use_same_address_for_shipping = models.BooleanField(default=False)
    use_the_address_for_next_time = models.BooleanField(default=False)

    def __str__(self):
        return self.billing_address

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    shipping_address = models.CharField(max_length=1000)
    contact = models.CharField(max_length=13)

    def __str__(self):
        return self.shipping_address


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    preferred_billing_address = models.ForeignKey(BillingAddress, null=True, blank=True, on_delete=models.SET_NULL, related_name='preferred_billing_user')
    preferred_shipping_address = models.ForeignKey(ShippingAddress, null=True, blank=True, on_delete=models.SET_NULL, related_name='preferred_shipping_user')

    def __str__(self):
        return f"Profile for {self.user.email}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    billing_address = models.ForeignKey(BillingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=15, unique=True)
    order_date = models.DateField(auto_now_add=True)
    quantity = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = order_gen_id()
        super(Order, self).save(*args, **kwargs)

class ProductOrderCount(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product} - {self.order_count}"