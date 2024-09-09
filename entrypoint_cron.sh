#!/usr/bin/env bash

/usr/bin/envsubst < /var/www/crontab > /etc/cron.d/crontab

crontab /etc/cron.d/crontab
touch /var/log/cron.log

cron && tail -f /var/log/cron.log
