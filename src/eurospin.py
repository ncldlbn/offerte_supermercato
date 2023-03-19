import requests
import json
import datetime
import pandas as pd
from bs4 import BeautifulSoup

keywords = ['extravergine',
            'tonno',
            'mozzarelle',
            'yogurt',
            'fagioli',
            'piselli',
            'lenticchie',
            'funghi',
            'carciofini',
            'latte',
            'burro'
            ]

# -----------------------------------------------------------------------------
# EUROSPIN
# -----------------------------------------------------------------------------

url = requests.get('https://www.eurospin.it/promozioni/')
soup = BeautifulSoup(url.content, 'html.parser')
items = soup.find_all("div", class_="sn_promo_grid_item_ct")

#test = soup.find("span", style="color: #808080;")
#print(test.text.split()[3])

list1 = []
for item in items:
    
    element = {}

    title = item.find("h2", itemprop="name").text
    element['Prodotto'] = title.replace('\n', ' ').capitalize()
    
    if any(key in title.lower() for key in keywords):
    
        element['Marca'] = item.find("div", itemprop="brand").text.capitalize()
        
        date  = item.find("div", class_="date_current_promo").text
        start_date = date[date.find(""):].split()[0]
        end_date = date[date.find("-")+1:].split()[0]
        element["Inizio"] = datetime.datetime.strptime(start_date, '%d.%m').strftime('%d-%m')
        element["Scadenza"] = datetime.datetime.strptime(end_date, '%d.%m').strftime('%d-%m')
        
        price = item.find("div", itemprop="offers").text
        price = price.replace(',', '.')
        price = float(price[price.find(""):].split()[0])
        element['Prezzo originale'] = price
        
        offer = item.find("i", itemprop="price").text
        offer = offer.replace(',', '.')
        offer = float(offer[offer.find(""):].split()[0])
        element['Prezzo'] = offer
        
        element['Risparmio'] = round(price-offer, 2)
        
        if price == offer:
            element['Prezzo originale'] = None
            element['Risparmio'] = None
        
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
        
        element['img_url'] = item.find("img", itemprop="image")['src']
        
        list1.append(element)
df = pd.DataFrame(list1)


with open("../data/output/eurospin_last.json", "w") as file:
   json.dump(list1, file, indent=4)