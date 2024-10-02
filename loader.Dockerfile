FROM python:3.10

RUN apt-get update && apt-get -y install cron gettext

WORKDIR /app

COPY crontab /app/crontab
COPY entrypoint_cron.sh /app/
COPY config-docker-compose.ttl /app/
COPY skosmos-repository.ttl /app/
COPY crontask.sh /app/

COPY src /app/src
COPY entrypoint.py /app/entrypoint.py

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

ENTRYPOINT ["/app/entrypoint_cron.sh"]
