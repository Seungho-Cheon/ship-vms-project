# mysite/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from main import views

router = DefaultRouter()
# 기존 API
router.register(r'vessels', views.VesselViewSet)
router.register(r'seafarers', views.SeafarerViewSet)
router.register(r'equipments', views.EquipmentViewSet)
router.register(r'maintenance-jobs', views.MaintenanceJobViewSet)

# [신규] 고급 기능 API
router.register(r'noon-reports', views.NoonReportViewSet)
router.register(r'certificates', views.CertificateViewSet)
router.register(r'work-hours', views.WorkRestHourViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]