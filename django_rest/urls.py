from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from rest_framework import routers

from first import views

router = routers.DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'recipients', views.RecipientViewSet)
router.register(r'parcels', views.ParcelViewSet)
router.register(r'vendors', views.VendorViewSet)
router.register(r'barcodes', views.BarcodeViewSet)
router.register(r'barcodetypess', views.BarcodeTypeViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

