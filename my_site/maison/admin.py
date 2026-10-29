from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (User, Category, Dish, Booking, Review,
                     RestaurantInfo, RestaurantPhoto, CartItem, Order, OrderItem)

admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(CartItem)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_popular', 'is_available']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'date', 'time', 'guests', 'status']
    list_filter = ['status', 'date']


class PhotoInline(admin.TabularInline):
    model = RestaurantPhoto
    extra = 1


@admin.register(RestaurantInfo)
class RestaurantInfoAdmin(admin.ModelAdmin):
    inlines = [PhotoInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'status', 'created_at']
    inlines = [OrderItemInline]
