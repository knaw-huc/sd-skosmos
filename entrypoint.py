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
    time.sleep(10)

    data = os.environ["DATA"]

    if os.path.isfile(f'{data}/config.ttl'):
        shutil.copy(f'{data}/config.ttl', '/tmp/config-docker-compose.ttl')
    else:
        shutil.copy('/var/www/html/config-docker-compose.ttl', '/tmp/config-docker-compose.ttl')

    if os.path.isfile(f'{data}/config-ext.ttl'):
        append_file(f'{data}/config-ext.ttl', '/tmp/config-docker-compose.ttl')

    admin_password = os.environ.get("ADMIN_PASSWORD", '')

    endpoint = os.environ.get("SPARQL_ENDPOINT", '')

    # Check if db exists
    resp = requests.get(f"{endpoint}/size")
    if resp.status_code != 200:
        # GraphDB repository not created yet -- create it
        headers = {
            'Content-Type': 'text/turtle',
        }
        response = requests.put(
            f"{endpoint}",
            headers=headers,
            data=open(f"/var/www/skosmos-repository.ttl", "rb"),
            auth=('admin', admin_password),
        )
        print(f"CREATED GRAPHDB[{endpoint}] DB[skosmos.tdb]")
    else:
        print(f"EXISTS GRAPHDB [{endpoint}]]")

    vocabs = glob.glob(f'{data}/*.ttl')

    graphs_response = requests.get(f"{endpoint}/rdf-graphs",
                                   headers={"Accept": "application/json"})
    loaded_vocabs = []
    if graphs_response.status_code == 200:
        body = graphs_response.json()
        loaded_vocabs = []
        for binding in body["results"]["bindings"]:
            loaded_vocabs.append(binding["contextID"]["value"])
        print("Loaded vocabs:")
        print(loaded_vocabs)

    for vocab in vocabs:
        path = Path(vocab)
        basename = path.stem
        graph = get_graph(data, basename)
        if graph not in loaded_vocabs:
            print(f"LOAD VOCAB[{basename}] ...")
            print(f"... in GRAPH[{graph}] ...")
            if not os.path.isfile(f'{data}/{basename}.ttl'):
                print(f"!ERROR {data}/{basename}.ttl doesn't exist!")
                exit(1)

            headers = {
                'Content-Type': 'text/turtle',
            }
            response = requests.put(
                f"{endpoint}/statements",
                data=open(f'{data}/{basename}.ttl'),
                headers=headers,
                auth=('admin', admin_password),
                params={'context': f"<{graph}>"},
            )
            print("... DONE")

    configs = glob.glob(f'{data}/*.config')
    for config in configs:
        append_file(config, "/tmp/config-docker-compose.ttl")
