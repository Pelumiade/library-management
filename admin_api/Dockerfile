FROM python:3.11-slim

WORKDIR /app

COPY admin_api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY admin_api/ .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]