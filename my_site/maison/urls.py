from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (RegisterView, ProfileView, CategoryViewSet, DishViewSet, BookingViewSet,
                    ReviewViewSet, RestaurantInfoView, CartViewSet, OrderViewSet)

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('dishes', DishViewSet)
router.register('bookings', BookingViewSet, basename='bookings')
router.register('reviews', ReviewViewSet)
router.register('cart', CartViewSet, basename='cart')
router.register('orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/profile/', ProfileView.as_view()),
    path('restaurant/', RestaurantInfoView.as_view()),
    path('', include(router.urls)),
]