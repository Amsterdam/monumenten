FROM amsterdam/python:3.9-buster
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1
ENV CONSUL_HOST=${CONSUL_HOST:-notset}
ENV CONSUL_PORT=${CONSUL_PORT:-8500}
ENV DATAPUNT_API_URL=${DATAPUNT_API_URL:-https://api.data.amsterdam.nl/}
ARG CULTUUR_OBJECTSTORE_PASSWORD
ENV CULTUUR_OBJECTSTORE_PASSWORD=$CULTUUR_OBJECTSTORE_PASSWORD

EXPOSE 8000

WORKDIR /app

# CI hook - see .jenkins/README.TXT
COPY .jenkins /.jenkins
COPY .jenkins/docker-migrate.sh /app/

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/

RUN mkdir -p /static && chown datapunt /static

USER datapunt

RUN export DJANGO_SETTINGS_MODULE=monumenten.settings

ENV SECRET_KEY=insecure
RUN ./manage.py collectstatic
ENV SECRET_KEY=
##
CMD uwsgi
