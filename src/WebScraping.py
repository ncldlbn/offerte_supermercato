# In questo file sono contenute le funzioni per lo scraping delle pagine web
# delle offerte di vari supermercati.
# Ogni funzione prende in input l'url della pagina da analizzare e il percorso
# nella repo del file con le parole chiave (key).
# Ogni funzione restituisce una lista con tutte le offerte che corrispondono
# alle parole chiave.

# -----------------------------------------------------------------------------
# LIBRERIE
# -----------------------------------------------------------------------------
from bs4 import BeautifulSoup
from functions import filtro
import datetime
import requests

# -----------------------------------------------------------------------------
# EUROSPIN 1
# -----------------------------------------------------------------------------
# Funzione per pagina promozioni Eurospin Trento.
def eurospin1(url, key):
    
    # lista output
    output = []
    
    # lista parole chiave
    with open(key) as file:
        keywords = file.read().split("\n")
    
    # elementi della pagina web corrispondenti ai prodotti in offerta
    weburl = requests.get(url)
    soup = BeautifulSoup(weburl.content, 'html.parser')
    items = soup.find_all("div", class_="sn_promo_grid_item_ct")
    
    # cicla su ogni prodotto
    for item in items:
        element = {}
        # nome prodotto
        prodotto = item.find("h2", itemprop="name").text.replace('\n', ' ')
        # se nel nome del prodotto ci sono delle parole chiave
        if filtro(prodotto, keywords) is True:
            
            # allora componi il dizionario con il resto delle informazioni sul
            # prodotto
            element['Negozio'] = "Eurospin via Fermi"
            element['Prodotto'] = prodotto.capitalize()
            element['Marca'] = item.find("div", itemprop="brand").text.capitalize()
            # Quantità e prezzo unitario
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
            # date inizio offerta e scadenza
            date = item.find("div", class_="date_current_promo").text
            start_date = date[date.find(""):].split()[0]
            end_date = date[date.find("-")+1:].split()[0]
            element["Inizio"] = datetime.datetime.strptime(start_date, '%d.%m').strftime('%d-%m')
            element["Scadenza"] = datetime.datetime.strptime(end_date, '%d.%m').strftime('%d-%m')
            # prezzo originale
            price = item.find("div", itemprop="offers").text.replace(',', '.')
            price = float(price[price.find(""):].split()[0])
            element['Prezzo originale'] = price
            # prezzo in offerta
            offer = item.find("i", itemprop="price").text.replace(',', '.')
            offer = float(offer[offer.find(""):].split()[0])
            element['Prezzo'] = offer
            # risparmio
            element['Risparmio'] = round(price-offer, 2)
            if price == offer:
                element['Prezzo originale'] = None
                element['Risparmio'] = None
            # url immagine prodotto
            element['img_url'] = item.find("img", itemprop="image")['src']
            
            # salva dizionario in lista output
            output.append(element)
            
    return output