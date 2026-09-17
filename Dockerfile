FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py seed.py database.py ./
COPY dashboard.html login.html ./
RUN useradd --create-home app && mkdir /data && chown app:app /data
USER app
ENV DATABASE_PATH=/data/birdbox.db
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
