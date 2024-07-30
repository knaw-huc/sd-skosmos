#!/usr/bin/env python3

"""
The python entrypoint initializes the Skosmos dataset before starting the application.
"""

import glob
import os
import shutil
import time
from pathlib import Path

from src.exceptions import InvalidConfigurationException
from src.graphdb import get_loaded_vocabs, setup_graphdb
from src.vocabularies import get_file_from_config, get_graph, load_vocab_yaml, load_vocabulary


def append_file(source, dest):
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


if __name__ == "__main__":
    time.sleep(10)

    data = os.environ["DATA"]

    if os.path.isfile(f'{data}/config.ttl'):
        shutil.copy(f'{data}/config.ttl', '/config/config-docker-compose.ttl')
    else:
        shutil.copy('/var/www/html/config-docker-compose.ttl', '/config/config-docker-compose.ttl')

    if os.path.isfile(f'{data}/config-ext.ttl'):
        with open(f'{data}/config-ext.ttl', 'r', encoding='utf-8') as f:
            append_file(f, '/config/config-docker-compose.ttl')

    setup_graphdb()

    loaded_vocabs = get_loaded_vocabs()

    vocabs = glob.glob(f'{data}/*.yaml')

    for vocab in vocabs:
        path = Path(vocab)

        vocab_config = load_vocab_yaml(path)

        try:
            with get_file_from_config(vocab_config['config'], data) as config:
                graph = get_graph(config)
                print(f"Graph: {graph}")

            always_load = vocab_config['config'].get('alwaysRefresh', False)

            if always_load or graph not in loaded_vocabs:
                print(f"Loading vocabulary {vocab}")
                load_vocabulary(vocab_config['source'], data, graph)
                print("... DONE")

            # Doing this last makes sure the vocab isn't added to the config when there's a problem
            with get_file_from_config(vocab_config['config'], data) as config:
                append_file(config, "/config/config-docker-compose.ttl")
        except InvalidConfigurationException as e:
            print(f"Invalid configuration: {e}")
            print(f"Skipping vocab '{vocab}'")
            continue
