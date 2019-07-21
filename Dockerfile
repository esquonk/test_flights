FROM ubuntu:latest

RUN apt update
RUN apt install python3.7

ADD . /app

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD exec gunicorn your_site_name.wsgi:application --bind 0.0.0.0:8000 --workers 3