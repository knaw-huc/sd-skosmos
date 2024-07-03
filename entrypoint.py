#!/usr/bin/env python3

import time
import os
import shutil
import glob
import re
import requests
from pathlib import Path


def get_graph(data_dir, vocab_name):
    """
    Get the sparql graph from the given vocab
    :param data_dir: The location of the 'data' directory
    :param vocab_name:  The vocabulary, a config and ttl should be present
    :return:
    """
    file = open(f"{data_dir}/{vocab_name}.config", 'r')
    for line in file:
        if re.search("sparqlGraph", line):
            return line.strip().split(" ")[1].strip("<>")


def append_file(source, dest):
    """
    Append source to dest file.
    :param source:
    :param dest:
    :return:
    """
    with open(source, "r") as sf:
        with open(dest, "a+") as df:
            df.write(sf.read())


if __name__ == "__main__":
    time.sleep(30)

    data = os.environ["DATA"]

    if os.path.isfile(f'{data}/config.ttl'):
        shutil.copy(f'{data}/config.ttl', '/tmp/config-docker-compose.ttl')
    else:
        shutil.copy('/var/www/html/config-docker-compose.ttl', '/tmp/config-docker-compose.ttl')

    if os.path.isfile(f'{data}/config-ext.ttl'):
        append_file(f'{data}/config-ext.ttl', '/tmp/config-docker-compose.ttl')

    admin_password = os.environ.get("ADMIN_PASSWORD", '')
    fuseki_base_url = os.environ["FUSEKI"]

    loaded = glob.glob(f'{data}/*.loaded')

    if len(loaded) == 0:
        # Create Fuseki
        requests.post(
            f"{fuseki_base_url}/$/datasets",
            auth=('admin', admin_password),
            params={'dbName': 'skosmos', 'dbType': 'tdb'},
        )
        print(f"CREATED FUSEKI[{fuseki_base_url}] DB[skosmos.tdb]")
        pass
    else:
        print(f"EXISTS FUSEKI [{fuseki_base_url}]]")

    vocabs = glob.glob(f'{data}/*.ttl')

    for vocab in vocabs:
        path = Path(vocab)
        basename = path.stem
        if not os.path.isfile(f'{data}/{basename}.loaded'):
            print(f"LOAD VOCAB[{basename}] ...")
            graph = get_graph(data, basename)
            print(f"... in GRAPH[{graph}] ...")
            if not os.path.isfile(f'{data}/{basename}.ttl'):
                print(f"!ERROR {data}/{basename}.ttl doesn't exist!")
                exit(1)

            headers = {
                'Content-Type': 'text/turtle',
            }
            requests.put(
                f"{fuseki_base_url}/skosmos/data",
                data=open(f'{data}/{basename}.ttl'),
                headers=headers,
                auth=('admin', admin_password),
                params={'graph': graph},
            )
            open(f'{data}/{basename}.loaded', 'a').close()
            print("... DONE")

    configs = glob.glob(f'{data}/*.config')
    for config in configs:
        append_file(config, "/tmp/config-docker-compose.ttl")

