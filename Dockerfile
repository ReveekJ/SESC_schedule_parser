FROM python:3.12-alpine3.20

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /usr/project
WORKDIR /usr/project

RUN apk add --no-cache --upgrade bash

COPY requirements.txt /usr/project
RUN pip install --no-cache --upgrade pip
RUN pip install --no-cache -r requirements.txt

COPY . .

CMD ["/bin/bash", "bot.sh"]
