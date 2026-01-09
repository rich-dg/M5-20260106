FROM python:3.12.3-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY source/ ./source/
COPY data/ ./data/

RUN mkdir -p /library_data

ENV PYTHONPATH=/app
ENTRYPOINT ["python3", "source/library_load_csv.py"]