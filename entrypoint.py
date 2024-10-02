#!/usr/bin/env python3

"""
The python entrypoint initializes the Skosmos dataset before starting the application.
"""

import glob
import os
import shutil
import time
from pathlib import Path
from typing import IO

from src.exceptions import InvalidConfigurationException
from src.graphdb import get_loaded_vocabs, set_timestamp, setup_graphdb, update_timestamp
from src.vocabularies import get_file_from_config, get_graph, load_vocab_yaml, load_vocabulary


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


def main() -> None:
    """
    Main function.
    :return:
    """
    data = os.environ["DATA"]

    if os.path.isfile(f'{data}/config.ttl'):
        shutil.copy(f'{data}/config.ttl', '/config/config-docker-compose.ttl')
    else:
        shutil.copy('/app/config-docker-compose.ttl', '/config/config-docker-compose.ttl')

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

            reload = False
            if graph not in loaded_vocabs:
                reload = True
            elif vocab_config['config'].get('refresh', False):
                interval = vocab_config['config'].get('refreshInterval', 0)
                diff = (time.time() - loaded_vocabs[graph]) / 3600
                reload = diff > interval

            if reload:
                print(f"Loading vocabulary {vocab}")
                load_vocabulary(vocab_config['source'], data, graph)
                if graph in loaded_vocabs:
                    update_timestamp(graph, int(time.time()))
                else:
                    set_timestamp(graph, int(time.time()))
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
