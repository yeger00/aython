FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 4000

CMD ["python", "-u", "app/main.py"]
