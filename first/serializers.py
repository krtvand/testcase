from django.contrib.auth.models import User, Group
from rest_framework import serializers
from . import models


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class VendorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Vendor
        fields = ('url', 'id', 'name')


class BarcodeTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.BarcodeType
        fields = ('url', 'type')


class BarcodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Barcode
        fields = ('url', 'type', 'value')


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    # Вопрос - какой формат производителя в api
    # предпочтительнее? Hyperlink или id + name
    # т.е. есть ли смысл описывать вложенные сериализаторы?
    barcode = BarcodeSerializer()
    vendor = serializers.HyperlinkedRelatedField(queryset=models.Vendor.objects.all(),
                                                 view_name='vendor-detail')

    class Meta:
        model = models.Product
        fields = ('url', 'article', 'name', 'image',
                  'price', 'weight', 'vendor', 'barcode')

        depth = 2

    def create(self, validated_data):
        barcode_data = validated_data.pop('barcode')
        barcode = models.Barcode.objects.create(**barcode_data)
        product = models.Product.objects.create(barcode=barcode, **validated_data)
        return product

    def update(self, instance, validated_data):
        """Обновление объекта

        В случае, если в PUT запросе одно из необязательных полей
        будет отсутствовать, а в текущей модили это поле заполнено,
        то в результате текщее значение сотрется"""
        # TODO обрабатывать исключение KeyError: 'barcode',
        # когда мы в PUT запросе не указали эти поля
        barcode_data = validated_data.pop('barcode')
        # Текущий объект
        barcode = instance.barcode

        # Вопрос, как автоматически обновить поля экземпляра?
        instance.article = validated_data.get('article', instance.article)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.price = validated_data.get('price', instance.price)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.save()

        barcode.type = barcode_data.get('type', barcode.type)
        barcode.value = barcode_data.get('value', barcode.value)
        barcode.save()

        return instance



