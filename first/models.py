from django.db import models


class Vendor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BarcodeType(models.Model):
    """e.g EAN-13    """

    type = models.CharField(max_length=20)

    def __str__(self):
        return self.type


class Barcode(models.Model):
    type = models.ForeignKey(BarcodeType, on_delete=models.CASCADE)
    value = models.CharField(max_length=256)

    def __str__(self):
        return '[{}] {}'.format(self.type, self.value)


# class Currency(models.Model):
#     name = models.CharField(max_length=10, default='USD')
#
#     def __str__(self):
#         return self.name
#
#
# class Price(models.Model):
#     currency = models.ForeignKey(Currency)
#     value = models.DecimalField(max_digits=9, decimal_places=2)
#
#     def __str__(self):
#         return '[{}] {}'.format(self.value, self.currency)


# class WeightType(models.Model):
#     name = models.CharField(max_length=20)
#
#     def __str__(self):
#         return self.name
#
#
# class Weight(models.Model):
#     type = models.ForeignKey(WeightType)
#     value = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def __str__(self):
#         return '[{}] {}'.format(self.value, self.type)


class Product(models.Model):
    article = models.CharField(max_length=20)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    barcode = models.ForeignKey(Barcode,
                                on_delete=models.CASCADE,
                                blank=True, null=True)
    image = models.ImageField(upload_to='product_images/',
                              blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    weight = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return '[{}] {}'.format(self.article, self.name)


class Fullname(models.Model):
    first_name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    patronymic = models.CharField(max_length=30,
                                  blank=True, null=True)

    def __str__(self):
        return '{} {} {}'.format(self.surname,
                                 self.first_name, self.patronymic)


class Address(models.Model):
    # TODO продумать тип адреса, чтобы был интернациональный
    postal_code = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    state = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=100)

    def __str__(self):
        return '{}, {}, {}, {}'.format(self.postal_code,
                                       self.country, self.city,
                                       self.address)


class Recipient(models.Model):
    fullname = models.ForeignKey(Fullname, on_delete=models.CASCADE)
    address = models.ForeignKey(Address)
    photo = models.ImageField(upload_to='recipient_photos/',
                              blank=True, null=True)
    registration_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{}, {}'.format(self.fullname, self.address)


class Parcel(models.Model):
    products = models.ManyToManyField(Product)
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    isdelivered = models.BooleanField()
    isrefused = models.BooleanField()
    departure_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    cost_of_delivery = models.DecimalField(max_digits=9,
                                           decimal_places=2)

    def __str__(self):
        return '{}, {}, {}'.format(self.recipient,
                                   self.departure_date,
                                   self.cost_of_delivery)
