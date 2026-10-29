from rest_framework import serializers
from .models import User, Category, Dish


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)  # пароль сохранится зашифрованным


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone']


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