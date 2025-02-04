"""
Database connector for interacting with triple stores.
"""
from abc import abstractmethod, ABC
from typing import TextIO

import requests
from SPARQLWrapper import SPARQLWrapper, JSON, POST, BASIC

from src.vocabularies import get_type


class DatabaseConnector(ABC):
    """
    Abstract Base Class for handling database connections
    """

    admin_password: str
    admin_username: str
    endpoint: str


    def __init__(self, endpoint, username, password):
        """
        Create a new DatabaseConnector. These three arguments are the same for all triple stores,
        as they are needed for interacting with SPARQL. Specific implementations can add more.
        :param endpoint:
        :param username:
        :param password:
        """
        self.admin_password = password
        self.admin_username = username
        self.endpoint = endpoint


    @abstractmethod
    def setup(self) -> None:
        """
        Initialize the database.
        :return:
        """


    @abstractmethod
    def add_vocabulary(self, graph: TextIO, graph_name: str, extension: str,
                       append: bool = False) -> None:
        """
        Add a vocabulary to the database
        :param graph:       File
        :param graph_name:  String representing the name of the graph
        :param extension:   String representing the extension
        :param append:      Append data instead of replacing
        :return:
        """


    def get_loaded_vocabs(self) -> dict[str, int]:
        """
        Get all loaded vocabularies from the triple store
        :return:
        """
        sparql = SPARQLWrapper(self.endpoint)
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


    def set_timestamp(self, graph_name: str, timestamp: int) -> None:
        """
        Set a timestamp for a new graph.
        :param graph_name:
        :param timestamp:
        :return:
        """
        sparql = SPARQLWrapper(f"{self.endpoint}/statements")
        sparql.setHTTPAuth(BASIC)
        sparql.setCredentials(self.admin_username, self.admin_password)
        sparql.setMethod(POST)
        q = """INSERT DATA {{
            <{graph}> <http://purl.org/dc/terms/modified> {timestamp} .
        }}"""
        q_formatted = q.format(graph=graph_name, timestamp=timestamp)
        print(q_formatted)
        sparql.setQuery(q_formatted)
        sparql.query()


    def update_timestamp(self, graph_name: str, timestamp: int) -> None:
        """
        Set a timestamp for an existing graph.
        :param graph_name:
        :param timestamp:
        :return:
        """
        sparql = SPARQLWrapper(f"{self.endpoint}/statements")
        sparql.setHTTPAuth(BASIC)
        sparql.setCredentials(self.admin_username, self.admin_password)
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


    def sparql_http_update(self, content, extension, params, append: bool = False):
        """
        Perform an update to the SPARQL-HTTP endpoint for adding a vocabulary
        :param append:
        :param extension:
        :param content:
        :param params:
        :return:
        """
        headers = {
            'Content-Type': get_type(extension)
        }

        method = requests.post if append else requests.put

        return method(
            f"{self.endpoint}/statements",
            data=content,
            headers=headers,
            auth=(self.admin_username, self.admin_password),
            params=params,
            timeout=60,
        )
