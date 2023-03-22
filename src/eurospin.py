import requests
import datetime
import sqlite3
from bs4 import BeautifulSoup
from functions import offerte, invia_a_Telegram, salva_nel_db, filtro, confronta

with open("/home/nicola/Projects/offerte_supermercato/data/input/keywords.txt") as file:
    keywords = file.read().split("\n")

db = sqlite3.connect("/home/nicola/Projects/offerte_supermercato/data/output/offerte.db")
vecchie_offerte = offerte(db)

# -----------------------------------------------------------------------------
# EUROSPIN
# -----------------------------------------------------------------------------

url = requests.get('https://www.eurospin.it/promozioni/')
soup = BeautifulSoup(url.content, 'html.parser')
items = soup.find_all("div", class_="sn_promo_grid_item_ct")

tutte_le_offerte = []
for item in items:
    
    element = {}
    prodotto = item.find("h2", itemprop="name").text.replace('\n', ' ')
    
    if filtro(prodotto, keywords) is True:

        element['Negozio'] = "Eurospin via Fermi"
        element['Prodotto'] = prodotto.capitalize()
        element['Marca'] = item.find("div", itemprop="brand").text.capitalize()
        
        info = item.find("div", class_="i_price_info")
        if info is not None:
            info = info.text
            info = " ".join(info.split()).split(' - ')
            if len(info) == 1:
                element['Quantità'] = info[0]
                element['Prezzo unitario'] = None
            elif len(info) == 2:
                element['Quantità'] = info[0]
                element['Prezzo unitario'] = info[1]
        else:
            element['Quantità'] = None
            element['Prezzo unitario'] = None

        date = item.find("div", class_="date_current_promo").text
        start_date = date[date.find(""):].split()[0]
        end_date = date[date.find("-")+1:].split()[0]
        element["Inizio"] = datetime.datetime.strptime(start_date, '%d.%m').strftime('%d-%m')
        element["Scadenza"] = datetime.datetime.strptime(end_date, '%d.%m').strftime('%d-%m')
        
        price = item.find("div", itemprop="offers").text.replace(',', '.')
        price = float(price[price.find(""):].split()[0])
        element['Prezzo originale'] = price
        
        offer = item.find("i", itemprop="price").text.replace(',', '.')
        offer = float(offer[offer.find(""):].split()[0])
        element['Prezzo'] = offer
        
        element['Risparmio'] = round(price-offer, 2)
        
        if price == offer:
            element['Prezzo originale'] = None
            element['Risparmio'] = None
        
        element['img_url'] = item.find("img", itemprop="image")['src']
        
        tutte_le_offerte.append(element)

# confronto con precedente lista offerte ed estrazione di quelle nuove 
nuove_offerte = confronta(tutte_le_offerte, vecchie_offerte)

# se ci sono nuove offerte allora inviale su telegram e salvale nel db
if nuove_offerte:        
    for prodotto in nuove_offerte:
        invia_a_Telegram(prodotto)
        salva_nel_db(db, prodotto)
        
db.commit()
db.close()
        



    