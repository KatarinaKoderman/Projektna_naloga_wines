import requests
import csv
import os

import re
import sys
import codecs
import urllib.request as rq

def prepare_directory(file_name):
    '''Prepare an empty directory for the given file if directory doesn't exist yet.'''
    directory = os.path.dirname(file_name)
    if directory:
        os.makedirs(directory, exist_ok=True)

def save(url, file_name, enforce_transfer=False):
    '''Save page contents from given url in a file file_name.'''
    try:
        print('Saving {}...'.format(url), end='')
        sys.stdout.flush()
        if os.path.isfile(file_name) and not enforce_transfer:
            print('Already saved!')
            return
        req = rq.Request(url, headers={'User-Agent' : "Magic Browser"})
        con = rq.urlopen(req)
    except ConnectionError:
        print("Page doesn't exist!")
    else:
        prepare_directory(file_name)
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(con.read().decode())
            print("Saved!")

def file_contents(file_name):
    '''Return a string of contents of given file.'''
    with open(file_name, encoding='utf-8') as file:
        contents = file.read()
    return contents

def files(directory):
    '''Return names of all files in given directory and its name.'''
    return [os.path.join(directory, file) for file in os.listdir(directory)]

def write_table(dictionaries, cells, file_name):
    '''Create csv file with headers from a list of dictionaries.'''
    prepare_directory(file_name)
    with open(file_name, 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=cells)
        writer.writeheader()
        for dictionary in dictionaries:
            writer.writerow(dictionary)
