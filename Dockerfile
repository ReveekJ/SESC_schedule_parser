FROM python:3.12-alpine3.20

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /usr/project
WORKDIR /usr/project

RUN apk add --no-cache --upgrade bash
#RUN apk add --no-cache build-base
#RUN apk add --no-cache python3-dev
#RUN apk add --no-cache libffi-dev
#RUN apk add --no-cache openssl-dev


COPY requirements.txt /usr/project
RUN pip install --no-cache --upgrade pip
RUN pip install --no-cache -r requirements.txt

COPY . .
RUN mkdir -p "proto"
RUN python -m grpc_tools.protoc --proto_path=Drawing/Drawing/Protos --pyi_out=./proto --python_out=./proto --grpc_python_out=./proto drawing.proto

CMD ["/bin/bash", "bot.sh"]
