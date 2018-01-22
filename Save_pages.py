import re
import mytools
import csv
import requests
import csv
import os

import re
import sys
import codecs
import urllib.request as rq


data_dir = "data/"  # ime mape z datotekami
search_results_dir = data_dir + "search_results/"  # ime mape, ki vsebuje strani, na katerih so povezave do vin
wine_data_dir = data_dir + "wine_data/"  # ime mape, ki vsebuje strani posameznih vin
urls = data_dir + "urls.txt"  # ime datoteke, ki vsebuje url-je do posameznih vin

wines_csv = 'vina.csv'  # csv datoteka
sommeliers_csv = 'sommelierji.csv'
max_page = 7619  # število strani, ki jih pregledamo; 12. 1. je bilo na voljo 7618 strani


# save search result pages 1 to max_page in directory
def capture(directory):
    '''Zajame html-je strani s povezavami do podatkov o vinih.'''
    primary = 'http://www.winemag.com/ratings/'
    drink_type_and_rating = 's=&drink_type=wine&wine_type=Red,White&rating=98.0-*,94.0-97.99*'
    # Vzamemo rdeča in bela vina, ocenjena nad 94 točk.
    # Rdečih in belih vin ocenjenih nad 94.0 je bilo 8938.
    # Če v url-ju karkoli spremenimo (npr. poskusimo namesto desc napisati asc), nam stran prikaže vsa vina.
    # Ocena in vrsta vina se tako pri zajemu podatkov nista upoštevali, ker pa so podatki že preneseni,
    # jih bom upoštevala še pri analizi.
    other_parameters = '&sort_by=pub_date_web&sort_dir=desc'  # Če bi želeli osvežiti naše podatke, pregledamo kasneje dodana vina do tistega, s katerim smo tokrat začeli.
    for page in range(1, max_page):
        url = '{}?{}&page={}{}'.format(primary, drink_type_and_rating, page, other_parameters)
        file = '{}{:0004}.html'.format(directory, page)
        mytools.save(url, file)

regex_url = re.compile(
    r'<a class=\"review-listing\" href=\"(?P<new_url>http:\/\/www\.winemag\.com\/buying-guide\/.*?)\" data-review-id=\"\d+?\">',
    flags=re.DOTALL)

def clean_url(url):
    '''Počisti podatek o url-ju.'''
    podatki = url.groupdict()
    podatki['new_url'] = podatki['new_url'].strip()
    return podatki

# extract urls from each search result page in directory, append them to `urls`
def capture_urls(directory):
    '''Izloči podatke url-jev.'''
    i = 0
    for html_file in mytools.files(directory):
        print("Odpra je datoteka {}".format(html_file))
        for url in re.finditer(regex_url, mytools.file_contents(html_file)):
            with open(urls, 'a') as file:  # Če program znova zaženemo, bo iz shranjenih iskalnih strani v url.txt zopet shranil (append) url-je do posameznih vin
                podatek = clean_url(url)
                file.write(podatek.get('new_url') + '\n')
                i += 1
            print('From file {}, extracting url nr {}'.format(html_file, i))


def capture_wines(directory):
    '''Zajame html-je strani s podatki o vinih.'''
    with open(urls, 'r') as f:
        i = 0
        for url in f:
            i += 1
            print('Saving details for wine {}'.format(i))
            file = '{}/data{:000006}.html'.format(directory, i)
            mytools.save(url, file)

regex_wine = re.compile(
    r'data-review-id=\"(?P<id>\d+)\".*?'
    r'<div class=\"article-title\" style=\"padding-top: 20px;\">(?P<title>.+?)<\/div>.*?'
    r'<div class=\"rating\">.*?<span id=\"points\">(?P<points>\d+)<\/span>.*?<span id=\"points-label\">Points<\/span>.*?<span id=\"badges\">.*?'
    r'<p class=\"description\">(?P<wine_description>.*?)<\/p>.*?'
    r'<span><span>(?:\$)?(?P<price>.*?),&nbsp;&nbsp;.*?'
    r'<span>Appellation<\/span>.*?<\/div>.*?<span><a href=.*?>(?P<country>\w+\s?\w*)<\/a><\/span>.*?'
    r'<span>Alcohol<\/span>.*?<span><span>(?P<alcohol>.*?)%?<\/span><\/span>.*?'
    r'<span>Bottle Size<\/span>.*?<span><span>(?P<bottle_size>.*?[l|L])<\/span><\/span>.*?'
    r'<span>Category<\/span>.*?<span><span>(?P<category>Red|White|Sparkling|Rose|Dessert|Port|Sherry|Port\/Sherry|Fortified)<\/span><\/span>.*?',
    flags=re.DOTALL)

  #  r'<div class=\"slug\">(?!Find Ratings)(?!What)(?:<\/div>.*?<div class=\"name\">(?P<sommelier>.*?)<\/div>.*?)?.*?'
regex_sommelier_only = re.compile(r'<div class=\"slug\"><\/div>.*?<div class=\"name\">(?P<sommelier>.*?)<\/div>', flags=re.DOTALL)

regex_sommelier = re.compile(
    r'<div class=\"slug\"><\/div>.*?<div class=\"name\">(?P<sommelier>.*?)<\/div>.*?'
    r'Reviews (?!by).*?(?P<reviews>[A-Z].*?)'
    r'(?:(?:\.)|(?:<\/h4>)|(?:<\/div>)|(?:<\/b><\/span><\/p>))',
    flags=re.DOTALL)

def clean_wine(wine):
    '''Počisti podatke o vinu.'''
    data = wine.groupdict()
    data['id'] = int(data['id'])
    data['title'] = data['title'].strip()
    data['points'] = int(data['points'])
    data['wine_description'] = data['wine_description'].strip()
    if data['price'] == 'N/A':
        data['price'] = None
    else:
        data['price'] = float(data['price'])
    data['country'] = data['country'].strip()
    if data['alcohol'] == 'N/A':
        data['alcohol'] = None
    else:
        data['alcohol'] = float(data['alcohol'])
    data['bottle_size'] = data['bottle_size'].strip()
    data['category'] = data['category'].strip()
    return data

def clean_sommelier(sommelier):
    '''Počisti podatka o sommelierju.'''
    data = sommelier.groupdict()
    data['sommelier'] = data['sommelier'].strip()
    data['reviews'] = separate(data['reviews'])
    return data

def separate(string):
    '''Loči besedne zveze danega niza zgolj glede na pike, vejice in and.
        Hkrati pobriše znake med znakoma < in >. Vrne seznam besed.'''
    word_list = []
    word = ''
    dolzina = len(string)
    for i in range(dolzina):
        if string[i] == ',':
            word_list.append(word.strip())
            word = ''
        elif string[i] == '<':
            word_list.append(word.strip())
            word = string[i]
        elif string[i] == '>':
            word = ''
        elif '<' in word:
            continue
        else:
            word += string[i]
            if ' and' in word:
                word = word[:-4]
                word_list.append(word.strip())
                word = ''
            if word == ' other':
                word = ''
    word_list.append(word.strip())
    words = [country for country in word_list if country != '']
    return words


def izloci_podatke(imenik):
    '''Izloči podatke o vinih in sommelierjih.'''
    vina = []
    sommelierji = []
    i = 1
    for html_datoteka in mytools.files(imenik):
        print('Parsing file {}, parsing wine nr {}'.format(html_datoteka, i))
        ujemanje = regex_sommelier_only.search(mytools.file_contents(html_datoteka))
        if ujemanje:
            for vino in re.finditer(regex_wine, mytools.file_contents(html_datoteka)):
                clean = clean_wine(vino)
                for taster in re.finditer(regex_sommelier, mytools.file_contents(html_datoteka)):
                    clean_taster = clean_sommelier(taster)
                    sommelierji.append(clean_taster)
                    clean['sommelier'] = clean_taster['sommelier']
                vina.append(clean)
        else:
            for vino in re.finditer(regex_wine, mytools.file_contents(html_datoteka)):
                clean = clean_wine(vino)
                clean['sommelier'] = None
                vina.append(clean)
        i += 1
    return (vina, sommelierji)

#capture(search_results_dir)
#capture_urls(search_results_dir)
#capture_wines(wine_data_dir)

#(vina, sommelierji) = izloci_podatke(wine_data_dir)

polja_vino = ['id', 'title', 'points', 'wine_description', 'price', 'country',
         'alcohol', 'bottle_size', 'category', 'sommelier']
polja_sommelier = ['sommelier', 'reviews']

#mytools.write_table(vina, polja_vino, wines_csv)
#mytools.write_table(sommelierji, polja_sommelier, sommeliers_csv)

def precisti_podatke(input, output):
    '''Prečisti podatke sommelierjev.'''
    with open(input, 'r', encoding='utf-8') as csvinput:
        mytools.prepare_directory(output)
        with open(output, 'w', encoding='utf-8', newline='') as csvoutput:
            writer = csv.DictWriter(csvoutput, fieldnames=['sommelier', 'reviews1', 'reviews2', 'reviews3'])
            for row in csv.reader(csvinput):
                if row[0] == 'sommelier':
                    writer.writeheader()
                else:
                    countries = row[1].split(',')
                    new_countries = []
                    for country in countries:
                        new = re.sub('\[|\]', '', country)
                        new_countries.append(new)
                    while len(new_countries) < 3:
                        new_countries.append(None)
                    dict = {'sommelier': row[0], 'reviews1': new_countries[0], 'reviews2': new_countries[1], 'reviews3': new_countries[2]}
                    writer.writerow(dict)

#precisti_podatke('sommelierji.csv', 'poskuševalci.csv')