FROM python:3.10.6-slim

# Allow dynamic UID/GID for the container user
ARG UID=1000
ARG GID=1000

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with dynamic UID/GID
RUN addgroup --gid $GID appuser && \
    adduser --uid $UID --gid $GID --disabled-password --gecos "" appuser

COPY --chown=appuser:appuser requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

# Create necessary directories and set ownership
RUN mkdir -p \
    uploaded_videos \
    extracted_audios \
    generated_audios \
    saved_avatars \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
