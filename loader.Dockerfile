FROM python:3.10

RUN apt-get update && apt-get -y install cron gettext \
                   && apt-get install -y default-jdk

WORKDIR /app

COPY crontab /app/crontab
COPY entrypoint_cron.sh /app/
COPY config-docker-compose.ttl /app/
COPY config-docker-compose.ttl /config/
COPY skosmos-repository.ttl /app/
COPY crontask.sh /app/

COPY src /app/src
COPY entrypoint.py /app/entrypoint.py

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
RUN wget -O /app/src/skos-play-cli-0.9.1-onejar.jar "https://github.com/sparna-git/skos-play/releases/download/0.9.1/skos-play-cli-0.9.1-onejar.jar"
 

ENTRYPOINT ["/app/entrypoint_cron.sh"]
