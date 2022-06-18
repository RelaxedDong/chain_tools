# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

WORKDIR /workspace
RUN apt-get update &&  apt-get -y install gcc

COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip && pip3 install -r requirements.txt
COPY . .
CMD [ "sanic", "main:app" , "--host=0.0.0.0", "--port=8000"]
