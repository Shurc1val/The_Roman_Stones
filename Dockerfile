FROM python:latest

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY validate_heart_rate.py .
COPY static/ .
COPY templates/ .



CMD python3 pipeline.py