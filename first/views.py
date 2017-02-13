from django.contrib.auth.models import User, Group
from django.db.models import Count
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import detail_route
from . import serializers
from . import models

TOP_OTHERS_PRODUCT_COUNT = 3


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer

    #TODO Разделить статистичиеские данные на отдельные ресурсы
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
                [x['products'] for x in others_products_qs
                 if x['products'] != self.get_object().id][:TOP_OTHERS_PRODUCT_COUNT]

        else:
            refuse_probability_data['refuse_probability'] = None
            top_others['top_other_products'] = None
            # refused_parcels = []

        # parcel_serializer = serializers.ParcelSerializer(refused_parcels, many=True, context={'request': request})
        # refused_parcels_data = parcel_serializer.data

        data = [refuse_probability_data, top_others]
        response = Response(data)

        return response


class VendorViewSet(viewsets.ModelViewSet):
    queryset = models.Vendor.objects.all()
    serializer_class = serializers.VendorSerializer


class BarcodeViewSet(viewsets.ModelViewSet):
    queryset = models.Barcode.objects.all()
    serializer_class = serializers.BarcodeSerializer


class BarcodeTypeViewSet(viewsets.ModelViewSet):
    queryset = models.BarcodeType.objects.all()
    serializer_class = serializers.BarcodeTypeSerializer


class RecipientViewSet(viewsets.ModelViewSet):
    queryset = models.Recipient.objects.all()
    serializer_class = serializers.RecipientSerializer

    @detail_route(methods=['get'])
    def statistics(self, request, pk=None):
        """Расчет статистики по получателю

        Вероятность отказа от посылки. (учитывающая историю
        врученных получателю посылок)
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

        # parcel_serializer = serializers.ParcelSerializer(recipient_parcels,
        #                                                  many=True,
        #                                                  context={'request': request})
        # recipient_parcels_data = parcel_serializer.data

        data = [refused_parcels_data]
        response = Response(data)

        return response


class ParcelViewSet(viewsets.ModelViewSet):
    queryset = models.Parcel.objects.all()
    serializer_class = serializers.ParcelSerializer
