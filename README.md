# Vina
Projektna naloga pri predmetu programiranje 1

## Vsebovane datoteke
V datoteki mytools.py se nahajajo orodja za zajem podatkov, v datoteki Save_pages.py pa koda za zajem podatkov. Ta šmorn res ni posebno lep. :)
Program deluje tako, da najprej z iskalne strani shrani url povezave do vin, nato pa z vsake povezave shrani še podatke o vinu.
Ker je podatkov veliko, priporočam, da se datoteke ne zaganja, temveč se uporabi naloženi csv datoteki.
V datoteki vina.csv so podatki o vinih, v datoteki sommelierji.csv so podatki o sommelierjih.
V datoteki vina_analiza.ipynb se nahaja analiza podatkov.

## Zajem podatkov
Podatki so zajeti za vsa vina s strani winemag.com na dan 12. 1. 2018.
Če želite sami zagnati kodo, bodite pripravljeni, da bo za zajem podatkov treba nekajkrat menjati IP.
### Zajeti podatki o vinih:
- id,
- naslov (ime vina),
- točke,
- opis,
- cena,
- država pridelave,
- stopnja vsebnosti alkohola,
- velikost steklenice,
- kategorija,
- sommelier.

Treba je poudariti, da točke podeljujejo ocenjevalci (sommelierji). Pri vseh vinih je ta le en ali pa ni naveden, zato lahko rečemo, da so točke nekoliko subjektvine.
Razlaga točk se nahaja v vina_analiza.ipynb.


### Zajeti podatki o sommelierjih:
- sommelier,
- katere države pokriva.

Lahko bi zajeli tudi opis sommelierjev, vendar so strani različno grajene, zato tega podatka nisem zajela.
Ravno tako bi lahko zajeli tudi elektronski naslov, zatorej če bi želeli katerega izmed sommelierjev kontaktirati, lahko njegov e-mail poiščete na strani winemag.com.

## Analiza

