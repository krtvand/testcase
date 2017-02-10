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

    # TODO изменять название изображений при загрузке на уникальное, при
    # DELETE запросах, удалять из файловой системы

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
        product = models.Product.objects.create(barcode=barcode,
                                                **validated_data)
        return product

    def update(self, instance, validated_data):
        """Обновление объекта

        В случае, если в PUT запросе одно из необязательных полей
        будет отсутствовать, а в текущей модили это поле заполнено,
        то в результате текщее значение сотрется"""

        # TODO обрабатывать исключение KeyError: 'barcode',
        # когда мы в PUT запросе не указали эти поля
        # TODO удалять фото при PUT запросе в случае, если
        # соответсвующее поле изменилось на пустое

        barcode_data = validated_data.pop('barcode')
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


class FullnameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Fullname
        fields = ('first_name', 'surname', 'patronymic')


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = ('postal_code', 'country', 'state', 'city', 'address')


class RecipientSerializer(serializers.HyperlinkedModelSerializer):
    # TODO изменять название изображений при загрузке на уникальное, при
    # DELETE запросах, удалять из файловой системы

    fullname = FullnameSerializer()
    address = AddressSerializer()

    class Meta:
        model = models.Recipient
        fields = ('url', 'fullname', 'address', 'photo', 'registration_date')
        read_only_fields = ('registration_date',)

    def create(self, validated_data):
        fullname_data = validated_data.pop('fullname')
        fullname = models.Fullname.objects.create(**fullname_data)
        address_data = validated_data.pop('address')
        address = models.Address.objects.create(**address_data)
        recipient = models.Recipient.objects.create(fullname=fullname,
                                                    address=address,
                                                    **validated_data)
        return recipient

    def update(self, instance, validated_data):
        """Обновление объекта

        В случае, если в PUT запросе одно из необязательных полей
        будет отсутствовать, а в текущей модили это поле заполнено,
        то в результате текщее значение сотрется

        """
        # TODO обрабатывать исключение KeyError: 'barcode',
        # когда мы в PUT запросе не указали эти поля
        # TODO удалять фото при PUT запросе в случае, если
        # соответсвующее поле изменилось на пустое

        fullname_data = validated_data.pop('fullname')
        fullname = instance.fullname
        address_data = validated_data.pop('address')
        address = instance.address

        # Вопрос, как автоматически обновить поля экземпляра?
        instance.photo = validated_data.get('photo', instance.photo)
        instance.save()

        fullname.first_name = fullname_data.get('first_name', fullname.first_name)
        fullname.surname = fullname_data.get('surname', fullname.surname)
        fullname.patronymic = fullname_data.get('patronymic', fullname.patronymic)
        fullname.save()

        address.postal_code = address_data.get('postal_code', address.postal_code)
        address.country = address_data.get('country', address.country)
        address.state = address_data.get('state', address.state)
        address.city = address_data.get('city', address.city)
        address.address = address_data.get('address', address.address)
        address.save()

        return instance


class ParcelSerializer(serializers.ModelSerializer):
    products = serializers.HyperlinkedRelatedField(many=True,
                                                   view_name='product-detail',
                                                   queryset=models.Product.objects.all())
    recipient = serializers.HyperlinkedRelatedField(view_name='recipient-detail',
                                                    queryset=models.Recipient.objects.all())

    class Meta:
        model = models.Parcel
        fields = ('url', 'recipient', 'isdelivered', 'isrefused', 'departure_date',
                  'delivery_date', 'cost_of_delivery', 'products')

    # def create(self, validated_data):
    #     recipient_data = validated_data.pop('recipient')
    #     recipient = models.Recipient.objects.create(recipient_data)
    #
    #     products_data = validated_data.pop('products')
    #     products = models.Product.objects.create(**products_data)
    #
    #     parcel = models.Parcel.objects.create(recipient=recipient,
    #                                           products=products,
    #                                           **validated_data)
    #     return parcel
