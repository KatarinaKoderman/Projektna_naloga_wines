import re
import requests
import sys
import csv
import os
import sys
import codecs
import urllib.request as rq

import mytools

data_dir = "data/"
search_results_dir = data_dir + "search_results/"
wine_data_dir = data_dir + "wine_data/"
urls = data_dir + "urls.txt"
wines_csv = 'vina.csv'
max_page = 2

# save search result pages 1 to max_page in directory
def capture(directory):
    '''Zajame html-je strani s povezavami do podatkov o vinih.'''
    primary = 'http://www.winemag.com/ratings/'
    drink_type_and_rating = 's=&drink_type=wine&wine_type=Red&rating=94.0-97.99,98.0-\*'
    other_parameters = '&sort_by=retail&sort_dir=asc'
    for page in range(1, max_page):
        url = '{}?{}&page={}{}'.format(primary, drink_type_and_rating, page, other_parameters)
        file = '{}{:003}.html'.format(directory, page)
        mytools.save(url, file)

regex_url = re.compile(
    r'<a class=\"review-listing\" href=\"(?P<new_url>http:\/\/www\.winemag\.com\/buying-guide\/.*?)\" data-review-id=\"\d+?\">',
    flags=re.DOTALL)

def clean_url(url):
    podatki = url.groupdict()
    podatki['new_url'] = podatki['new_url'].strip()
    return podatki

# extract urls from each search result page in directory, append them to `urls`
def capture_urls(directory):
    '''Izloči podatke url-jev.'''
    i = 0
    for html_file in mytools.files(directory):
        for url in re.finditer(regex_url, mytools.file_contents(html_file)):
            with open(urls, 'a') as file:
                podatek = clean_url(url)
                file.write(podatek.get('new_url') + '\n')
                i += 1
            print('From file {}, extracting url nr {}'.format(html_file, i))

#captdata_dir/strani')

def capture_wines(directory):
    '''Zajame html-je strani s podatki o vinih.'''
    with open(urls, 'r') as f:
        i = 0
        for line in f:
            i += 1
            url = line
            file = '{}/data{:0004}.html'.format(directory, i)
            mytools.save(url, file)
            print('Saving details for wine {}'.format(i))

regex_wine = re.compile(
    r'<div class=\"article-title\">(?P<title>.+?)<\/div>.*?'
    r'<div class=\"rating\">.*?<span id=\"points\">(?P<points>\d\d)<\/span>.*?<span id=\"points-label\">Points<\/span>.*?<span id=\"badges\">.*?'
    r'<span><span>\$(?P<price>.*?),&nbsp;&nbsp;.*?'
    r'<span>Variety<\/span>.*?<span><a href=\"http:\/\/www.*?\">(?P<variety>\w*)<\/a><\/span>.*?'
    r'<span>Appellation<\/span>.*?<\/div>.*?<span><a href=.*?>(?P<country>\w+)<\/a><\/span>.*?'
    r'<span>Alcohol<\/span>.*?<span><span>(?P<alcohol>\d.*?)%<\/span><\/span>.*?'
    r'<div class=\"slug\"><\/div>.*?<div class=\"name\">(?P<sommelier>.*?)<\/div>.*?',
    re.DOTALL)

def clean_wine(wine):
    data = wine.groupdict()
    data['title'] = data['title'].strip()
    data['points'] = int(data['points'])
    data['price'] = float(data['price'])
    data['variety'] = data['variety'].strip()
    data['country'] = data['country'].strip()
    data['alcohol'] = float(data['alcohol'])
    data['sommelier'] = data['sommelier'].strip()
    return data

def izloci_podatke_vin(imenik):
    vina = []
    i = 1
    for html_datoteka in mytools.files(imenik):
        print('Parsing file {}'.format(html_datoteka))
        for vino in re.finditer(regex_wine, mytools.file_contents(html_datoteka)):
            print('Parsing wine nr {}'.format(i))
            vina.append(clean_wine(vino))
            i += 1
        if i == 30:
            return vina
    return vina



# capture(search_results_dir)
# capture_urls(search_results_dir)
# capture_wines(wine_data_dir)

vina = izloci_podatke_vin(wine_data_dir)

mytools.write_table(vina, ['title', 'points', 'price', 'variety', 'country', 'alcohol', 'sommelier'], wines_csv)
