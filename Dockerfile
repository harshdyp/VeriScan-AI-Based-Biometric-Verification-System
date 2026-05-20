# Use official Python image
FROM python:3.9

# Set work directory
WORKDIR /app

# Copy project files
COPY . .

# Ensure src is on PYTHONPATH
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Install Tesseract for OCR (Linux)
RUN apt-get update && apt-get install -y tesseract-ocr

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose backend and frontend ports
EXPOSE 8000 8501

# Default command: run backend
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# To run frontend in another container or process:
# streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 