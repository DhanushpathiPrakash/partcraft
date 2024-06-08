from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from user.permissions import *
from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.
class CustomPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'size'
    max_page_size = 10

class BestSellingView(APIView):
    serializer_class = ProductSerializer
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