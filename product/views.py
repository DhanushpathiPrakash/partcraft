from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from user.permissions import *
from .models import *
from .serializers import *

# Create your views here.
class BestSellingView(APIView):
    serializer_class = ProductSerializer
    def get(self, request):
        products = Product.objects.filter(sales_count__gte=50)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BrandView(APIView):
    serializer_class = BrandSerializer
    def get(self, request):
        brands = Brand.objects.all()
        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
