FROM amsterdam/docker_python:latest
MAINTAINER datapunt.ois@amsterdam.nl

ENV PYTHONUNBUFFERED 1
ENV CONSUL_HOST=${CONSUL_HOST:-notset}
ENV CONSUL_PORT=${CONSUL_PORT:-8500}
ENV DATAPUNT_API_URL=${DATAPUNT_API_URL:-https://api.datapunt.amsterdam.nl/}
ARG OBJECTSTORE_PASSWORD
ENV OBJECTSTORE_PASSWORD=$OBJECTSTORE_PASSWORD

EXPOSE 8000

RUN apt-get update \
	&& apt-get install -y \
		gdal-bin \
		libgeos-dev \
		netcat \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
	&& adduser --system datapunt \
	&& mkdir -p /static \
	&& chown datapunt /static \
	&& pip install uwsgi

WORKDIR /app

COPY . /app/

# see .jenkins/README.TXT
COPY .jenkins-import /.jenkins-import/

RUN pip install --no-cache-dir -r requirements.txt
USER datapunt

RUN export DJANGO_SETTINGS_MODULE=monumenten.settings

CMD ["/app/docker-run.sh"]

