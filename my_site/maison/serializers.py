from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (User, Category, Dish, Booking, Order, OrderItem,
                     Review, RestaurantInfo, RestaurantPhoto)


# ---------- Сотрудники ----------
class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'phone', 'role', 'role_display']


class LoginSerializer(TokenObtainPairSerializer):
    """Вход: кроме токенов отдаём данные сотрудника и роль"""
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


# ---------- Меню ----------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class DishSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Dish
        fields = ['id', 'name', 'description', 'composition', 'price', 'image',
                  'badge', 'category', 'category_name', 'is_popular']


# ---------- Бронь с сайта ----------
class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'guest_name', 'phone', 'date', 'time', 'guests', 'comment', 'status']
        read_only_fields = ['id', 'status']

    def validate_guests(self, value):
        if value < 1 or value > 20:
            raise serializers.ValidationError('Гостей должно быть от 1 до 20')
        return value

    def validate(self, data):
        now = timezone.localtime()
        if data['date'] < now.date():
            raise serializers.ValidationError({'date': 'Нельзя бронировать на прошедшую дату'})
        if data['date'] == now.date() and data['time'] <= now.time():
            raise serializers.ValidationError({'time': 'Это время уже прошло'})
        return data


# ---------- Заказ с сайта ----------
class OrderItemInputSerializer(serializers.Serializer):
    dish = serializers.PrimaryKeyRelatedField(queryset=Dish.objects.filter(is_available=True))
    quantity = serializers.IntegerField(min_value=1, max_value=50)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=255)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'dish', 'dish_name', 'quantity', 'price', 'comment']


class OrderCreateSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=[('takeaway', 'С собой'), ('delivery', 'Доставка')])
    guest_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    items = OrderItemInputSerializer(many=True, write_only=True)
    order_items = OrderItemSerializer(source='items', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'type', 'guest_name', 'phone', 'address', 'comment',
                  'items', 'order_items', 'total', 'status']
        read_only_fields = ['id', 'total', 'status']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('Корзина пуста')
        return value

    def validate(self, data):
        if data['type'] == 'delivery' and not data.get('address'):
            raise serializers.ValidationError({'address': 'Укажите адрес доставки'})
        return data
    def create(self, validated_data):
        items = validated_data.pop('items')
        with transaction.atomic():
            order = Order.objects.create(source='site', **validated_data)
            for item in items:
                dish = item['dish']
                OrderItem.objects.create(
                    order=order, dish=dish, dish_name=dish.name,
                    quantity=item['quantity'],
                    price=dish.price,          # цену берём из базы, а не с фронта
                    comment=item.get('comment', ''),
                )
            order.recalc_total()
        return order


# ---------- Отзывы и инфо ----------
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'rating', 'text', 'created_at']
        read_only_fields = ['created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Оценка от 1 до 5')
        return value


class RestaurantPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantPhoto
        fields = ['id', 'image']


class RestaurantInfoSerializer(serializers.ModelSerializer):
    photos = RestaurantPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = RestaurantInfo
        fields = ['id', 'name', 'address', 'phone', 'email', 'work_hours', 'description', 'photos']
