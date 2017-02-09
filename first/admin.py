from django.contrib import admin

# Register your models here.

from . import models


class BarcodeAdmin(admin.ModelAdmin):
    model = models.Barcode
    list_display = ('type', 'value')


class ProductAdmin(admin.ModelAdmin):
    model = models.Product
    list_display = ('article', 'vendor', 'name',
                    'barcode', 'image', 'price', 'weight')

admin.site.register(models.BarcodeType)
admin.site.register(models.Barcode, BarcodeAdmin)
admin.site.register(models.Vendor)
# TODO сделать поле Barcode типа Inline
admin.site.register(models.Product, ProductAdmin)
