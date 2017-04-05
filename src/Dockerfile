FROM amsterdam/docker_python:latest
MAINTAINER datapunt.ois@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN apt-get update \
	&& apt-get install -y \
		gdal-bin \
		libgeos-dev \
		netcat \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
	&& adduser --system datapunt

WORKDIR /app

COPY . /app/

# CI hook - see .jenkins/README.TXT
COPY .jenkins/import /.jenkins-import/
COPY .jenkins/docker-migrate.sh /app/

RUN pip install --no-cache-dir -r requirements.txt
USER datapunt

RUN export DJANGO_SETTINGS_MODULE=monumenten.settings

CMD uwsgi

