FROM python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /usr/project
WORKDIR /usr/project

#RUN export PYTHONPATH=$PYTHONPATH:pwd
COPY requirements.txt /usr/project
RUN pip install --upgrade pip
RUN pip install --no-cache -r requirements.txt

COPY . .

#RUN cd src && uvicorn services:app --reload && cd .. &

CMD ["/bin/bash", "bot.sh"]
