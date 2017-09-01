FROM amsterdam/docker_python:latest
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1
ENV CONSUL_HOST=${CONSUL_HOST:-notset}
ENV CONSUL_PORT=${CONSUL_PORT:-8500}
ENV DATAPUNT_API_URL=${DATAPUNT_API_URL:-https://api.data.amsterdam.nl/}
ARG CULTUUR_OBJECTSTORE_PASSWORD
ENV CULTUUR_OBJECTSTORE_PASSWORD=$CULTUUR_OBJECTSTORE_PASSWORD
ENV JWT_SHARED_SECRET_KEY=${JWT_SHARED_SECRET_KEY}

EXPOSE 8000

RUN apt-get install -y \
		gdal-bin \
		libgeos-dev \
		netcat \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
	&& adduser --system datapunt

WORKDIR /app


# CI hook - see .jenkins/README.TXT
COPY .jenkins/import /.jenkins-import/
COPY .jenkins/docker-migrate.sh /app/

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/

USER datapunt

RUN export DJANGO_SETTINGS_MODULE=monumenten.settings

CMD uwsgi

