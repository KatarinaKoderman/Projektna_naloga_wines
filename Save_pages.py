import re
import requests
import sys
import csv
import os
import sys
import codecs
import urllib.request as rq


import mytools

data_dir = "data/"  # ime mape z datotekami
search_results_dir = data_dir + "search_results/"  # ime mape, ki vsebuje strani, na katerih so povezave do vin
wine_data_dir = data_dir + "wine_data/"  # ime mape, ki vsebuje strani posameznih vin
urls = data_dir + "urls.txt"  # ime datoteke, ki vsebuje url-je do posameznih vin

wines_csv = 'vina.csv'  # csv datoteka
sommeliers_csv = 'somelierji.csv'
max_page = 7619  # število strani, ki jih pregledamo; 12. 1. je bilo na voljo 7618 strani


# save search result pages 1 to max_page in directory
def capture(directory):
    '''Zajame html-je strani s povezavami do podatkov o vinih.'''
    primary = 'http://www.winemag.com/ratings/'
    drink_type_and_rating = 's=&drink_type=wine&wine_type=Red,White&rating=98.0-*,94.0-97.99*' # Vzamemo rdeča in bela vina, ocenjena nad 94 točk.
    ## Rdečih in belih vin ocenjenih nad 94.0 je bilo 8938. Če v url-ju karkoli spremenimo (npr. poskusimo namesto desc napisati asc, nam stran prikaže vsa vina
    ## (op. nekatera celo podvojeno, kar je razvidno iz skupne številke vin). Ocena se tako pri zajemu podatkov ni upoštevala, ker pa so podatki že preneseni,
    ## jih bom upoštevala še pri analizi.
    other_parameters = '&sort_by=pub_date_web&sort_dir=desc'  # Če bi želeli osvežiti naše podatke, pregledamo kasneje dodana vina do tistega, s katerim smo tokrat začeli.
    for page in range(1, max_page):
        url = '{}?{}&page={}{}'.format(primary, drink_type_and_rating, page, other_parameters)
        file = '{}{:0004}.html'.format(directory, page)
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
    r'<div class=\"article-title\" style=\"padding-top: 20px;\">(?P<title>.+?)<\/div>.*?'
    r'<div class=\"rating\">.*?<span id=\"points\">(?P<points>\d+)<\/span>.*?<span id=\"points-label\">Points<\/span>.*?<span id=\"badges\">.*?'
    r'<p class=\"description\">(?P<wine_description>.*?)<\/p>.*?'
    r'<span><span>(?:\$)?(?P<price>.*?),&nbsp;&nbsp;.*?'
    r'<span>Appellation<\/span>.*?<\/div>.*?<span><a href=.*?>(?P<country>\w+\s?\w*)<\/a><\/span>.*?'
    r'<span>Alcohol<\/span>.*?<span><span>(?P<alcohol>.*?)%?<\/span><\/span>.*?'
    r'<span>Bottle Size<\/span>.*?<span><span>(?P<bottle_size>.*?[l|L])<\/span><\/span>.*?'
    r'<span>Category<\/span>.*?<span><span>(?P<category>Red|White|Sparkling|Rose|Dessert|Port|Sherry|Port\/Sherry|Fortified)<\/span><\/span>.*?',
    re.DOTALL)

  #  r'<div class=\"slug\">(?!Find Ratings)(?!What)(?:<\/div>.*?<div class=\"name\">(?P<sommelier>.*?)<\/div>.*?)?.*?'
regex_sommelier_only = re.compile('<div class=\"slug\"><\/div>.*?<div class=\"name\">(?P<sommelier>.*?)<\/div>', flags=re.DOTALL)

regex_sommelier = re.compile(
    r'<div class=\"slug\"><\/div>.*?<div class=\"name\">(?P<sommelier>.*?)<\/div>.*?'
    r'Reviews .*?(?P<reviews>[A-Z].*?)\.?'
    r'<\/h4>(?P<sommelier_description>.*?)'
    r'(?:<strong>|<\/span>).*?Email'
    , re.DOTALL)

def clean_wine(wine):
    data = wine.groupdict()
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
    print(data.get('sommelier'))
    return data

def clean_sommelier(sommelier):
    data = sommelier.groupdict()
    data['sommelier'] = data['sommelier'].strip()
    data['reviews'] = separate(data['reviews'].strip())
    data['sommelier_description'] = data['sommelier_description'].strip()

def separate(string):
    '''Loči besede danega niza zgolj glede na presledke, pike, vejice.'''
    word_list = []
    word = ''
    for a in string: # a predstavlja črko niza
        if a != ' ' or a != '.' or a != ',':
            word = word + a
        else:
            word_list.append(word)
            word = ''
    word_list.append(word)
    word_list = [w for w in word_list if w != 'and']
    return word_list

def izloci_podatke(imenik):
    vina = []
    sommelierji = []
    i = 1
    for html_datoteka in mytools.files(imenik):
        print('Parsing file {}'.format(html_datoteka))
        ujemanje = regex_sommelier_only.search(html_datoteka)
        print(ujemanje)
        if ujemanje:
            som = ujemanje.groupdict()
            som['sommelier'] = som['sommelier'].strip()
            for vino in re.finditer(regex_wine, mytools.file_contents(html_datoteka)):
                print('Parsing wine nr {}'.format(i))
                clean = clean_wine(vino)
                clean['sommelier'] = som['sommelier']
                vina.append(clean)
                for taster in re.finditer(regex_sommelier, mytools.file_contents(html_datoteka)):
                    sommelierji.append(clean_sommelier(taster))
                    print(len(sommelierji))
        else:
            for vino in re.finditer(regex_wine, mytools.file_contents(html_datoteka)):
                print('Parsing wine nr {}, ni tasterja'.format(i))
                new_match = clean_wine(vino)
                new_match['sommelier'] = None
                vina.append(new_match)
        i += 1
    return (vina, sommelierji)

#capture(search_results_dir)
#capture_urls(search_results_dir)
#capture_wines(wine_data_dir)


(vina, sommelierji) = izloci_podatke(wine_data_dir)

polja_vino = ['title', 'points', 'wine_descripton', 'price', 'country',
         'alcohol', 'bottle_size', 'category', 'sommelier']
polja_sommelier = ['sommelier', 'reviews', 'sommelier_description']


#mytools.write_table(vina, polja_vino, wines_csv)
#mytools.write_table(sommerierji, polja_sommelier, sommerliers_csv)

