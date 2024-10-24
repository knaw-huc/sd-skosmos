#!/usr/bin/env bash
set -x

ls -al $DATA

ln -s /config/config.ttl /var/www/html/config.ttl
cat /var/www/html/config.ttl

/usr/sbin/apache2ctl -D FOREGROUND
