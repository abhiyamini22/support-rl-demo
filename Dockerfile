FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY hf_requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r hf_requirements.txt

# Copy application files
COPY hf_app.py .
COPY hf_env.py .

# Create a simple README
RUN echo "# Customer Support Environment\nA demo customer support environment for Hugging Face Spaces." > README.md

# Expose the port
EXPOSE 7860

# Set environment variables
ENV PYTHONPATH=/app
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Run the application
CMD ["python", "hf_app.py"]
