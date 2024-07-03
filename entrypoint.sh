#!/usr/bin/env bash
set -x

/var/www/entrypoint.py

/usr/bin/envsubst < /tmp/config-docker-compose.ttl > /var/www/html/config.ttl
cat /var/www/html/config.ttl

/usr/sbin/apache2ctl -D FOREGROUND
