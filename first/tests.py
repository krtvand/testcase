from datetime import date
from datetime import timedelta

from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory

from . import models
from . import serializers


class ParcelTests(APITestCase):
    """
    Тестируем CRUD для посылки
    """
    fixtures = ['first_models.json', 'users.json']

    def setUp(self):
        self.client.force_authenticate(user=User.objects.get(username='reviewer'))

        factory = APIRequestFactory()
        self.request = factory.get('/')

    def test_read_parcel_list(self):
        response = self.client.get(reverse('parcel-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_parcel_detail(self):
        parcel = models.Parcel.objects.first()
        response = self.client.get(reverse('parcel-detail', args=[parcel.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_isdeliv_isrefuse(self):
        """
        Пытаемся установить флаг isrefused = True для посылки,
        у которой уже установлен флаг isdelivered=True
        """
        parcel = models.Parcel.objects.filter(isdelivered=True).first()
        data_s = serializers.ParcelSerializer(
            instance=parcel,
            context={'request': Request(self.request)})
        data = data_s.data
        data['isrefused'] = True
        response = self.client.put(reverse('parcel-detail', args=[parcel.id]), data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_departure_date(self):
        """
        Пытаемся установить дату вручения, раньше чем дату отправления
        """
        parcel = models.Parcel.objects.first()
        data_s = serializers.ParcelSerializer(
            instance=parcel,
            context={'request': Request(self.request)})
        data = data_s.data
        data['departure_date'] = date.today()
        data['delivery_date'] = date.today() + timedelta(days=-5)
        response = self.client.put(reverse('parcel-detail', args=[parcel.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductTests(APITestCase):
    """
    Тестируем CRUD для товара
    """
    def setUp(self):
        self.superuser = User.objects.create_superuser('reviewer', 'reviewer@snow.com', '$1mb1r$0ft')
        self.user = User.objects.get(username='reviewer')
        self.client.force_authenticate(user=self.user)

        factory = APIRequestFactory()
        self.request = factory.get('/')

        self.vendor = models.Vendor.objects.create(name='Apple')
        self.barcode_type = models.BarcodeType.objects.create(type='EAN-13')
        barcode = models.Barcode.objects.create(type=self.barcode_type, value='987654321012')
        self.product = models.Product.objects.create(
            article='123456789',
            name='iPhone',
            price=99.32,
            weight=0.30,
            vendor=self.vendor,
            barcode=barcode
        )

    def test_create_product(self):
        """
        Создание
        """
        url = reverse('product-list')
        article = "9874563245"
        cur_obj_count = models.Product.objects.count()
        data = {
            "article": article,
            "name": "testproduct",
            "price": "12.32",
            "weight": "45.30",
            "vendor": "http://194.54.64.91:8000/vendors/{}/".format(self.vendor.id),
            "barcode": {
                "type": "http://194.54.64.91:8000/barcodetypess/{}/".format(self.barcode_type.id),
                "value": "2400000032632"
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Product.objects.count(), cur_obj_count + 1)
        self.assertEqual(models.Product.objects.get(name='testproduct').article, article)

    def test_update_product(self):
        data_s = serializers.ProductSerializer(instance=self.product, context={'request': Request(self.request)})
        data = data_s.data
        data['price'] = 89.9
        response = self.client.put(reverse('product-detail', args=[self.product.id]), data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_product_list(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_read_product_detail(self):
        response = self.client.get(reverse('product-detail', args=[self.product.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
