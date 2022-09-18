#!/usr/bin/env bash
set -x

sleep 30

if [ -f /data/config.ttl ];then
    cp /data/config.ttl /tmp/config-docker-compose.ttl   
else 
    cp /var/www/html/config-docker-compose.ttl /tmp/config-docker-compose.ttl
fi

LOADED=`ls /data/*.loaded | wc -l`
if [ ${LOADED} -eq 0 ];then
    curl -u admin:admin -XPOST --data "dbName=skosmos&dbType=tdb" -G ${FUSEKI}/\$/datasets
fi

PWD=`pwd`
cd /data
for VOCAB in `ls *.ttl`; do
    VOCAB=`basename ${VOCAB} .ttl`
    if [ ! -f ${VOCAB}.loaded ]; then
        echo "LOAD VOCAB[${VOCAB}] ..."
        GRAPH=`grep sparqlGraph ${VOCAB}.config | sed 's|\s*skosmos:sparqlGraph <\s*||g' | sed 's|\s*>\s*||g'`
        echo "... in GRAPH[${GRAPH}] ..."
        if [ ! -f ${VOCAB}.ttl ]; then
            echo "!ERROR: /data/${VOCAB}.ttl doesn't exist!"
            exit 1
        fi
        curl -X PUT -H Content-Type:text/turtle -T ${VOCAB}.ttl -G ${FUSEKI}/skosmos/data --data-urlencode graph=${GRAPH}
        touch /data/${VOCAB}.loaded
        echo "... DONE"
    fi
done
cat /data/*.config >> /tmp/config-docker-compose.ttl
cd ${PWD}

/usr/bin/envsubst < /tmp/config-docker-compose.ttl > /var/www/html/config.ttl
cat /var/www/html/config.ttl

/usr/sbin/apache2ctl -D FOREGROUND