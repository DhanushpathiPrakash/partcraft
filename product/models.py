from decimal import Decimal
from django.db import models

# Create your models here.
class Product(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_images/')
    logo = models.ImageField(upload_to='brand_logos/')
    title = models.CharField(max_length=200)
    part_no = models.CharField(max_length=50)
    discount = models.CharField(max_length=20)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=100, blank=True)
    full_title = models.CharField(max_length=500, blank=True)
    sales_count = models.IntegerField(default=0)

class Brand(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='brand_images/')

class Carousel(models.Model):
    image = models.ImageField(upload_to='carousel_images/')
    title = models.CharField(max_length=200)

class Client(models.Model):
    image = models.ImageField(upload_to='client_images/')
    data = models.TextField()
    name = models.CharField(max_length=255)