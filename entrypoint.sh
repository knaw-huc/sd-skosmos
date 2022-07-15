#!/usr/bin/env bash
set -x

sleep 30

cp /var/www/html/config-docker-compose.ttl /tmp/config-docker-compose.ttl

LOADED=`ls /data/loaded/* | wc -l`
if [ $LOADED -eq 0 ];then
    curl -u admin:admin -XPOST --data "dbName=skosmos&dbType=tdb" -G http://fuseki:3030/$/datasets
fi

PWD=`pwd`
cd /data/load
for VOCAB in `ls *.ttl`; do
    echo "LOAD VOCAB[$VOCAB] ..."
    GRAPH=`grep sparqlGraph $VOCAB.config | sed 's|    skosmos:sparqlGraph <||g' | sed 's|>$||g'`
    echo "... in GRAPH[$GRAPH] ..."
    curl -X PUT -H Content-Type:text/turtle -T $VOCAB -G http://fuseki:3030/skosmos/data --data-urlencode graph=$GRAPH
    mv $VOCAB $VOCAB.config ../loaded
    echo "... DONE"
done
cat /data/loaded/*.ttl.config >>  /tmp/config-docker-compose.ttl
cd $PWD

/usr/bin/envsubst < /tmp/config-docker-compose.ttl > /var/www/html/config.ttl
cat /var/www/html/config.ttl

/usr/sbin/apache2ctl -D FOREGROUND