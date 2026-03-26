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
    cmd = ['java', '-jar', 'xls2rdf-app-3.2.1-onejar.jar', 'convert', '-f', 'text/turtle', '--input', file_path, '-o', uitvoer]
    p = subprocess.Popen(cmd)
    try:
        p.wait()
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()
    except subprocess.CalledProcessError as e:
        end_prog(e.returncode)
    # unzip
    zipfile = ZipFile(uitvoer)
    zipfile.printdir()
    zipfile.extractall(temp_dir)
    # get requested file
    for f in listdir(temp_dir):
        print(f)
        if f.endswith(filename):
            return f'{temp_dir}/{f}'
    return None

