# -*- coding: utf-8 -*-
from os import listdir
import requests
import signal
import subprocess
import tempfile
from zipfile import ZipFile

def get_ttl(identifier,filename):
    # read xslx
    url = f"https://docs.google.com/spreadsheets/d/{identifier}/export?format=xlsx"
    response = requests.get(url)
    temp_dir = tempfile.mkdtemp()
    file_path = f'{temp_dir}/temp.xlsx'
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
            print('File downloaded successfully')
    else:
        print(f'Failed to download file: {identifier}')
        return None
    # write zip-file
    uitvoer = f'{temp_dir}/result.zip'
    cmd = ['java', '-jar', '/app/src/xls2rdf-app-3.2.1-onejar.jar', 'convert', '-f', 'text/turtle', '--input', file_path, '-o', uitvoer]
    try: 
        p = subprocess.run(cmd,capture_output=True)
        p.check_returncode()
    except Exception as exc:
        print('Exception Handler')
        print(exc)
        return None
    # unzip
    zipfile = ZipFile(uitvoer)
    zipfile.printdir()
    zipfile.extractall(temp_dir)
    # get requested file
    for f in listdir(temp_dir):
        if f.endswith(filename+'.ttl'):
            return f'{temp_dir}/{f}'
    return None

