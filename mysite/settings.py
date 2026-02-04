"""
Django settings for mysite project.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%dy!&_4libqp_t696-=8@g5#-=#)uv-me9p(!wemomp$am^h#x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 기존: ALLOWED_HOSTS = ['*']  (개발용)
# 수정: 실제 도메인과 IP를 명시 (보안 강화)
ALLOWED_HOSTS = [
    'vms.jongroinf.com',  # 연결할 도메인
    'localhost',
    '127.0.0.1',
    # 필요하다면 EC2 IP도 추가
]

# [중요] CSRF 신뢰 도메인 추가 (로그인 등 POST 요청 시 필수)
CSRF_TRUSTED_ORIGINS = [
    'https://vms.jongroinf.com',
    'http://vms.jongroinf.com',
    'https://vms.jongroinf.com:8000',  # [추가] 8000번 포트 명시
    'http://vms.jongroinf.com:8000',   # [추가] 8000번 포트 명시
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # [필수 추가] API 서버 기능을 위해 꼭 필요합니다.
    'rest_framework', 
    'corsheaders',
    'main',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # 최상단 배치 (유지)
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# MySQL 연동 설정 (보내주신 정보 유지)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # 주의: MySQL Workbench에 'django'라는 이름의 스키마(데이터베이스)가 생성되어 있어야 합니다.
        'NAME': 'vms_db',  
        'USER': 'vms_user',
        'PASSWORD': 'saein#09437',
        'HOST': 'localhost',
        'PORT': '3306', # 포트번호 3307이 맞는지 꼭 확인하세요 (기본값은 3306입니다)
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
# [수정] 한국 실무 환경에 맞게 변경
LANGUAGE_CODE = 'ko-kr' # 한국어
TIME_ZONE = 'Asia/Seoul' # 한국 시간
USE_I18N = True
USE_TZ = True # True로 두면 DB에는 UTC로 저장되고, 화면에는 한국 시간으로 보입니다 (권장)


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS 설정
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]