FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Set environment variables
ENV DATABASE_PATH=/app/data/bot_data.db
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Expose port for Hugging Face
EXPOSE 7860

# Run the bot
CMD ["python", "app.py"]
