from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from . import serializers
from . import models


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


class VendorViewSet(viewsets.ModelViewSet):
    queryset = models.Vendor.objects.all()
    serializer_class = serializers.VendorSerializer


class BarcodeViewSet(viewsets.ModelViewSet):
    queryset = models.Barcode.objects.all()
    serializer_class = serializers.BarcodeSerializer
    print(repr(serializer_class))


class BarcodeTypeViewSet(viewsets.ModelViewSet):
    queryset = models.BarcodeType.objects.all()
    serializer_class = serializers.BarcodeTypeSerializer