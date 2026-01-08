FROM python:3.9.7-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update \
     && apt-get install -y --no-install-recommends \
         build-essential gcc libpq-dev \
         libxml2-dev libxslt1-dev zlib1g-dev \
         libssl-dev libffi-dev pkg-config \
        libjpeg-dev libpng-dev libfreetype6-dev libwebp-dev libtiff5-dev \
        rustc cargo \
        python3-dev libpython3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade "pip<24.1" setuptools wheel

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN mkdir -p /vol/static /var/celery

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "Healthy_Care.wsgi:application", "--bind", "0.0.0.0:8000"]
