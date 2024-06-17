from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class BillingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingAddress
        fields = '__all__'

class ShippingAddressSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = ShippingAddress
        fields = '__all__'