import decimal
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from . import models

PARCEL_MAX_WEIGHT = 100
PARCEL_MIN_WEIGHT = 0.1
PARCEL_MAX_PRICE = 1000
PARCEL_COST_OF_DELIVERY_PCT = 0.13


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
        if 'barcode' in validated_data:
            barcode_data = validated_data.pop('barcode')
            barcode = models.Barcode.objects.create(**barcode_data)
            product = models.Product.objects.create(barcode=barcode,
                                                    **validated_data)
        else:
            # TODO проверить создание товара без штрих-кода
            product = models.Product.objects.create(**validated_data)
        return product

    def update(self, instance, validated_data):
        """Обновление объекта

        В случае, если в PUT запросе одно из необязательных полей
        будет отсутствовать, а в текущей модили это поле заполнено,
        то в результате текщее значение сотрется"""
        # TODO удалять фото при PUT запросе в случае, если
        # соответсвующее поле изменилось на пустое

        if 'barcode' in validated_data:
            barcode_data = validated_data.pop('barcode')
            barcode = instance.barcode
            barcode.type = barcode_data.get('type', barcode.type)
            barcode.value = barcode_data.get('value', barcode.value)
            barcode.save()

        # Вопрос, как автоматически обновить поля экземпляра?
        instance.article = validated_data.get('article', instance.article)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.price = validated_data.get('price', instance.price)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.save()

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
        # TODO удалять фото при PUT запросе в случае, если
        # соответсвующее поле изменилось на пустое

        if 'fullname' in validated_data:
            fullname_data = validated_data.pop('fullname')
            fullname = instance.fullname
            fullname.first_name = fullname_data.get('first_name', fullname.first_name)
            fullname.surname = fullname_data.get('surname', fullname.surname)
            fullname.patronymic = fullname_data.get('patronymic', fullname.patronymic)
            fullname.save()

        if 'address' in validated_data:
            address_data = validated_data.pop('address')
            address = instance.address
            address.postal_code = address_data.get('postal_code', address.postal_code)
            address.country = address_data.get('country', address.country)
            address.state = address_data.get('state', address.state)
            address.city = address_data.get('city', address.city)
            address.address = address_data.get('address', address.address)
            address.save()

        # Вопрос, как автоматически обновить поля экземпляра?
        instance.photo = validated_data.get('photo', instance.photo)
        instance.save()

        return instance


class ParcelValidatorMixin:
    def isdeliv_isrefus_validate(self, data):
        """Проверка флагов 'isdelivered', 'isrefused'

        Признак вручения не может быть установлен
        одновременно с признаком отказа
        Рассматриваем 3 случая:
        1) Оба параметра заданы в запросе
        2) В запросе isdelivered=True, isrefused не задан,
           а в экземпляре уже задан isrefused=True
        3) В запросе isrefused=True, isdelivered не задан,
           а в экземпляре уже задан isdelivered=True
        """

        bad_conditions = []
        # В запросе оба параметра заданы как True
        try:
            bad_conditions.append(
                all(('isdelivered' in data,
                     'isrefused' in data,
                     data['isdelivered'] and data['isrefused']
                     )))
        except (KeyError, TypeError):
            bad_conditions.append(False)
        # В запросе isdelivered=True, isrefused не задан,
        # а в экземпляре уже задан isrefused=True
        try:
            bad_conditions.append(
                all(('isdelivered' in data,
                     'isrefused' not in data,
                     data['isdelivered'] and self.instance.isrefused
                     )))
        except (KeyError, AttributeError, TypeError):
            bad_conditions.append(False)
        # В запросе isrefused=True, isdelivered не задан,
        # а в экземпляре уже задан isdelivered=True
        try:
            bad_conditions.append(
                all(('isdelivered' not in data,
                     'isrefused' in data,
                     data['isrefused'] and self.instance.isdelivered
                     )))
        except (KeyError, AttributeError, TypeError):
            bad_conditions.append(False)

        if any(bad_conditions):
            raise serializers.ValidationError("Delivered flag can not be installed "
                                              "simultaneously with refused flag")

    def deliv_depart_dates_validate(self, data):
        """Дата вручения не должна предшествовать дате отправки.

        Рассматриваем 3 случая:
          1) оба параметра получаем в запросе
          2) запрос содержит только только дату отпраки,
             а в экземпляре уже сохранена дата вручения
          3) запрос содержит только дату вручения,
             а в экземпляре уже сохранена дата отправки
        """

        # Проверяем наличие ряда ошибочных условий
        bad_conditions = []
        # 1) оба параметра получаем в запросе
        try:
            bad_conditions.append(
                all(['departure_date' in data,
                     'delivery_date' in data,
                     data['departure_date'] > data['delivery_date']
                     ]))
        except (KeyError, TypeError):
            bad_conditions.append(False)

        # 2) запрос содержит только только дату отпраки,
        #    а в экземпляре уже сохранена дата вручения
        try:
            bad_conditions.append(
                all(['departure_date' in data,
                     'delivery_date' not in data,
                     data['departure_date'] > self.instance.delivery_date
                     ]))
        except (KeyError, AttributeError, TypeError):
            bad_conditions.append(False)
        # 3) запрос содержит только дату вручения,
        #    а в экземпляре уже сохранена дата отправки
        try:
            bad_conditions.append(
                all(['delivery_date' in data,
                     'departure_date' not in data,
                     self.instance.departure_date > data['delivery_date']
                     ]))
        except (KeyError, AttributeError, TypeError):
            bad_conditions.append(False)

        if any(bad_conditions):
            raise serializers.ValidationError("Delivery date can not be "
                                              "earlier than departure")

    def parcel_weight_validate(self, data):
        if 'products' in data:
            products = data['products']
            # Проверка массы посылки
            parcel_weight = sum(p.weight for p in products)
            if parcel_weight > PARCEL_MAX_WEIGHT:
                raise serializers.ValidationError("Parsel weight should be less "
                                                  "then {}".format(PARCEL_MAX_WEIGHT))
            elif parcel_weight < PARCEL_MIN_WEIGHT:
                raise serializers.ValidationError("Parsel weight should be more "
                                                  "then {}".format(PARCEL_MIN_WEIGHT))

    def parcel_price_validate(self, data):
        if 'products' in data:
            products = data['products']

            # Проверка стоимости посылки
            parcel_price = sum(p.price for p in products)
            if parcel_price > PARCEL_MAX_PRICE:
                raise serializers.ValidationError("Parsel price should be less "
                                                  "then {}".format(PARCEL_MAX_PRICE))



class ParcelSerializer(ParcelValidatorMixin, serializers.ModelSerializer):
    products = serializers.HyperlinkedRelatedField(many=True,
                                                   view_name='product-detail',
                                                   queryset=models.Product.objects.all())
    recipient = serializers.HyperlinkedRelatedField(view_name='recipient-detail',
                                                    queryset=models.Recipient.objects.all())

    class Meta:
        model = models.Parcel
        fields = ('url', 'recipient', 'isdelivered', 'isrefused', 'departure_date',
                  'delivery_date', 'cost_of_delivery', 'products')
        read_only_fields = ('cost_of_delivery',)

    def validate(self, data):
        """ Валидация данных

        Вес посылки должен быть меньше PARCEL_MAX_WEIGHT кг,
        но больше PARCEL_MIN_WEIGHT г.
        Стоимость посылки не должна превышать PARCEL_MAX_WEIGHT евро.
        Дата вручения не должна предшествовать дате отправки.
        Признак вручения не может быть установлен
        одновременно с признаком отказа
        """

        self.isdeliv_isrefus_validate(data)
        self.deliv_depart_dates_validate(data)
        self.parcel_weight_validate(data)
        self.parcel_price_validate(data)

        return data

    def save(self, **kwargs):
        instance = super().save(**kwargs)

        instance.cost_of_delivery = \
            sum(p.price for p in instance.products.all()) * \
            decimal.Decimal(PARCEL_COST_OF_DELIVERY_PCT)

        instance.save()

        return self.instance

