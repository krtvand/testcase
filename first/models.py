from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse

from django_rest.settings import ALLOWED_HOSTS


class Vendor(models.Model):
    """
    Производитель
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BarcodeType(models.Model):
    """
    Тип штрих-кода, например EAN-13
    """

    type = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.type


class Barcode(models.Model):
    """
    Штрих-код
    """
    type = models.ForeignKey(BarcodeType, on_delete=models.CASCADE)
    value = models.CharField(max_length=256)

    def __str__(self):
        return '[{}] {}'.format(self.type, self.value)


class Product(models.Model):
    """
    Товар
    """
    article = models.CharField(max_length=20, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    barcode = models.OneToOneField(Barcode,
                                   on_delete=models.CASCADE,
                                   blank=True, null=True)
    image = models.ImageField(upload_to='product_images/',
                              blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    weight = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return '[{}] {}'.format(self.article, self.name)

    def get_full_absolute_url(self):
        """
        Абсолютный адрес объекта. Используется в функции
        получения статистики по товару
        """
        # TODO избавиться от этой функции !!!
        domain = ALLOWED_HOSTS[0]
        url = reverse('product-detail', args=[self.id])

        return 'http://{}:8000{}'.format(domain, url)


class Fullname(models.Model):
    """
    ФИО Получателя
    """
    first_name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    patronymic = models.CharField(max_length=30,
                                  blank=True, null=True)

    def __str__(self):
        return '{} {} {}'.format(self.surname,
                                 self.first_name, self.patronymic)


class Address(models.Model):
    """
    Адрес получателя
    """
    postal_code = models.CharField(max_length=6, blank=True)
    country = models.CharField(max_length=30)
    state = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=100)

    def __str__(self):
        return '{}, {}, {}, {}'.format(self.postal_code,
                                       self.country, self.city,
                                       self.address)


class Recipient(models.Model):
    """
    Получатель
    """
    fullname = models.ForeignKey(Fullname, on_delete=models.CASCADE)
    address = models.ForeignKey(Address)
    photo = models.ImageField(upload_to='recipient_photos/',
                              blank=True, null=True)
    # TODO для даты возможно стоит применить editable=False
    registration_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{}, {}'.format(self.fullname, self.address)


class ProductInParcel(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField()
    comment = models.CharField(max_length=500)


class Parcel(models.Model):
    """
    Посылка
    """
    # TODO включить параметр количество товаров для данной позиции,
    # скорее всего придется описать промежуточную модель.
    # products = models.ManyToManyField(ProductInParcel)
    # TODO Включить расчет стоимости доставки посылки при изменении
    # модели через django admin
    products = models.ManyToManyField(Product)
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    isdelivered = models.BooleanField()
    isrefused = models.BooleanField()
    departure_date = models.DateField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    cost_of_delivery = models.DecimalField(max_digits=9, decimal_places=2,
                                           blank=True, null=True)

    def __str__(self):
        return '{}, {}, {}'.format(self.recipient.fullname,
                                       self.departure_date,
                                       self.cost_of_delivery)

    def products_str(self):
        """
        Строковое отображение списка товаров в посылке (для django admin)
        """
        products = [p.name for p in self.products.all()][:50]
        return products
