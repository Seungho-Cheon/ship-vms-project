# main/management/commands/init_data.py
from django.core.management.base import BaseCommand
from django.db import connection
from main.models import Vessel, Seafarer, Equipment, MaintenanceJob, Certificate, WorkRestHour, NoonReport
import random
from datetime import date, timedelta

class Command(BaseCommand):
    help = '기존 데이터를 삭제하고 대규모 테스트 데이터를 생성합니다.'

    def handle(self, *args, **kwargs):
        self.stdout.write("[INFO] 데이터 초기화(TRUNCATE) 시작...")
        
        # 1. 기존 데이터 완전 삭제
        with connection.cursor() as cursor:
            cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')
            tables = ['main_noonreport', 'main_certificate', 'main_workresthour', 
                      'main_maintenancejob', 'main_equipment', 'main_seafarer', 'main_vessel']
            for table in tables:
                cursor.execute(f'TRUNCATE TABLE {table};')
            cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')
        
        self.stdout.write("[INFO] 기존 데이터 삭제 완료.")

        # 2. 선박 20척 데이터 (실제 선박명 기반)
        vessel_names = [
            "HMM Algeciras", "HMM Oslo", "HMM Copenhagen", "HMM Dublin", "HMM Gdansk",
            "HMM Hamburg", "HMM Helsinki", "HMM Le Havre", "HMM Southampton", "HMM Stockholm",
            "Maersk Mc-Kinney", "Maersk Madrid", "Maersk Munich", "Maersk Manchester", "Maersk Milan",
            "Ever Given", "Ever Gentle", "Ever Grade", "Ever Globe", "Ever Greet"
        ]
        
        vessel_types = ["CONTAINER", "BULK", "LNG", "TANKER"]
        
        created_vessels = []
        for i, name in enumerate(vessel_names):
            # 위도/경도: 전 세계 항구 및 해상 랜덤 분포
            lat = round(random.uniform(-50, 60), 4)
            lng = round(random.uniform(-160, 160), 4)
            
            v = Vessel.objects.create(
                name=name,
                imo_number=f"9{random.randint(100000, 999999)}",
                vessel_type=random.choice(vessel_types),
                built_year=random.randint(2010, 2025),
                latitude=lat,
                longitude=lng
            )
            created_vessels.append(v)

            # [장비 생성] 선박당 2~3개
            Equipment.objects.create(vessel=v, name="Main Engine", maker="Hyundai Heavy")
            Equipment.objects.create(vessel=v, name="Generator No.1", maker="STX Engine")
            if random.choice([True, False]):
                Equipment.objects.create(vessel=v, name="Ballast Pump", maker="Samsung")

            # [증서 생성] 선박당 2개 이상 (총 40개 이상)
            certs = ["Safety Construction", "IOPP Certificate", "Safety Equipment", "Load Line"]
            for c_name in random.sample(certs, 2):
                days_left = random.randint(-10, 400) # 이미 만료(-), 임박(30이하), 넉넉함
                Certificate.objects.create(
                    vessel=v, 
                    name=c_name, 
                    expiry_date=date.today() + timedelta(days=days_left)
                )

        self.stdout.write(f"[INFO] 선박 20척, 장비 및 증서 데이터 생성 완료.")

        # 3. 선원 100명 이상 생성 (선박당 5~6명)
        # 필수 직책 + 랜덤 추가 직책
        base_ranks = ['CAPTAIN', 'CHIEF_ENGINEER', 'CHIEF_MATE', 'ABLE_SEAMAN', 'ABLE_SEAMAN']
        extra_ranks = ['2ND_MATE', '3RD_MATE', 'BOSUN', 'OILER', 'COOK'] # 모델에 없는 건 기타로 처리됨(화면상)
        
        # 한국인/외국인 이름 풀
        korean_names = ["Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Yoon", "Jang", "Lim", "Han"]
        intl_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        
        seafarer_count = 0
        for v in created_vessels:
            # 5명 기본 배정
            crew_list = base_ranks.copy()
            # 1~2명 랜덤 추가
            crew_list.extend(random.sample(extra_ranks, random.randint(1, 2)))
            
            for rank in crew_list:
                # 랭크가 모델 CHOICES에 없으면 기타 처리를 위해 텍스트로 저장되거나 모델 수정 필요하지만, 
                # 현재 모델은 Choices에 제한되므로 'ABLE_SEAMAN' 등으로 매핑하거나 Choices 외 값 허용 필요.
                # 여기서는 안전하게 기존 Choices 내에서 매핑하거나, 편의상 ABLE_SEAMAN으로 통일하되 이름을 직무로 표시.
                
                real_rank = rank
                if rank not in ['CAPTAIN', 'CHIEF_ENGINEER', 'CHIEF_MATE', 'ABLE_SEAMAN']:
                    real_rank = 'ABLE_SEAMAN' # DB 제약 준수용
                    display_name = f"{random.choice(intl_names)} ({rank})" # 이름에 직무 병기
                else:
                    is_korean = random.choice([True, False])
                    name_pool = korean_names if is_korean else intl_names
                    display_name = f"{random.choice(name_pool)} {random.choice(['A', 'B', 'C'])}."

                s = Seafarer.objects.create(
                    name=display_name,
                    rank=real_rank,
                    nationality="Korea" if random.random() > 0.4 else "International",
                    vessel=v
                )
                seafarer_count += 1
                
                # [근로 관리 데이터] 선원당 1~2건 생성
                for _ in range(random.randint(1, 2)):
                    WorkRestHour.objects.create(
                        seafarer=s,
                        date=date.today() - timedelta(days=random.randint(0, 5)),
                        work_hours=random.choice([8, 9, 10, 11, 12, 14, 16]) # 15초과시 위반
                    )

        self.stdout.write(f"[INFO] 선원 {seafarer_count}명 및 근로 시간 데이터 생성 완료.")

        # 4. PMS 정비 데이터 (20건 이상)
        job_titles = ["Piston Overhaul", "Lube Oil Filter Clean", "Turbocharger Inspection", "Pump Seal Change"]
        equipments = Equipment.objects.all()
        
        for i in range(30): # 30건 생성
            equip = random.choice(equipments)
            MaintenanceJob.objects.create(
                equipment=equip,
                job_title=random.choice(job_titles),
                interval_days=random.choice([30, 90, 180, 365]),
                last_performed=date.today() - timedelta(days=random.randint(10, 400))
            )
            
        self.stdout.write("[INFO] PMS 정비 데이터 30건 생성 완료.")

        # 5. CII 모니터링 (Noon Report) - 30건 이상
        # 최근 3일간의 데이터를 랜덤한 선박에 대해 생성
        for i in range(30):
            v = random.choice(created_vessels)
            NoonReport.objects.create(
                vessel=v,
                report_date=date.today() - timedelta(days=random.randint(0, 10)),
                latitude=v.latitude + random.uniform(-0.5, 0.5),
                longitude=v.longitude + random.uniform(-0.5, 0.5),
                sog=random.uniform(10, 20),
                distance=random.uniform(200, 400),
                fuel_consumption=random.uniform(20, 50)
            )

        self.stdout.write("[INFO] CII/Noon Report 데이터 30건 생성 완료.")
        self.stdout.write("[SUCCESS] 모든 데이터 준비가 완료되었습니다!")