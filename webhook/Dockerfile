FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Copy run script
COPY run.sh .
RUN chmod +x run.sh

# Expose port
EXPOSE 8099

# Run the application
CMD ["/app/run.sh"]
