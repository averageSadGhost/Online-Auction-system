from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuctionViewSet

# Create a router and register the viewset
router = DefaultRouter()
router.register(r'auctions', AuctionViewSet, basename='auction')

# Define urlpatterns
urlpatterns = [
    path('', include(router.urls)),  # Include router-generated URLs
]
