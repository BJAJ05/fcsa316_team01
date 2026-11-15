# Django API image.
# Layer order matters for the build cache: dependencies are installed before the
# source code is copied, so editing code does not re-run `pip install`.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Run as a normal user, not root. /app stays writable for it (SQLite in a standalone run).
RUN useradd --create-home app && chown app /app

# 1) Dependencies: this layer is rebuilt only when requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Source code: changes often, so it comes last.
COPY --chown=app:app . .

# Gather the admin's CSS/JS into staticfiles/ (served by WhiteNoise). The settings need a
# secret key to load; this throwaway value exists only during the build.
RUN DJANGO_SECRET_KEY=collectstatic-only DB_ENGINE=sqlite python manage.py collectstatic --noinput

USER app

EXPOSE 8000

# entrypoint.sh applies migrations when RUN_MIGRATIONS=1, then starts the CMD.
# Called through `sh` so it works even if the file lost its executable bit (e.g. on Windows).
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-"]
