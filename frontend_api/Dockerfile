FROM python:3.13
WORKDIR /app

# Copy requirements from the root directory (now accessible due to changed build context)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only this service's application code
COPY ./frontend_api .

# Command is specified in docker-compose.yml
# This is a fallback command if not overridden
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]