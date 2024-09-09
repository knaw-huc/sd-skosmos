#!/usr/bin/env bash
set -x

/var/www/entrypoint.py

/usr/bin/envsubst < /config/config-docker-compose.ttl > /config/config.ttl
