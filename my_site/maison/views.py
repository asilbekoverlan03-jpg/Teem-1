from django.db import transaction
from rest_framework import generics, viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, Category, Dish, Booking, Review, RestaurantInfo, CartItem, Order, OrderItem
from .serializers import (RegisterSerializer, UserSerializer, CategorySerializer, DishSerializer,
                          BookingSerializer, ReviewSerializer, RestaurantInfoSerializer,
                          CartItemSerializer, OrderSerializer)
from .filters import DishFilter


# ---------- Пользователи ----------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ---------- Меню ----------
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class DishViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dish.objects.filter(is_available=True)
    serializer_class = DishSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DishFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name']


# ---------- Бронирование ----------
class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------- Отзывы ----------
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # читать могут все, писать — только вошедшие
    http_method_names = ['get', 'post']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------- О ресторане ----------
class RestaurantInfoView(generics.RetrieveAPIView):
    serializer_class = RestaurantInfoSerializer

    def get_object(self):
        obj = RestaurantInfo.objects.first()
        if obj is None:
            raise NotFound('Информация о ресторане не заполнена')
        return obj


# ---------- Корзина ----------
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related('dish')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dish = serializer.validated_data['dish']
        quantity = serializer.validated_data.get('quantity', 1)

        # если блюдо уже в корзине — просто увеличиваем количество
        item, created = CartItem.objects.get_or_create(
            user=request.user, dish=dish, defaults={'quantity': quantity})
        if not created:
            item.quantity += quantity
            item.save()
        return Response(self.get_serializer(item).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------- Заказы ----------
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items').order_by('-created_at')

    def create(self, request, *args, **kwargs):
        cart = CartItem.objects.filter(user=request.user).select_related('dish')
        if not cart.exists():
            return Response({'error': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():  # или всё сохранится, или ничего
            order = Order.objects.create(user=request.user, comment=request.data.get('comment', ''))
            total = 0
            for item in cart:
                OrderItem.objects.create(order=order, dish=item.dish,
                                         quantity=item.quantity, price=item.dish.price)
                total += item.dish.price * item.quantity
            order.total = total
            order.save()
            cart.delete()  # корзина очищается после заказа

        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)