from django.contrib.auth.models import AbstractUser
from django.db import models


# ---------- Сотрудники ----------
class User(AbstractUser):
    ROLES = [
        ('owner', 'Владелец'),
        ('admin', 'Администратор'),
        ('waiter', 'Официант'),
        ('kitchen', 'Кухня'),
    ]
    email = models.EmailField('Рабочая почта', unique=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    role = models.CharField('Роль', max_length=20, choices=ROLES, default='waiter')

    USERNAME_FIELD = 'email'          # вход по почте, как в макете CRM
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f'{self.get_full_name() or self.email} ({self.get_role_display()})'


# ---------- Меню ----------
class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    position = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['position']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Dish(models.Model):
    STATIONS = [('hot', 'Горячий цех'), ('cold', 'Холодный цех')]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='dishes', verbose_name='Категория')
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    composition = models.TextField('Состав и аллергены', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    image = models.ImageField('Фото', upload_to='dishes/', blank=True)
    badge = models.CharField('Метка на карточке', max_length=50, blank=True,
                             help_text='Например: Шеф рекомендует, Новинка')
    station = models.CharField('Цех', max_length=10, choices=STATIONS, default='hot')
    is_popular = models.BooleanField('Выбранное для вас', default=False)
    is_available = models.BooleanField('В наличии', default=True)

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'

    def __str__(self):
        return self.name


# ---------- Зал ----------
class Table(models.Model):
    number = models.CharField('Номер', max_length=10, unique=True)   # T01, T02...
    seats = models.PositiveSmallIntegerField('Мест')
    zone = models.CharField('Зона', max_length=50, default='Основной зал')
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        ordering = ['number']
        verbose_name = 'Стол'
        verbose_name_plural = 'Столы'

    def __str__(self):
        return f'{self.number} · {self.seats} мест'


# ---------- Бронирования ----------
class Booking(models.Model):
    STATUS = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждена'),
        ('seated', 'В зале'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]
    SOURCES = [('site', 'Сайт'), ('phone', 'По телефону'), ('walk_in', 'Без брони')]

    guest_name = models.CharField('Имя гостя', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    date = models.DateField('Дата')
    time = models.TimeField('Время')
    guests = models.PositiveSmallIntegerField('Гостей')
    duration = models.PositiveSmallIntegerField('Продолжительность, ч', default=2)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='bookings', verbose_name='Стол')
    source = models.CharField('Источник', max_length=20, choices=SOURCES, default='site')
    status = models.CharField('Статус', max_length=20, choices=STATUS, default='pending')
    comment = models.TextField('Пожелания гостя', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='Ответственный')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']
        verbose_name = 'Бронь'
        verbose_name_plural = 'Бронирования'

    @property
    def number(self):
        return f'Б-{self.id:03d}'       # как в макете: Б-024

    def __str__(self):
        return f'{self.number} {self.guest_name} {self.date} {self.time}'


class BookingHistory(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='history')
    text = models.CharField('Событие', max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


# ---------- Заказы ----------
class Order(models.Model):
    TYPES = [('hall', 'В зале'), ('takeaway', 'С собой'), ('delivery', 'Доставка')]
    STATUS = [
        ('new', 'Новый'),
        ('cooking', 'Готовится'),
        ('ready', 'Готов к подаче'),
        ('served', 'Подан'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]
    SOURCES = [('site', 'Сайт'), ('crm', 'CRM')]

    type = models.CharField('Тип', max_length=20, choices=TYPES, default='hall')
    source = models.CharField('Источник', max_length=10, choices=SOURCES, default='crm')
    status = models.CharField('Статус', max_length=20, choices=STATUS, default='new')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='orders', verbose_name='Стол')
    waiter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='orders', verbose_name='Официант')
    guest_name = models.CharField('Имя гостя', max_length=100, blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    address = models.CharField('Адрес доставки', max_length=255, blank=True)
    comment = models.TextField('Комментарий', blank=True)
    cancel_reason = models.CharField('Причина отмены', max_length=255, blank=True)
    discount = models.DecimalField('Скидка', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('Итого', max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField('Оплачен', default=False)
    paid_at = models.DateTimeField('Время оплаты', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def recalc_total(self):
        subtotal = sum(i.price * i.quantity for i in self.items.all())
        self.total = max(subtotal - self.discount, 0)
        self.save(update_fields=['total'])

    def __str__(self):
        return f'Заказ №{self.id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.SET_NULL, null=True)
    dish_name = models.CharField('Блюдо', max_length=200)   # копия названия на момент заказа
    quantity = models.PositiveSmallIntegerField('Кол-во', default=1)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    comment = models.CharField('Комментарий для кухни', max_length=255, blank=True)


# ---------- Отзывы и инфо ----------
class Review(models.Model):
    name = models.CharField('Имя', max_length=100)
    rating = models.PositiveSmallIntegerField('Оценка', default=5)
    text = models.TextField('Текст')
    is_published = models.BooleanField('Опубликован', default=False)   # модерация
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class RestaurantInfo(models.Model):
    name = models.CharField(max_length=100, default='MAISON')
    address = models.CharField('Адрес', max_length=255)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField(blank=True)
    work_hours = models.CharField('Часы работы', max_length=100)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'О ресторане'
        verbose_name_plural = 'О ресторане'

    def __str__(self):
        return self.name


class RestaurantPhoto(models.Model):
    restaurant = models.ForeignKey(RestaurantInfo, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='restaurant/')