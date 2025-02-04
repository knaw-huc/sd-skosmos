"""
This file contains functions for interacting with Fuseki
"""
from typing import TextIO

import requests

from src.database import DatabaseConnector
from src.vocabularies import get_type


class Fuseki(DatabaseConnector):
    """
    GraphDB database connector
    """

    def setup(self) -> None:
        """
        Setup fuseki, if it isn't set up yet.
        :return:
        """
        # Check if db exists
        resp = requests.get(f"{self.endpoint}/size", timeout=60)
        if resp.status_code != 200:
            # GraphDB repository not created yet -- create it
            headers = {
                'Content-Type': 'text/turtle',
            }
            requests.post(
                f"{self.endpoint}/$/datasets",
                headers=headers,
                auth=(self.admin_username, self.admin_password),
                params={'dbName': 'skosmos', 'dbType': 'tdb'},
                timeout=60
            )
            print(f"CREATED FUSEKI[{self.endpoint}] DB[skosmos.tdb]")
        else:
            print(f"EXISTS FUSEKI [{self.endpoint}]]")


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
        content = graph.read()
        try:
            content = content.encode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            pass

        headers = {
            'Content-Type': get_type(extension),
        }
        method = requests.post if append else requests.put

        response = method(
            f"{self.endpoint}/statements",
            data=content,
            headers=headers,
            auth=(self.admin_username, self.admin_password),
            params={'graph': f"{graph_name}"},
            timeout=60,
        )
        print(f"RESPONSE: {response.status_code}")
        if response.status_code != 200:
            print(response.content)
            print(f"used format: {get_type(extension)}, extension {extension}")
