from django.core.exceptions import ObjectDoesNotExist
from django_filters import FilterSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from user.permissions import *
from .models import *
from .serializers import *
from user.serializers import UserProfileSerializer
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle
from collections import Counter
from user.emails import send_confirmation_email
# Create your views here.
class CustomPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'size'
    max_page_size = 10

class CustomThrottle(AnonRateThrottle):
    scope = 'custom'


class BestSellingView(APIView):
    serializer_class = ProductSerializer
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    def get(self, request):
        products = Product.objects.filter(sales_count__gte=50)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BrandView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('name',)
    search_fields = ('^name',)
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'brand'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CarouselView(APIView):
    serializer_class = CarouselSerializer
    throttle_classes = [CustomThrottle]
    def get(self, request):
        carousels = Carousel.objects.all()
        serializer = CarouselSerializer(carousels, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        permission_classes = [IsAuthenticated, EditUser]  # Define permission classes here for PUT method only
        self.permission_classes = permission_classes
        self.check_permissions(request)

        carousel = self.get_object(pk)
        serializer = CarouselSerializer(carousel, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return Carousel.objects.get(pk=pk)
        except Carousel.DoesNotExist:
            return Response({"detail": "Carousel not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        permission_classes = [IsAuthenticated, DeleteUser]
        self.permission_classes = permission_classes
        self.check_permissions(request)
        carousel = self.get_object(pk)
        carousel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        permission_classes = [IsAuthenticated, EditUser]
        self.permission_classes = permission_classes
        self.check_permissions(request)
        serializer = CarouselSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response("message:No Permission ", status=status.HTTP_404_NOT_FOUND)
        return Response("message:No Permission ", status=status.HTTP_400_BAD_REQUEST)


class ClientView(APIView):
    serializer_class = ClientSerializer
    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        permission_classes = [IsAuthenticated, EditUser]
        self.permission_classes = permission_classes
        self.check_permissions(request)
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response("message:No Permission ", status=status.HTTP_404_NOT_FOUND)
        return Response("message:No Permission ", status=status.HTTP_400_BAD_REQUEST)


class BuyNowAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        print("DATA 2", data)
        billing_address_data = data.get('billing_address', {})
        billing_address_data['user'] = user.id
        billing_address_data['use_same_address_for_shipping'] = data.get('use_same_address_for_shipping', False)
        billing_address_data['use_the_address_for_next_time'] = data.get('use_the_address_for_next_time', False)
        billing_serializer = BillingAddressSerializer(data=billing_address_data)
        print("DATA 2", billing_serializer)
        if billing_serializer.is_valid():
            billing_instance = billing_serializer.save()
        else:
            return Response(billing_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        shipping_instance = None
        if data.get('use_same_address_for_shipping', False):
            shipping_address_data = {
                'user': user.id,
                'shipping_name': billing_instance.billing_name,
                'email': billing_instance.email,
                'shipping_address': billing_instance.billing_address,
                'contact': billing_instance.contact,
                'use_same_address_for_shipping': False,
                'use_the_address_for_next_time': False,
            }
            print("DATA 3", shipping_address_data)
        else:
            shipping_address_data = data.get('shipping_address', {})
            shipping_address_data['user'] = user.id

        shipping_serializer = ShippingAddressSerializer(data=shipping_address_data)
        if shipping_serializer.is_valid():
            shipping_instance = shipping_serializer.save()
        else:
            billing_instance.delete()
            return Response(shipping_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if data.get('use_the_address_for_next_time', True):
            user_profile, created = Profile.objects.get_or_create(user=user)
            user_profile.preferred_billing_address = billing_instance
            user_profile.preferred_shipping_address = shipping_instance
            user_profile.save()

            print("DATA USER PROFILE:", user_profile.preferred_billing_address, user_profile.preferred_shipping_address)
            print("DATA PROFILE:", user_profile)
            response_data = {
                "message": "Addresses saved successfully.",
                "billing_address": BillingAddressSerializer(billing_instance).data,
                "shipping_address": ShippingAddressSerializer(shipping_instance).data if shipping_instance else None
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response("message:No Permission ", status=status.HTTP_404_NOT_FOUND)



class OrderSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_profile = Profile.objects.filter(user=user).first()
        if not user_profile:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        preferred_billing_address = user_profile.preferred_billing_address
        preferred_shipping_address = user_profile.preferred_shipping_address

        products_data = request.query_params.getlist('products')
        if not products_data:
            return Response({"detail": "No products."}, status=status.HTTP_400_BAD_REQUEST)

        order_items = []
        grand_total = 0

        for product_data in products_data:
            product_id, quantity = product_data.split(',')
            quantity = int(quantity)

            product = Product.objects.get(id=product_id)
            total = product.price * quantity
            grand_total += total

            product_image1 = product.image1.url if product.image1 and hasattr(product.image1, 'url') else None

            order_items.append({
                "product_id": product.id,
                "product_name": product.title,
                "product_category": product.category,
                "product_image": product.image,
                "product_image2": product_image1,
                "quantity": quantity,
                "total": total,
            })

        response = Response(status=status.HTTP_200_OK)
        for item in order_items:
            cookie_name = f'product_{item["product_id"]}'
            cookie_value = item["quantity"]
            response.set_cookie(cookie_name, cookie_value, httponly=True, secure=False, samesite='Lax')

        response.data = {
            "preferred_billing_address": BillingAddressSerializer(preferred_billing_address).data if preferred_billing_address else None,
            "preferred_shipping_address": ShippingAddressSerializer(preferred_shipping_address).data if preferred_shipping_address else None,
            "order_items": order_items,
            "grand_total": grand_total,
        }
        return response

class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_profile = Profile.objects.filter(user=user).first()
        if not user_profile:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        order_items = []
        print("Cookies present in the request:")
        for key, value in request.COOKIES.items():
            print(f"{key}: {value}")
            if key.startswith('product_'):
                product_id = key.split('_')[1]
                quantity = int(value)
                print(f"get cookie {key} = {quantity}")
                order_items.append({"product_id": product_id, "quantity": quantity})

        if not order_items:
            print("No order items found in cookies")
            return Response({"detail": "No order items."}, status=status.HTTP_400_BAD_REQUEST)

        orders = []
        for item in order_items:
            product_id = item['product_id']
            quantity = item['quantity']

            product = Product.objects.get(id=product_id)
            order = Order.objects.create(
                user=user,
                product=product,
                quantity=quantity,
                billing_address=user_profile.preferred_billing_address,
                shipping_address=user_profile.preferred_shipping_address,
            )

            product_order_count, created = ProductOrderCount.objects.get_or_create(product=product)
            product_order_count.order_count += quantity
            product_order_count.save()
            orders.append(order)

        response_data = {
            "message": "Thank you for your order!",
            "order_details": [OrderSerializer(order).data for order in orders]
        }
        try:
            most_recent_order = orders[-1]
            data = {
                'order_id': most_recent_order.id,
                'to_email': user.email,
            }
            send_confirmation_email(data)
        except Exception as e:
            print(e)

        response = Response(response_data, status=status.HTTP_201_CREATED)

        for item in order_items:
            cookie_name = f'product_{item["product_id"]}'
            print(f"Deleting cookie {cookie_name}")
            response.delete_cookie(cookie_name)
        return response



