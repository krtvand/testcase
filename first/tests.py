from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory

from . import models
from . import serializers


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
        print('create ', response.data)
        print(self.product.id)
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


