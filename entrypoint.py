#!/usr/bin/env python3
import time
import os
import shutil
import glob
import re
import urllib.request
from pathlib import Path
from rdflib import ConjunctiveGraph

import yaml

from src.exceptions import InvalidConfigurationException, UnknownAuthenticationTypeException
from src.graphdb import add_vocabulary, get_loaded_vocabs, setup_graphdb


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


def append_file(source, dest):
    """
    Append source to dest file.
    :param source:  A file pointer to a source file.
    :param dest:    The path of the destination file.
    :return:
    """
    with open(dest, "a+") as df:
        for line in source:
            try:
                line = line.decode()
            except (UnicodeDecodeError, AttributeError):
                pass
            df.write(line)


def load_vocab_yaml(file_location):
    """
    Open a yaml config file and return a dict with its contents
    :param file_location:
    :return:
    """
    with open(file_location, 'r', encoding='utf-8') as fp:
        return yaml.safe_load(fp)


def get_file_from_config(config_data, data_dir):
    """
    Get the config file from yaml data.
    :param config_data: The configuration, a dict with information about the file.
    :param data_dir:    The data directory of the application
    :return:
    """
    if config_data['type'] == 'file':
        return open(f"{data_dir}/{config_data['location']}")
    elif config_data['type'] == 'fetch':
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
    else:
        raise InvalidConfigurationException("Type must be file")


def get_vocab_format(source_data):
    if 'format' in source_data:
        return source_data['format']
    return source_data['location'].split('.')[-1]


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


if __name__ == "__main__":
    time.sleep(10)

    data = os.environ["DATA"]

    if os.path.isfile(f'{data}/config.ttl'):
        shutil.copy(f'{data}/config.ttl', '/tmp/config-docker-compose.ttl')
    else:
        shutil.copy('/var/www/html/config-docker-compose.ttl', '/tmp/config-docker-compose.ttl')

    if os.path.isfile(f'{data}/config-ext.ttl'):
        with open(f'{data}/config-ext.ttl', 'r', encoding='utf-8') as f:
            append_file(f, '/tmp/config-docker-compose.ttl')

    setup_graphdb()

    loaded_vocabs = get_loaded_vocabs()

    vocabs = glob.glob(f'{data}/*.yaml')

    for vocab in vocabs:
        path = Path(vocab)

        vocab_config = load_vocab_yaml(path)

        with get_file_from_config(vocab_config['config'], data) as config:
            graph = get_graph(config)
            print(f"Graph: {graph}")
        with get_file_from_config(vocab_config['config'], data) as config:
            # Reset file pointer
            append_file(config, "/tmp/config-docker-compose.ttl")

        always_load = vocab_config['config'].get('alwaysRefresh', False)

        if always_load or graph not in loaded_vocabs:
            print(f"Loading vocabulary {vocab}")
            load_vocabulary(vocab_config['source'], data, graph)
            print("... DONE")
