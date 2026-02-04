# main/serializers.py
from rest_framework import serializers
from .models import Vessel, Seafarer, Equipment, MaintenanceJob, NoonReport, Certificate, WorkRestHour

# 1. 선박
class VesselSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_vessel_type_display', read_only=True)
    crew_count = serializers.IntegerField(source='crew.count', read_only=True)
    class Meta:
        model = Vessel
        fields = '__all__'

# 2. 선원
class SeafarerSerializer(serializers.ModelSerializer):
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)
    vessel_name = serializers.CharField(source='vessel.name', read_only=True)
    class Meta:
        model = Seafarer
        fields = '__all__'

# 3. 장비
class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'

# 4. PMS 정비
class MaintenanceJobSerializer(serializers.ModelSerializer):
    vessel_name = serializers.CharField(source='equipment.vessel.name', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    next_due_date = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    class Meta:
        model = MaintenanceJob
        fields = '__all__'

# 5. [신규] 운항 일보 (Noon Report)
class NoonReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoonReport
        fields = '__all__'

# 6. [신규] 증서 (Certificate)
class CertificateSerializer(serializers.ModelSerializer):
    days_left = serializers.ReadOnlyField()
    vessel_name = serializers.CharField(source='vessel.name', read_only=True)
    class Meta:
        model = Certificate
        fields = '__all__'

# 7. [신규] 근로 시간 (Work/Rest)
class WorkRestHourSerializer(serializers.ModelSerializer):
    seafarer_name = serializers.CharField(source='seafarer.name', read_only=True)
    rest_hours = serializers.ReadOnlyField()
    is_violation = serializers.ReadOnlyField()
    class Meta:
        model = WorkRestHour
        fields = '__all__'