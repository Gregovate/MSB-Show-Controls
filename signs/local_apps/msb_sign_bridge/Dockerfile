FROM python:3.12-slim-bookworm
# Install Central Time data and a bold Linux font.
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata fonts-liberation2 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install --no-cache-dir sacn==1.11.0 Pillow==11.3.0 paho-mqtt==2.1.0
COPY bridge.py engine.py /app/
ENV PYTHONUNBUFFERED=1
# Receive shutdown signals directly so both signs are released.
CMD ["python", "/app/bridge.py"]
