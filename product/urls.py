from django.urls import path
from .views import *

urlpatterns = [
    path('v1/BestSelling/', BestSellingView.as_view(), name='bestselling'),
    path('v1/Brands/', BrandView.as_view(), name='brands'),
    path('v1/carousel/', CarouselView.as_view(), name='carousel'),
    path('v1/carousel/<int:pk>/', CarouselView.as_view()),
    path('v1/client-feedback/', ClientView.as_view(), name='client-feedback'),
    path('v1/buy_now/', BuyNowAPIView.as_view(), name='address'),
    path('v1/order_summary/', OrderSummaryAPIView.as_view(), name='order'),
    path('v1/place_order/', OrderAPIView.as_view(), name='place_order'),
]
