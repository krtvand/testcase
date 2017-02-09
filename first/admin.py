from django.contrib import admin

# Register your models here.

from . import models


class BarcodeAdmin(admin.ModelAdmin):
    model = models.Barcode
    list_display = ('type', 'value')

# class RequestAdmin(admin.ModelAdmin):
#     inlines = [ContractInline]
#     list_display = ('it_manager_fullname', 'created_date', 'department_id')

admin.site.register(models.Currency)
admin.site.register(models.Price)
admin.site.register(models.Weight)
admin.site.register(models.BarcodeType)
admin.site.register(models.Barcode, BarcodeAdmin)
admin.site.register(models.Vendor)
admin.site.register(models.Product)
