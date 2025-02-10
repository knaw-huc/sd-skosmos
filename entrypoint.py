#!/usr/local/bin/python3

"""
The python entrypoint initializes the Skosmos dataset before starting the application.
"""

import glob
import importlib
import os
import shutil
import time
from pathlib import Path
from typing import IO

from src.database import DatabaseConnector
from src.exceptions import InvalidConfigurationException
from src.vocabularies import get_file_from_config, get_graph, load_vocab_yaml, get_vocab_format


def construct_database(db_type: str = "graphdb") -> DatabaseConnector:
    """
    Create an instance of a DatabaseConnector
    :return: 
    """
    module_name = f"src.database_connectors.{db_type}"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        raise InvalidConfigurationException(f"Database type '{db_type}' not known/supported")
    if not hasattr(module, "create_connector"):
        raise InvalidConfigurationException(f"'{db_type}' misses 'create_connector' function")
    connector =  module.create_connector()
    if not isinstance(connector, DatabaseConnector):
        raise InvalidConfigurationException(f"'{db_type}' doesn't extend DatabaseConnector")
    return connector


def append_file(source: IO, dest: str):
    """
    Append source to dest file.
    :param source:  A file pointer to a source file.
    :param dest:    The path of the destination file.
    :return:
    """
    with open(dest, "a+", encoding='utf-8') as df:
        for line in source:
            try:
                line = line.decode()
            except (UnicodeDecodeError, AttributeError):
                pass
            df.write(line)


def load_vocabulary(database: DatabaseConnector, source_data: dict, data_dir: str,
                    graph_name: str, append: bool = False) -> None:
    """
    Load a vocabulary using the source data from the yaml.
    :param database: The database connector for connecting to the vocabulary storage.
    :param source_data: Dict containing the information where to find the vocab.
    :param data_dir: Dir containing local files.
    :param graph_name: The name of the graph to put the vocabulary into.
    :param append: Boolean, when true this doesn't overwrite the graph but appends.
    :return:
    """
    with get_file_from_config(source_data, data_dir) as vocab_file:
        database.add_vocabulary(vocab_file, graph_name, get_vocab_format(source_data), append)


def main() -> None:
    """
    Main function.
    :return:
    """
    data = os.environ["DATA"]
    database_type = os.environ.get("DATABASE_TYPE", "graphdb")

    if os.path.isfile(f'{data}/config.ttl'):
        shutil.copy(f'{data}/config.ttl', '/config/config-docker-compose.ttl')
    else:
        shutil.copy('/app/config-docker-compose.ttl', '/config/config-docker-compose.ttl')

    if os.path.isfile(f'{data}/config-ext.ttl'):
        with open(f'{data}/config-ext.ttl', 'r', encoding='utf-8') as f:
            append_file(f, '/config/config-docker-compose.ttl')

    database = construct_database(database_type)

    database.setup()

    loaded_vocabs = database.get_loaded_vocabs()

    vocabs = glob.glob(f'{data}/*.yaml')

    for vocab in vocabs:
        path = Path(vocab)

        vocab_config = load_vocab_yaml(path)

        try:
            with get_file_from_config(vocab_config['config'], data) as config:
                graph = get_graph(config)
                print(f"Graph: {graph}")

            reload = False
            if graph not in loaded_vocabs:
                reload = True
            elif vocab_config['config'].get('refresh', False):
                interval = vocab_config['config'].get('refreshInterval', 0)
                diff = (time.time() - loaded_vocabs[graph]) / 3600
                reload = diff > interval

            if reload:
                print(f"Loading vocabulary {vocab}")
                load_vocabulary(database, vocab_config['source'], data, graph)
                if "tweaks" in vocab_config:
                    print(f"Tweaks found for {vocab}. Loading")
                    load_vocabulary(database, vocab_config['tweaks'], data, graph, True)
                if graph in loaded_vocabs:
                    database.update_timestamp(graph, int(time.time()))
                else:
                    database.set_timestamp(graph, int(time.time()))
                print("... DONE")

            # Doing this last makes sure the vocab isn't added to the config when there's a problem
            with get_file_from_config(vocab_config['config'], data) as config:
                append_file(config, "/config/config-docker-compose.ttl")
        except InvalidConfigurationException as e:
            print(f"Invalid configuration: {e}")
            print(f"Skipping vocab '{vocab}'")
            continue


if __name__ == "__main__":
    time.sleep(10)
    main()
