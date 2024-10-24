"""
This file contains functions for dealing with vocabularies and their configuration.
"""
import json
import re
import urllib.request
import urllib.parse
from pathlib import Path
from typing import IO, TextIO

import yaml

from src.exceptions import InvalidConfigurationException, UnknownAuthenticationTypeException
from src.graphdb import add_vocabulary


def set_auth_data(
        auth_data: dict,
        config_data: dict,
        req: urllib.request.Request) -> urllib.request.Request:
    """
    Set authentication data on the request.
    :param auth_data:
    :param config_data:
    :param req:
    :return:
    """
    if auth_data['type'] == 'github':
        req.add_header('Authorization', f'token {auth_data["token"]}')
    elif auth_data['type'] == 'gitlab':
        try:
            raw_url = config_data['location']
            url = urllib.parse.urlparse(raw_url)
            [repo, full_path] = map(
                lambda x: urllib.parse.quote_plus(x.strip('/')),
                url.path.split('/-/blob/')
            )
            [branch, path] = full_path.split('%2F', 1)
            api_url = (f"https://{url.netloc}/api/v4/projects/{repo}"
                       + f"/repository/files/{path}/raw?ref={branch}")
            req = urllib.request.Request(api_url)
            req.add_header('PRIVATE-TOKEN', auth_data["token"])
        except ValueError as e:
            raise InvalidConfigurationException("GitLab URI format invalid") from e
    else:
        raise UnknownAuthenticationTypeException()
    return req


def get_file_from_config(config_data: dict, data_dir: str) -> TextIO:
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
            req = set_auth_data(auth_data, config_data, req)

        return urllib.request.urlopen(req)
    if config_data['type'] == 'post':
        endpoint = config_data['location']
        body = config_data['body']
        req = urllib.request.Request(endpoint, method='POST', data=json.dumps(body).encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        if 'headers' in config_data:
            for header, val in config_data['headers'].items():
                req.add_header(header, val)
        return urllib.request.urlopen(req)

    if config_data['type'] == 'sparql':
        with open(f"{data_dir}/{config_data['query_location']}", encoding='utf-8') as file:
            sparql_query = file.read()
        endpoint = config_data['location']
        data_dict = {'query': sparql_query}
        req = urllib.request.Request(endpoint, method='POST', data=urllib.parse.urlencode(data_dict).encode())
        req.add_header('Accept', 'text/turtle')
        if 'headers' in config_data:
            for header, val in config_data['headers'].items():
                req.add_header(header, val)

        return urllib.request.urlopen(req)

    raise InvalidConfigurationException("Type must be file")


def load_vocabulary(source_data: dict, data_dir: str, graph_name: str) -> None:
    """
    Load a vocabulary using the source data from the yaml.
    :param source_data:
    :param data_dir:
    :param graph_name:
    :return:
    """
    with get_file_from_config(source_data, data_dir) as vocab_file:
        add_vocabulary(vocab_file, graph_name, get_vocab_format(source_data))


def get_graph(fp: IO) -> str:
    """
    Get the sparql graph from the given vocab
    :param fp:  The vocabulary config, a file pointer
    :return:
    """
    for line in fp:
        try:
            line = line.decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            # Already decoded
            pass
        if re.search("sparqlGraph", line):
            return line.strip().split(" ")[1].strip("<>")
    return ""


def load_vocab_yaml(file_location: Path) -> dict:
    """
    Open a yaml config file and return a dict with its contents
    :param file_location:
    :return:
    """
    with open(file_location, 'r', encoding='utf-8') as fp:
        return yaml.safe_load(fp)


def get_vocab_format(source_data: dict) -> str:
    """
    Return the vocab format of the given data source. It is either based on the file extension,
    or on an override in the yaml file.
    :param source_data:
    :return:
    """
    if 'format' in source_data:
        return source_data['format']
    return source_data['location'].split('?')[0].split('.')[-1]
