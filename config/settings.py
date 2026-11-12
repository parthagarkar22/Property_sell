import os
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Existing environment variables win, so Vercel settings are not replaced by a local .env file.
load_dotenv(override=False)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-key-change-me")
DEBUG = os.getenv("DEBUG", "True").lower() in ("1", "true", "yes")
if not DEBUG and SECRET_KEY == "django-insecure-dev-key-change-me":
    raise ImproperlyConfigured("Set SECRET_KEY before deploying with DEBUG=False.")

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]
if ".vercel.app" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(".vercel.app")

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
if not DEBUG and "https://*.vercel.app" not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append("https://*.vercel.app")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "storages",
    "django.contrib.humanize",
    "accounts",
    "properties",
    "dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "properties.context_processors.business_info",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if DATABASE_URL:
    # conn_max_age 0: each Vercel request is short-lived.
    # Server-side cursors and prepared statements break Supabase's transaction pooler (port 6543).
    DATABASES = {"default": dj_database_url.config(default=DATABASE_URL, conn_max_age=0, ssl_require=True)}
    DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True
    DATABASES["default"].setdefault("OPTIONS", {})
    DATABASES["default"]["OPTIONS"]["prepare_threshold"] = None
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-in"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

SUPABASE_S3_ACCESS_KEY = os.getenv("SUPABASE_S3_ACCESS_KEY", "").strip()
SUPABASE_S3_SECRET_KEY = os.getenv("SUPABASE_S3_SECRET_KEY", "").strip()
SUPABASE_S3_ENDPOINT = os.getenv("SUPABASE_S3_ENDPOINT", "").strip().rstrip("/")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "property-photos").strip() or "property-photos"
SUPABASE_REGION = os.getenv("SUPABASE_REGION", "ap-south-1").strip() or "ap-south-1"

if SUPABASE_S3_ACCESS_KEY and SUPABASE_S3_SECRET_KEY and SUPABASE_S3_ENDPOINT:
    AWS_ACCESS_KEY_ID = SUPABASE_S3_ACCESS_KEY
    AWS_SECRET_ACCESS_KEY = SUPABASE_S3_SECRET_KEY
    AWS_STORAGE_BUCKET_NAME = SUPABASE_BUCKET
    AWS_S3_ENDPOINT_URL = SUPABASE_S3_ENDPOINT
    AWS_S3_REGION_NAME = SUPABASE_REGION
    AWS_S3_ADDRESSING_STYLE = "path"
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False
    _supabase_host = urlparse(SUPABASE_S3_ENDPOINT).netloc
    AWS_S3_CUSTOM_DOMAIN = f"{_supabase_host}/storage/v1/object/public/{SUPABASE_BUCKET}"
    AWS_S3_URL_PROTOCOL = "https:"
    STORAGES["default"] = {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.Customer"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "properties:list"
LOGOUT_REDIRECT_URL = "properties:home"

# Business contact — Call / WhatsApp shown on website
FATHER_PHONE = os.getenv("FATHER_PHONE", "7972926211").strip() or "7972926211"
FATHER_WHATSAPP = (os.getenv("FATHER_WHATSAPP", "") or "7972926211").strip() or "7972926211"
FATHER_NAME = os.getenv("FATHER_NAME", "Baba Khatu Shyam Real Estate")
FATHER_NAME_HI = os.getenv("FATHER_NAME_HI", "बाबा खाटू श्याम रियल इस्टेट")
FATHER_OWNER = os.getenv("FATHER_OWNER", "Prashant Agarkar")
FATHER_EMAIL = os.getenv("FATHER_EMAIL", "")

# Email (optional backup alerts)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("1", "true", "yes")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or "noreply@amravati-properties.local"

# Optional SMS alerts to broker (customers use mobile + password login)
OTP_EXPIRY_SECONDS = 600
OTP_RATE_LIMIT_SECONDS = 60
FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY", "").strip()
DEBUG_SMS = os.getenv("DEBUG_SMS", "False").lower() in ("1", "true", "yes")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "amravati-otp",
    }
}
