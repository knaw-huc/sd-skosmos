"""
This file contains functions for interacting with GraphDB
"""
import os
from typing import TextIO

import requests

from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST

admin_password = os.environ.get("ADMIN_PASSWORD", '')
endpoint = os.environ.get("SPARQL_ENDPOINT", '')


def setup_graphdb() -> None:
    """
    Setup graphdb, if it isn't set up yet.
    :return:
    """
    # Check if db exists
    resp = requests.get(f"{endpoint}/size", timeout=60)
    if resp.status_code != 200:
        # GraphDB repository not created yet -- create it
        headers = {
            'Content-Type': 'text/turtle',
        }
        with open("/var/www/skosmos-repository.ttl", "rb") as fp:
            requests.put(
                f"{endpoint}",
                headers=headers,
                data=fp,
                auth=('admin', admin_password),
                timeout=60
            )
        print(f"CREATED GRAPHDB[{endpoint}] DB[skosmos.tdb]")
    else:
        print(f"EXISTS GRAPHDB [{endpoint}]]")


def get_loaded_vocabs() -> dict[str, int]:
    """
    Get all loaded vocabularies from GraphDB
    :return:
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)
    q = """
        SELECT ?graph ?timestamp
        WHERE {
            ?graph <http://purl.org/dc/terms/modified> ?timestamp .
            FILTER NOT EXISTS {
                GRAPH ?g {?graph <http://purl.org/dc/terms/modified> ?timestamp .}
            }
        }
        ORDER BY ?timestamp
    """
    sparql.setQuery(q)
    result = sparql.queryAndConvert()
    result = result['results']['bindings']
    tmp = {}
    for line in result:
        tmp[line['graph']['value']] = int(line['timestamp']['value'])
    return tmp


def set_timestamp(graph_name: str, timestamp: int) -> None:
    """
    Set a timestamp for a new graph.
    :param graph_name:
    :param timestamp:
    :return:
    """
    sparql = SPARQLWrapper(f"{endpoint}/statements")
    sparql.setHTTPAuth(DIGEST)
    sparql.setCredentials("admin", admin_password)
    sparql.setMethod(POST)
    q = """INSERT DATA {{
        <{graph}> <http://purl.org/dc/terms/modified> {timestamp} .
    }}"""
    q_formatted = q.format(graph=graph_name, timestamp=timestamp)
    print(q_formatted)
    sparql.setQuery(q_formatted)
    sparql.query()


def update_timestamp(graph_name: str, timestamp: int) -> None:
    """
    Set a timestamp for an existing graph.
    :param graph_name:
    :param timestamp:
    :return:
    """
    sparql = SPARQLWrapper(f"{endpoint}/statements")
    sparql.setHTTPAuth(DIGEST)
    sparql.setCredentials("admin", admin_password)
    sparql.setMethod(POST)
    q = """
    DELETE {{
        <{graph}> <http://purl.org/dc/terms/modified> ?timestamp .
    }}
    INSERT {{
        <{graph}> <http://purl.org/dc/terms/modified> {timestamp} .
    }}
    WHERE {{
        <{graph}> <http://purl.org/dc/terms/modified> ?timestamp .
    }}
    """
    sparql.setQuery(q.format(graph=graph_name, timestamp=timestamp))
    sparql.query()


def get_type(extension: str) -> str:
    """
    Get the http mimetype based on the extension of a file.
    :param extension:
    :return:
    """
    if extension in ["ttl", "turtle"]:
        return "text/turtle"
    if extension in ["trig"]:
        return "application/x-trig"
    # Default
    return "text/turtle"


def add_vocabulary(graph: TextIO, graph_name: str, extension: str) -> None:
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
        timeout=60,
    )
    print(f"RESPONSE: {response.status_code}")
    if response.status_code != 200:
        print(response.content)
