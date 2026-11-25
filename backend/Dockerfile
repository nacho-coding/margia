FROM python:3.13-slim@sha256:7249d5587b78209a006dc4a3b5340678f84ea729239193aa559962cd8c1fce50
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2
WORKDIR /app
COPY requirements.lock ./requirements.lock
RUN pip install --no-cache-dir -r requirements.lock && useradd --uid 10001 --create-home margia && mkdir /app/evaluacion && chown margia:margia /app/evaluacion
COPY --chown=margia:margia . .
USER margia
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && python -m app.datos.seed && python -m app.modelos.servicio && python -m app.datos.historia_search && python -m app.creatividad.servicio && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --no-access-log"]
