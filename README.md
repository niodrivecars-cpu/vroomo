# Vroomo

نظام إدارة أسطول المركبات (Fleet Management System)

## المتطلبات

- Python 3.11+
- Docker Desktop
- Git

## البدء السريع

```powershell
# 1. نسخ إعدادات البيئة
cp .env.example .env
# ثم عدّل .env بوضع SECRET_KEY وقاعدة البيانات

# 2. تشغيل الإعداد الكامل
.\setup.ps1
# أو خطوة بخطوة:
.\setup.ps1 db       # MySQL 8 عبر Docker
.\setup.ps1 migrate  # ترحيل قاعدة البيانات
.\setup.ps1 superuser# إنشاء مشرف
.\setup.ps1 run      # تشغيل الخادم

# 3. فتح المتصفح على:
#    http://localhost:8000
```

## الإعداد اليدوي

```powershell
# 1. الحزم
python -m pip install -r requirements.txt

# 2. قاعدة البيانات
docker compose up -d

# 3. الترحيل
python manage.py migrate

# 4. المشرف
python manage.py createsuperuser

# 5. التشغيل
python manage.py runserver
```

## البيئة

| متغير | شرح |
|-------|------|
| `SECRET_KEY` | مفتاح التشفير (غيّره للإنتاج) |
| `DEBUG` | `True` للتطوير، `False` للإنتاج |
| `DB_NAME` | اسم قاعدة البيانات |
| `DB_USER` | مستخدم MySQL |
| `DB_PASSWORD` | كلمة مرور MySQL |
| `DB_HOST` | مضيف MySQL (`localhost`) |
| `DB_PORT` | منفذ MySQL (`3306`) |
| `ALLOWED_HOSTS` | أسماء النطاقات المسموحة |
| `ADMIN_EMAIL` | بريد المدير للتنبيهات |
| `EMAIL_HOST_USER` | بريد Gmail للإرسال |
| `EMAIL_HOST_PASSWORD` | كلمة مرور تطبيق Gmail |

## الاختبارات

```powershell
python manage.py test fleet --settings=config.test_settings --verbosity=2
```
