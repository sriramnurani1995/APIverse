# Use the latest stable Python version
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy all source files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose only Flask (5000)
EXPOSE 8080

# Keep FastAPI internal (8000 is NOT exposed)
CMD ["python", "run.py"]
