from django.contrib import admin
from product.models import *

# Register your models here.
admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Carousel)
admin.site.register(Client)
admin.site.register(BillingAddress)
admin.site.register(ShippingAddress)
admin.site.register(Profile)