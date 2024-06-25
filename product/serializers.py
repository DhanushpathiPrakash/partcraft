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
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = BillingAddress
        fields = '__all__'

class ShippingAddressSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = ShippingAddress
        fields = '__all__'

class Buynowserilizers(serializers.Serializer):
    billing_address = Billaddressserializer()
    shipping_address = Shippingaddressserializer(required=False)
    use_same_address_for_shipping = serializers.BooleanField(default=False)
    use_the_address_for_next_time = serializers.BooleanField(default=False)

    def to_internal_value(self, data):
        return_user = self.context["request"].user
        if 'billing_address' in data:
            data['billing_address']['user'] = return_user.id
        if 'shipping_address' in data:
            data['shipping_address']['user'] = return_user.id

        return super().to_internal_value(data)

    def create(self, validated_data):
        billing_address_data = validated_data.pop('billing_address')
        use_same_address_for_shipping = validated_data.pop('use_same_address_for_shipping', False)
        use_the_address_for_next_time = validated_data.pop('use_the_address_for_next_time', False)
        user = self.context['request'].user

        # Create BillingAddress instance
        billing_address_data['user'] = user
        billing_instance = BillingAddress.objects.create(**billing_address_data)

        print(billing_instance)

        shipping_instance = None
        if use_same_address_for_shipping:
            shipping_address_data = {
                'user': user,
                'shipping_name': billing_instance.billing_name,
                'email': billing_instance.email,
                'shipping_address': billing_instance.billing_address,
                'contact': billing_instance.contact,
            }
            shipping_instance = ShippingAddress.objects.create(**shipping_address_data)
        else:
            shipping_address_data = validated_data.pop('shipping_address', None)
            if shipping_address_data:
                shipping_address_data['user'] = user
                shipping_instance = ShippingAddress.objects.create(**shipping_address_data)

        if use_the_address_for_next_time:
            user_profile, created = Profile.objects.get_or_create(user=user)
            user_profile.preferred_billing_address = billing_instance
            user_profile.preferred_shipping_address = shipping_instance
            user_profile.save()

        return {
            "billing_address": billing_instance,
            "shipping_address": shipping_instance,
        }

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'order_date']
