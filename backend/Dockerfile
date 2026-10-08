FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000
# One worker on purpose: the in-process scheduler must run only once
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
