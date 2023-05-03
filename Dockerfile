# Base image
FROM python:3.9

ARG OUT_PORT

# Set working directory
WORKDIR /app

# Copy source code to container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for Flask
EXPOSE $OUT_PORT

# Run Python file
CMD ["python", "betteryear.py"]