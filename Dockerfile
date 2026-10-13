# Production Dockerfile for Securitisation AI Agent
FROM python:3.12-slim

# Metadata
LABEL maintainer="Zetheta Structured Finance Analytics"
LABEL project="Securitisation AI Agent (Code: 483553A)"

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and data
COPY . .

# Run test suite during build to guarantee zero-defect deployment
RUN python -m unittest discover tests -v

# Expose port
EXPOSE 8501

# Start the interactive platform
CMD ["python", "app/server.py", "8501"]
