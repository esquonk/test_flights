FROM ubuntu:latest

WORKDIR /app

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apt-get update -y && \
    apt-get install --no-install-recommends -y -q \
    python3 python3-dev python3-pip \
    python3-setuptools \
    libpq-dev \
    gettext \
    unzip wget cmake build-essential libffi-dev libssl-dev

RUN pip3 install --upgrade pip
RUN pip3 install pipenv

COPY src /app
COPY data /app-data

COPY Pipfile ./

RUN pipenv install --skip-lock --system --dev

RUN python3 /app/manage.py collectstatic --no-input

EXPOSE 8000
