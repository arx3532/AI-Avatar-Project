FROM python:3.10.6-slim

# Allow dynamic UID/GID for the container user
ARG UID=1000
ARG GID=1000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY sadtalker_utils.py .
COPY inference.py .

COPY checkpoints/ ./checkpoints/
COPY gfpgan/ ./gfpgan/
COPY src/ ./src/

# Create necessary directory and set ownership
RUN mkdir -p generated_videos && \
    chown -R $UID:$GID /app

# Create non-root user with dynamic UID/GID
RUN addgroup --gid $GID appuser && \
    adduser --uid $UID --gid $GID --disabled-password --gecos "" appuser

USER appuser

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
