from rest_framework import generics, viewsets, filters, mixins
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Dish, BookingHistory, Review, RestaurantInfo
from .serializers import (LoginSerializer, UserSerializer, CategorySerializer, DishSerializer,
                          BookingCreateSerializer, OrderCreateSerializer,
                          ReviewSerializer, RestaurantInfoSerializer)
from .filters import DishFilter


# ---------- Вход сотрудников (CRM) ----------
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ---------- Сайт: меню ----------
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class DishViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dish.objects.filter(is_available=True).select_related('category')
    serializer_class = DishSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DishFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name']


# ---------- Сайт: бронь и заказ (без входа) ----------
class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingCreateSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        booking = serializer.save(source='site')
        BookingHistory.objects.create(booking=booking, text='Бронь создана с сайта')


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [AllowAny]


# ---------- Сайт: отзывы и инфо ----------
class ReviewViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Review.objects.filter(is_published=True).order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]


class RestaurantInfoView(generics.RetrieveAPIView):
    serializer_class = RestaurantInfoSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        obj = RestaurantInfo.objects.first()
        if obj is None:
            raise NotFound('Информация о ресторане не заполнена')
        return obj