"""
This file contains functions for interacting with GraphDB
"""
from typing import TextIO

import requests

from src.database import DatabaseConnector


class GraphDB(DatabaseConnector):
    """
    GraphDB database connector
    """
    def __init__(self, endpoint, username, password):
        """
        Construct GraphDB DatabaseConnector
        :param endpoint:
        :param username:
        :param password:
        """
        super().__init__(endpoint,
                         f"{endpoint}/statements",
                         f"{endpoint}/statements",
                         username,
                         password)


    def setup(self) -> None:
        """
        Setup graphdb, if it isn't set up yet.
        :return:
        """
        if not self.check_repository_exists():
            # GraphDB repository not created yet -- create it
            headers = {
                'Content-Type': 'text/turtle',
            }
            with open("/app/skosmos-repository.ttl", "rb") as fp:
                requests.put(
                    f"{self.sparql_endpoint_read}",
                    headers=headers,
                    data=fp,
                    auth=(self.admin_username, self.admin_password),
                    timeout=60
                )
            print(f"CREATED GRAPHDB[{self.sparql_http_endpoint}] DB[skosmos.tdb]")
        else:
            print(f"EXISTS GRAPHDB [{self.sparql_http_endpoint}]]")


    def add_vocabulary(self, graph: TextIO, graph_name: str, extension: str,
                       append: bool = False) -> None:
        """
        Add a vocabulary to GraphDB
        :param graph:       File
        :param graph_name:  String representing the name of the graph
        :param extension:   String representing the extension
        :param append:      Append data instead of replacing
        :return:
        """
        print(f"[GraphDB] Adding vocabulary {graph_name}")
        content = graph.read()
        try:
            content = content.encode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            pass

        response = self.sparql_http_update(content, extension,{'context': f"<{graph_name}>"},
                                           append)

        print(f"RESPONSE: {response.status_code}")
        if response.status_code != 200:
            print(response.content)
