FROM ubuntu:latest

RUN apt-get update -y && \
    apt-get install --no-install-recommends -y -q \
    python3 python3-dev python3-pip \
    python3-setuptools \
    libpq-dev \
    gettext \
    unzip wget cmake build-essential libffi-dev libssl-dev

RUN pip3 install wheel

ADD . /app

WORKDIR /app

COPY requirements.txt ./

RUN python3 /app/manage.py collectstatic --no-input

RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD exec gunicorn djangoproject.wsgi:application --bind 0.0.0.0:8000 --workers 3