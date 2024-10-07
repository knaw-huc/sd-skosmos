#!/usr/bin/env bash
set -x

/app/entrypoint.py

/usr/bin/envsubst < /config/config-docker-compose.ttl > /config/config.ttl
