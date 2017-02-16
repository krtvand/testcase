from django.db.models import Count
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from . import serializers
from . import models
from .config import *


class ProductViewSet(viewsets.ModelViewSet):
    """
    Контроллер товара
    """
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer

    #TODO Разделить статистичиеские данные на отдельные ресурсы,
    # выделить статистику как отдельный ресурс,
    # а конкретные данные выводить в списке доступных подресурсов

    @detail_route(methods=['get'])
    def statistics(self, request, pk=None):
        """Расчет статистики по товару

        1) Вероятность отказа от товара - отношение количества посылок с отказом
        от всех посылок с этим товаром. Если товар ни раз не заказывался, то Null
        2) Другие 3 товара, которые чаще всего заказывают с этим товаром.
        """
        parcels_with_product = models.Parcel.objects.filter(
            products__in=[self.get_object()]
        )

        top_others = {}
        refuse_probability_data = {}
        if parcels_with_product:
            # Вероятность отказа
            refused_parcels = parcels_with_product.filter(isrefused=True)
            refuse_probability_data['refuse_probability'] = \
                len(refused_parcels) / len(parcels_with_product)

            # Другие 3 товара, которые чаще всего заказывают с этим товаром.
            others_products_qs = models.Parcel.objects.values('products')\
                .annotate(total=Count('products'))\
                .filter(products__in=[self.get_object()]) \
                .order_by('-total')
                # .exclude(products=7)\
            # Из QuerySet выбираем id товаров, исключая текущий товар
            top_others['top_other_products'] = \
                [models.Product.objects.get(pk=x['products']).get_full_absolute_url()
                 for x in others_products_qs
                 if x['products'] != self.get_object().id
                 ][:TOP_OTHERS_PRODUCT_COUNT]
            # print(reverse('product-detail', args=[ top_others[1]])))

        else:
            refuse_probability_data['refuse_probability'] = None
            top_others['top_other_products'] = None
            # refused_parcels = []

        data = [refuse_probability_data, top_others]
        response = Response(data)

        return response


class VendorViewSet(viewsets.ModelViewSet):
    """
    Контроллер производителя
    """
    queryset = models.Vendor.objects.all()
    serializer_class = serializers.VendorSerializer


class BarcodeViewSet(viewsets.ModelViewSet):
    """
    Контроллер штрих-кода
    """
    queryset = models.Barcode.objects.all()
    serializer_class = serializers.BarcodeSerializer


class BarcodeTypeViewSet(viewsets.ModelViewSet):
    """
    Контроллер типа штрих-кода
    """
    queryset = models.BarcodeType.objects.all()
    serializer_class = serializers.BarcodeTypeSerializer


class RecipientViewSet(viewsets.ModelViewSet):
    """
    Контроллер получателя
    """
    queryset = models.Recipient.objects.all()
    serializer_class = serializers.RecipientSerializer

    @detail_route(methods=['get'])
    def statistics(self, request, pk=None):
        """Расчет статистики по получателю

        Вероятность отказа от посылки. (учитывающая историю врученных
        получателю посылок). Рассчитывается как отношение числа
        отказанных посылок к общему количеству заказанных посылок
        """
        recipient_parcels = models.Parcel.objects.filter(
            recipient__in=[self.get_object()]
        )

        refused_parcels_data = {}
        if recipient_parcels:
            # Вероятность отказа
            refused_parcels = recipient_parcels.filter(isrefused=True)
            refused_parcels_data['refuse_probability'] = \
                len(refused_parcels) / len(recipient_parcels)
        else:
            refused_parcels_data['refuse_probability'] = None

        data = [refused_parcels_data]
        response = Response(data)

        return response


class ParcelViewSet(viewsets.ModelViewSet):
    """
    Контроллер посылки
    """
    queryset = models.Parcel.objects.all()
    serializer_class = serializers.ParcelSerializer
