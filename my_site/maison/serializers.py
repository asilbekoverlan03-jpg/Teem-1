from datetime import date
from rest_framework import serializers
from .models import (User, Category, Dish, Booking, Review,
                     RestaurantInfo, RestaurantPhoto, CartItem, Order, OrderItem)


# ---------- Пользователи ----------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone']


# ---------- Меню ----------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class DishSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Dish
        fields = ['id', 'name', 'description', 'price', 'image',
                  'category', 'category_name', 'is_popular']


# ---------- Бронирование ----------
class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'name', 'phone', 'date', 'time', 'guests', 'comment', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

    def validate_date(self, value):
        if value < date.today():
            raise serializers.ValidationError('Нельзя бронировать на прошедшую дату')
        return value

    def validate_guests(self, value):
        if value < 1 or value > 20:
            raise serializers.ValidationError('Гостей должно быть от 1 до 20')
        return value


# ---------- Отзывы ----------
class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'text', 'created_at']
        read_only_fields = ['created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Оценка от 1 до 5')
        return value


# ---------- О ресторане ----------
class RestaurantPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantPhoto
        fields = ['id', 'image']


class RestaurantInfoSerializer(serializers.ModelSerializer):
    photos = RestaurantPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = RestaurantInfo
        fields = ['id', 'name', 'address', 'phone', 'email', 'work_hours', 'description', 'photos']


# ---------- Корзина ----------
class CartItemSerializer(serializers.ModelSerializer):
    dish_name = serializers.CharField(source='dish.name', read_only=True)
    dish_price = serializers.DecimalField(source='dish.price', max_digits=10, decimal_places=2, read_only=True)
    dish_image = serializers.ImageField(source='dish.image', read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'dish', 'dish_name', 'dish_price', 'dish_image', 'quantity', 'total']

    def get_total(self, obj):
        return obj.dish.price * obj.quantity


# ---------- Заказы ----------
class OrderItemSerializer(serializers.ModelSerializer):
    dish_name = serializers.CharField(source='dish.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'dish_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'total', 'status', 'comment', 'created_at', 'items']
        read_only_fields = ['total', 'status', 'created_at']