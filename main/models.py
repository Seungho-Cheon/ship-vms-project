from django.db import models
from django.utils import timezone
from datetime import timedelta

# 1. 선박 정보
class Vessel(models.Model):
    VESSEL_TYPES = [
        ('CONTAINER', '컨테이너선'),
        ('BULK', '벌크선'),
        ('LNG', 'LNG선'),
        ('TANKER', '유조선'),
    ]
    name = models.CharField(max_length=100, verbose_name="선박명")
    imo_number = models.CharField(max_length=20, unique=True, verbose_name="IMO 번호")
    vessel_type = models.CharField(max_length=20, choices=VESSEL_TYPES, verbose_name="선종")
    built_year = models.IntegerField(verbose_name="건조년도")
    # [추가됨] 위치 정보 (기본값은 부산항 근처로 설정)
    latitude = models.FloatField(default=35.10)  # 위도
    longitude = models.FloatField(default=129.04) # 경도
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 2. 선원 정보
class Seafarer(models.Model):
    RANKS = [
        ('CAPTAIN', '선장'),
        ('CHIEF_MATE', '1항사'),
        ('CHIEF_ENGINEER', '기관장'),
        ('ABLE_SEAMAN', '갑판수'),
    ]
    name = models.CharField(max_length=50, verbose_name="성명")
    rank = models.CharField(max_length=20, choices=RANKS, verbose_name="직책")
    nationality = models.CharField(max_length=50, verbose_name="국적")
    vessel = models.ForeignKey(Vessel, related_name='crew', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_rank_display()})"

# 3. 장비 정보 (PMS 대상)
class Equipment(models.Model):
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, related_name='equipments')
    name = models.CharField(max_length=100, verbose_name="장비명") 
    maker = models.CharField(max_length=100, verbose_name="제조사", blank=True)

    def __str__(self):
        return f"[{self.vessel.name}] {self.name}"

# 4. 정비 작업 (PMS Job)
class MaintenanceJob(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='jobs')
    job_title = models.CharField(max_length=200, verbose_name="작업명")
    interval_days = models.IntegerField(verbose_name="정비 주기(일)")
    last_performed = models.DateField(verbose_name="최근 정비일")

    @property
    def next_due_date(self):
        return self.last_performed + timedelta(days=self.interval_days)

    @property
    def is_overdue(self):
        return timezone.now().date() > self.next_due_date

    def __str__(self):
        return self.job_title

# main/models.py (기존 코드 아래에 추가)

# 5. 운항 일보 (Noon Report) & CII 데이터
class NoonReport(models.Model):
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, related_name='noon_reports')
    report_date = models.DateField(default=timezone.now)
    # 위치 정보 (입력 시 선박 위치 자동 갱신용)
    latitude = models.FloatField()
    longitude = models.FloatField()
    # 운항 데이터
    sog = models.FloatField(verbose_name="평균 속도(Knot)")
    distance = models.FloatField(verbose_name="운항 거리(NM)")
    fuel_consumption = models.FloatField(verbose_name="연료 소모량(MT)") # CII 계산용
    
    # CII 등급 계산 (간이 로직: 소모량/거리)
    @property
    def cii_score(self):
        if self.distance == 0: return 0
        return round(self.fuel_consumption / self.distance * 1000, 2)

    def __str__(self):
        return f"[{self.vessel.name}] {self.report_date}"

# 6. 증서 및 검사 (Certificate) - 스마트 알림
class Certificate(models.Model):
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, related_name='certificates')
    name = models.CharField(max_length=100, verbose_name="증서명")
    expiry_date = models.DateField(verbose_name="만료일")
    
    @property
    def days_left(self):
        return (self.expiry_date - timezone.now().date()).days

    @property
    def is_expiring_soon(self):
        return 0 < self.days_left <= 30 # 30일 이내 만료 임박

    def __str__(self):
        return self.name

# 7. 선원 근로/휴식 시간 (Work/Rest Hours)
class WorkRestHour(models.Model):
    seafarer = models.ForeignKey(Seafarer, on_delete=models.CASCADE, related_name='work_hours')
    date = models.DateField(default=timezone.now)
    work_hours = models.FloatField(verbose_name="총 근로 시간")
    
    @property
    def rest_hours(self):
        return 24 - self.work_hours
    
    @property
    def is_violation(self):
        return self.rest_hours < 10 # STCW 규정: 최소 10시간 휴식 필요

    def __str__(self):
        return f"{self.seafarer.name} - {self.date}"
        