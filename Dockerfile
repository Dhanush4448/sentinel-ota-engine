FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# This makes it run the whole pipeline automatically
CMD ["python", "test_sentinel.py"]