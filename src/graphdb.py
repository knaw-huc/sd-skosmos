"""
This file contains functions for interacting with GraphDB
"""
import os

import requests

admin_password = os.environ.get("ADMIN_PASSWORD", '')
endpoint = os.environ.get("SPARQL_ENDPOINT", '')


def setup_graphdb():
    """
    Setup graphdb, if it isn't set up yet.
    :return:
    """
    # Check if db exists
    resp = requests.get(f"{endpoint}/size")
    if resp.status_code != 200:
        # GraphDB repository not created yet -- create it
        headers = {
            'Content-Type': 'text/turtle',
        }
        requests.put(
            f"{endpoint}",
            headers=headers,
            data=open(f"/var/www/skosmos-repository.ttl", "rb"),
            auth=('admin', admin_password),
        )
        print(f"CREATED GRAPHDB[{endpoint}] DB[skosmos.tdb]")
    else:
        print(f"EXISTS GRAPHDB [{endpoint}]]")


def get_loaded_vocabs():
    """
    Get all loaded vocabularies from GraphDB
    :return:
    """
    graphs_response = requests.get(f"{endpoint}/rdf-graphs",
                                   headers={"Accept": "application/json"})
    tmp = []
    if graphs_response.status_code == 200:
        body = graphs_response.json()
        tmp = []
        for binding in body["results"]["bindings"]:
            tmp.append(binding["contextID"]["value"])
        print("Loaded vocabs:")
        print(tmp)
    return tmp


def get_type(extension):
    if extension in ["ttl", "turtle"]:
        return "text/turtle"
    if extension in ["trig"]:
        return "application/x-trig"
    # Default
    return "text/turtle"


def add_vocabulary(graph, graph_name, extension):
    """
    Add a vocabulary to GraphDB
    :param graph:       File
    :param graph_name:  String representing the name of the graph
    :param extension:    String representing the extension
    :return:
    """
    print(f"Adding vocabulary {graph_name}")
    headers = {
        'Content-Type': get_type(extension),
    }
    response = requests.put(
        f"{endpoint}/statements",
        data=graph.read(),
        headers=headers,
        auth=('admin', admin_password),
        params={'context': f"<{graph_name}>"},
    )
    print(f"RESPONSE: {response.status_code}")
    if response.status_code != 200:
        print(response.content)
