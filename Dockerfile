# Builder stage
FROM python:3.10-slim as builder

RUN apt-get update &&  \
    apt-get install -y libpq-dev gcc ffmpeg

# Create the virtual environment
RUN python -m venv /opt/venv
# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt


# Operational stage
FROM python:3.10-slim

RUN apt-get update &&  \
    apt-get install -y libpq-dev ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Get the virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application
COPY src /src

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]