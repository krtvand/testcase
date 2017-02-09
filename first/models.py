from django.db import models


class Vendor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BarcodeType(models.Model):
    """e.g EAN-13
    """

    type = models.CharField(max_length=20)

    def __str__(self):
        return self.type


class Barcode(models.Model):
    type = models.ForeignKey(BarcodeType, on_delete=models.CASCADE)
    value = models.CharField(max_length=256)

    def __str__(self):
        return '[{}] {}'.format(self.type, self.value)


class Currency(models.Model):
    name = models.CharField(max_length=10, default='USD')


class Price(models.Model):
    currency = models.ForeignKey(Currency)
    value = models.DecimalField(max_digits=9, decimal_places=2)


class WeightType(models.Model):
    name = models.CharField(max_length=20)


class Weight(models.Model):
    type = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=10, decimal_places=2)


class Product(models.Model):
    article = models.CharField(max_length=20)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    barcode = models.ForeignKey(Barcode, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    price = models.ForeignKey(Price)
    weight = models.ForeignKey(Weight)


class Fullname(models.Model):
    first_name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    patronymic = models.CharField(max_length=30, blank=True, null=True)

class Address(models.Model):
    # TODO продумать тип адреса, чтобы был интернациональный
    postal_code = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    state = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=100)


class Recipient(models.Model):
    fullname = models.ForeignKey(Fullname, on_delete=models.CASCADE)
    address = models.ForeignKey(Address)
    photo = models.ImageField(upload_to='recipient_photos/')
    registration_date = models.DateField(auto_now=True)

