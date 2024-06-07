FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Install Python packages
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application files
COPY consumer_health_check_service.py /app/consumer_health_check_service.py

# Set the working directory
WORKDIR /app

# Expose port 5001
EXPOSE 5001

# Run the application
CMD ["python", "consumer_health_check_service.py"]
