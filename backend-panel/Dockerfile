FROM python:3.14-slim AS wheels
WORKDIR /wheels
RUN apt-get update && apt-get install -y --no-install-recommends build-essential default-libmysqlclient-dev pkg-config && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements-railway.txt ./
RUN pip wheel --no-cache-dir --wheel-dir /wheels/packages -r requirements-railway.txt

FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_SETTINGS_MODULE=config.settings_railway
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libmariadb3 gosu && rm -rf /var/lib/apt/lists/* && useradd --create-home --uid 10001 app
COPY requirements.txt requirements-railway.txt ./
COPY --from=wheels /wheels/packages /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements-railway.txt && rm -rf /wheels
COPY . .
# Solo recopila recursos públicos durante la construcción; no conecta ni migra la base.
RUN DJANGO_SECRET_KEY=build-only-static-resources-no-auth LPN_PRIVATE_ROOT=/tmp/build-private python manage.py collectstatic --noinput
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["sh", "-c", "exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 60"]
