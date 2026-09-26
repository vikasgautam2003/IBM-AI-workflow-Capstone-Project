FROM python:3.14-slim

WORKDIR /app
ADD . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# The Flask app listens on port 8080
EXPOSE 8080

CMD ["python", "app.py"]
