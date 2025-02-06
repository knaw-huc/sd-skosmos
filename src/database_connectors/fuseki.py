"""
This file contains functions for interacting with Fuseki
"""
from typing import TextIO

import requests

from src.database import DatabaseConnector


class Fuseki(DatabaseConnector):
    """
    Fuseki database connector
    """

    fuseki_base: str

    def __init__(self, fuseki_base, username, password):
        """
        Create a new Fuseki DatabaseConnector
        :param fuseki_base:
        :param username:
        :param password:
        """
        self.fuseki_base = fuseki_base
        super().__init__(f"{fuseki_base}/sparql",
                         f"{fuseki_base}/update",
                         f"{fuseki_base}/data",
                         username,
                         password)


    def setup(self) -> None:
        """
        Setup fuseki, if it isn't set up yet.
        :return:
        """
        # Check if db exists
        if not self.check_repository_exists():
            # Fuseki repository not created yet -- create it
            base_endpoint = '/'.join(self.fuseki_base.split('/')[:-1])
            requests.post(
                f"{base_endpoint}/$/datasets",
                auth=(self.admin_username, self.admin_password),
                params={'dbName': 'skosmos', 'dbType': 'tdb'},
                timeout=60
            )
            print(f"CREATED FUSEKI[{self.fuseki_base}] DB[skosmos.tdb]")
        else:
            print(f"EXISTS FUSEKI [{self.fuseki_base}]]")


    def add_vocabulary(self, graph: TextIO, graph_name: str, extension: str,
                       append: bool = False) -> None:
        """
        Add a vocabulary to Fuseki
        :param graph:       File
        :param graph_name:  String representing the name of the graph
        :param extension:   String representing the extension
        :param append:      Append data instead of replacing
        :return:
        """
        print(f"[Fuseki] Adding vocabulary {graph_name}")
        try:
            content = graph.read().encode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            content = graph.read()

        response = self.sparql_http_update(content, extension,{'graph': f"{graph_name}"},
                                           append)

        print(f"RESPONSE: {response.status_code}")
        if response.status_code >= 400:
            print()
            print(response.content)
