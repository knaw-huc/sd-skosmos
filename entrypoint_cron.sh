#!/usr/bin/env bash

/usr/bin/envsubst < /app/crontab > /etc/cron.d/crontab

/app/entrypoint.py

/usr/bin/envsubst < /config/config-docker-compose.ttl > /config/config.ttl

crontab /etc/cron.d/crontab
touch /var/log/cron.log

cron && tail -f /var/log/cron.log
