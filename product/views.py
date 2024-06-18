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
import logging

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
        try:
            user = request.user
            data = request.data
            billing_address_data = data.get('billing_address', {})
            billing_address_data['user'] = user.id
            billing_serializer = BillingAddressSerializer(data=billing_address_data)
            print(billing_serializer)
            if billing_serializer.is_valid():
                billing_instance = billing_serializer.save()
            else:
                return Response(billing_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            shipping_instance = None
            print(shipping_instance)
            if data.get('use_same_address_for_shipping', False):
                shipping_address_data = {
                    'user': user.id,
                    'shipping_name': billing_instance.billing_name,
                    'email': billing_instance.email,
                    'shipping_address': billing_instance.billing_address,
                    'contact': billing_instance.contact,
                    'use_same_address_for_shipping': billing_instance.use_same_address_for_shipping,
                    'use_the_address_for_next_time': billing_instance.use_the_address_for_next_time,
                }
                shipping_serializer = ShippingAddressSerializer(data=shipping_address_data)
                if shipping_serializer.is_valid():
                    shipping_instance = shipping_serializer.save()
                else:
                    billing_instance.delete()  # Clean up the saved billing address if shipping address validation fails
                    return Response(shipping_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                shipping_address_data = data.get('shipping_address', {})
                shipping_address_data['user'] = user.id
                shipping_serializer = ShippingAddressSerializer(data=shipping_address_data)
                if shipping_serializer.is_valid():
                    shipping_instance = shipping_serializer.save()
                else:
                    billing_instance.delete()
                    return Response(shipping_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if data.get('use_the_address_for_next_time', False):
                user_profile, created = Profile.objects.get_or_create(user=user)
                user_profile.preferred_billing_address = billing_instance
                user_profile.preferred_shipping_address = shipping_instance
                user_profile.save()
                print(user_profile)

            # Prepare response data
            response_data = {
                "message": "Addresses saved successfully.",
                "billing_address": BillingAddressSerializer(billing_instance).data,
                "shipping_address": ShippingAddressSerializer(shipping_instance).data if shipping_instance else None
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            user_profile = Profile.objects.filter(user=user).first()

            if not user_profile:
                return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

            preferred_billing_address = user_profile.preferred_billing_address
            preferred_shipping_address = user_profile.preferred_shipping_address

            response_data = {
                "preferred_billing_address": BillingAddressSerializer(
                    preferred_billing_address).data if preferred_billing_address else None,
                "preferred_shipping_address": ShippingAddressSerializer(
                    preferred_shipping_address).data if preferred_shipping_address else None,
            }
            print(response_data)
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)