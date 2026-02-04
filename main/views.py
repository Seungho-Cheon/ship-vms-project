from rest_framework import viewsets
# [중요] 기존 모델뿐만 아니라 새로 추가한 NoonReport, Certificate, WorkRestHour를 모두 import 해야 합니다.
from .models import Vessel, Seafarer, Equipment, MaintenanceJob, NoonReport, Certificate, WorkRestHour
from .serializers import (
    VesselSerializer, SeafarerSerializer, EquipmentSerializer, MaintenanceJobSerializer,
    NoonReportSerializer, CertificateSerializer, WorkRestHourSerializer
)

# 1. 선박 뷰셋
class VesselViewSet(viewsets.ModelViewSet):
    queryset = Vessel.objects.all().order_by('-created_at')
    serializer_class = VesselSerializer

# 2. 선원 뷰셋
class SeafarerViewSet(viewsets.ModelViewSet):
    queryset = Seafarer.objects.all().order_by('rank')
    serializer_class = SeafarerSerializer

# 3. 장비 뷰셋
class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer

# 4. PMS 정비 뷰셋
class MaintenanceJobViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceJob.objects.all().order_by('last_performed')
    serializer_class = MaintenanceJobSerializer

# 5. [신규] 운항 일보 뷰셋
class NoonReportViewSet(viewsets.ModelViewSet):
    queryset = NoonReport.objects.all().order_by('-report_date')
    serializer_class = NoonReportSerializer

    # 리포트 제출 시 선박 위치 자동 업데이트 로직
    def perform_create(self, serializer):
        instance = serializer.save()
        vessel = instance.vessel
        vessel.latitude = instance.latitude
        vessel.longitude = instance.longitude
        vessel.save()

# 6. [신규] 증서 뷰셋
class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all().order_by('expiry_date')
    serializer_class = CertificateSerializer

# 7. [신규] 근로 시간 뷰셋
class WorkRestHourViewSet(viewsets.ModelViewSet):
    queryset = WorkRestHour.objects.all().order_by('-date')
    serializer_class = WorkRestHourSerializer