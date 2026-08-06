# Vroom application image.
#
# Builds the Django app with gunicorn. Config-driven: production settings
# (config/settings/production.py) refuse to start without SECRET_KEY,
# ALLOWED_HOSTS, and DEBUG=False, so the container must be given the same
# environment as a bare-metal deploy (see docs/deployment.md).
#
# Build locally:  docker build -t vroom:local .
# Run (example):  docker run --rm -p 8000:8000 --env-file /opt/vroom/.env vroom:local

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# gettext -> compilemessages (i18n); libmagic1 -> python-magic (document MIME).
RUN apt-get update \
    && apt-get install -y --no-install-recommends gettext libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
