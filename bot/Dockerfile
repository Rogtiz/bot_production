FROM python:3.11

WORKDIR /bot

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./bot ./bot

# В конце Dockerfile
COPY images/ images/

CMD ["python", "bot/main.py"]
