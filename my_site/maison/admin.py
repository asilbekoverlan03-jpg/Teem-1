from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (User, Category, Dish, Table, Booking, BookingHistory, Order, OrderItem,
                     Review, RestaurantInfo, RestaurantPhoto)


@admin.register(User)
class StaffAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    ordering = ['email']
    fieldsets = UserAdmin.fieldsets + (('MAISON', {'fields': ('role', 'phone')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('MAISON', {'fields': ('email', 'role', 'phone')}),)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'position']


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'badge', 'station', 'is_popular', 'is_available']
    list_filter = ['category', 'station', 'is_popular', 'is_available']
    search_fields = ['name']


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'seats', 'zone', 'is_active']


class BookingHistoryInline(admin.TabularInline):
    model = BookingHistory
    extra = 0
    readonly_fields = ['text', 'user', 'created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'guest_name', 'phone', 'date', 'time', 'guests', 'table', 'status', 'source']
    list_filter = ['status', 'source', 'date']
    search_fields = ['guest_name', 'phone']
    inlines = [BookingHistoryInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'table', 'waiter', 'status', 'total', 'is_paid', 'created_at']
    list_filter = ['status', 'type', 'is_paid', 'source']
    readonly_fields = ['total']
    inlines = [OrderItemInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'is_published', 'created_at']
    list_editable = ['is_published']


class PhotoInline(admin.TabularInline):
    model = RestaurantPhoto
    extra = 1


@admin.register(RestaurantInfo)
class RestaurantInfoAdmin(admin.ModelAdmin):
    inlines = [PhotoInline]