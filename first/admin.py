from django.contrib import admin

# Register your models here.

from . import models


class BarcodeAdmin(admin.ModelAdmin):
    model = models.Barcode
    list_display = ('type', 'value')


class ProductAdmin(admin.ModelAdmin):
    model = models.Product
    list_display = ('article', 'name', 'vendor', 'price', 'weight',
                    'barcode', 'image')

    # TODO сделать поле Barcode типа Inline
    # 'first.Barcode' has no ForeignKey to 'first.Product'.
    # inlines = [BarCodeInline]


class RecipientAdmin(admin.ModelAdmin):
    model = models.Recipient
    list_display = ('fullname', 'address', 'photo',
                    'registration_date')

admin.site.register(models.BarcodeType)
admin.site.register(models.Barcode, BarcodeAdmin)
admin.site.register(models.Vendor)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Recipient, RecipientAdmin)
admin.site.register(models.Parcel)
