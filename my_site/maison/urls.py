from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (LoginView, ProfileView, CategoryViewSet, DishViewSet, BookingCreateView,
                    OrderCreateView, ReviewViewSet, RestaurantInfoView)

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('dishes', DishViewSet)
router.register('reviews', ReviewViewSet)

urlpatterns = [
    # CRM: вход сотрудников
    path('auth/login/', LoginView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/profile/', ProfileView.as_view()),
    # Сайт
    path('bookings/', BookingCreateView.as_view()),
    path('orders/', OrderCreateView.as_view()),
    path('restaurant/', RestaurantInfoView.as_view()),
    path('', include(router.urls)),
]