"""
This file contains functions for dealing with vocabularies and their configuration.
"""

import re
import urllib.request
import yaml

from src.exceptions import InvalidConfigurationException, UnknownAuthenticationTypeException
from src.graphdb import add_vocabulary


def get_file_from_config(config_data, data_dir):
    """
    Get the config file from yaml data.
    :param config_data: The configuration, a dict with information about the file.
    :param data_dir:    The data directory of the application
    :return:
    """
    if config_data['type'] == 'file':
        return open(f"{data_dir}/{config_data['location']}", encoding='utf-8')
    if config_data['type'] == 'fetch':
        req = urllib.request.Request(config_data['location'])
        if 'headers' in config_data:
            for header, val in config_data['headers'].items():
                req.add_header(header, val)

        if 'auth' in config_data:
            auth_data = config_data['auth']
            if auth_data['type'] == 'github':
                req.add_header('Authorization', f'token {auth_data["token"]}')
            else:
                raise UnknownAuthenticationTypeException()

        return urllib.request.urlopen(req)
    raise InvalidConfigurationException("Type must be file")


def load_vocabulary(source_data, data_dir, graph_name):
    """
    Load a vocabulary using the source data from the yaml.
    :param source_data:
    :param data_dir:
    :param graph_name:
    :return:
    """
    with get_file_from_config(source_data, data_dir) as vocab_file:
        # g = ConjunctiveGraph()
        # g.parse(vocab_file, format=get_vocab_format(source_data))
        # c = list(g.contexts())[0]
        add_vocabulary(vocab_file, graph_name, get_vocab_format(source_data))


def get_graph(fp):
    """
    Get the sparql graph from the given vocab
    :param fp:  The vocabulary config, a file pointer
    :return:
    """
    for line in fp:
        # If line is a bytes-like object, we need to decode it
        try:
            line = line.decode()
        except (UnicodeDecodeError, AttributeError):
            # Already decoded
            pass
        if re.search("sparqlGraph", line):
            return line.strip().split(" ")[1].strip("<>")
    return ""


def load_vocab_yaml(file_location):
    """
    Open a yaml config file and return a dict with its contents
    :param file_location:
    :return:
    """
    with open(file_location, 'r', encoding='utf-8') as fp:
        return yaml.safe_load(fp)


def get_vocab_format(source_data):
    """
    Return the vocab format of the given data source. It is either based on the file extension,
    or on an override in the yaml file.
    :param source_data:
    :return:
    """
    if 'format' in source_data:
        return source_data['format']
    return source_data['location'].split('.')[-1]
