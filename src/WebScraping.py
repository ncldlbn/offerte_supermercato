# In questo file sono contenute le funzioni per lo scraping delle pagine web
# delle offerte di vari supermercati.
# Ogni funzione prende in input l'url della pagina da analizzare e il percorso
# nella repo del file con le parole chiave (key).
# Ogni funzione restituisce una lista con tutte le offerte che corrispondono
# alle parole chiave.

# -----------------------------------------------------------------------------
# LIBRERIE
# -----------------------------------------------------------------------------

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from functions import filtro, url_is_valid
from datetime import datetime
import time
import re

# -----------------------------------------------------------------------------
# EUROSPIN 1
# -----------------------------------------------------------------------------
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
            element["Inizio"] = datetime.strptime(start_date, '%d.%m').strftime('%d-%m')
            element["Scadenza"] = datetime.strptime(end_date, '%d.%m').strftime('%d-%m')
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

# -----------------------------------------------------------------------------
# POLI Via Fermi
# -----------------------------------------------------------------------------
def poli(url, key):
    output = []
    # lista parole chiave
    with open(key) as file:
        keywords = file.read().split("\n")
    # initiating the webdriver. Parameter includes the path of the webdriver.
    # instantiate options 
    chrome_options = webdriver.ChromeOptions() 
    # run browser in headless mode 
    chrome_options.headless = True 
    driver = webdriver.Chrome('./chromedriver', options=chrome_options) 
    driver.get(url)
    # lascia un po' di tempo alla pagina di caricarsi
    time.sleep(5) 

    # seleziona poli via fermi
    drop = Select(driver.find_element('id', 'ddNegozio'))
    drop.select_by_value("00203")
    # accetta cookie e clicca trova offerte
    driver.find_element('xpath', "//button[contains(text(), 'Accetta')]").click()
    driver.find_element('id', "ctl00_ContentPlaceBody_CambiaNegozio1_btnTrova").click()
    # aspetta che la pagina si carichi del tutto
    time.sleep(10)
    # estrai codice html
    html = driver.execute_script("return document.body.innerHTML;")
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all('div', 'band-volantino-prodotto visible container-prodotto')

    # leggi la data di scandenza delle offerte
    date = soup.find('div', class_='pagina-testo').text
    date = re.search(r'\d{2}/\d{2}/\d{4}', date)
    date = datetime.strptime(date.group(), '%d/%m/%Y').date()
    scadenza = date.strftime("%d-%m")
    # leggi il contenuto delle offerte
    for item in items:
        element = {}
        prodotto = item.find("div", class_="band-volantino-prodotto-titolo").text.strip()
        if filtro(prodotto, keywords) is True:
            element['Negozio'] = "Poli via Fermi"
            element['Prodotto'] = prodotto.capitalize()
            element['Marca'] = item.find("span", class_="band-volantino-prodotto-produttore").text.capitalize()
            element['Quantità']  =  item.find("span", class_="band-volantino-prodotto-quantita").text
            # prezzo originale
            price = item.find("div", class_="band-volantino-prodotto-prezzo-normale").text.replace(",", ".").replace("€", "").strip()
            if len(price) > 0:
                element['Prezzo originale'] = float(price)
            else:
                element['Prezzo originale'] = None
            # prezzo offerta
            offer = item.find("div", class_="band-volantino-prodotto-prezzo-scontato").text.replace(",", ".").replace("€", "").strip()
            if len(offer) > 0:
                element['Prezzo'] = float(offer)
            else:
                element['Prezzo'] = None
            # prezzo unitario
            element['Prezzo unitario'] = item.find("div", class_="band-volantino-prodotto-prezzo-al-kg").text.replace(",", ".").replace("€ ", " €").replace("(", "").replace(")", "").strip()
            # Risparmio
            if element['Prezzo'] and element['Prezzo originale']: 
                element['Risparmio'] = round(element['Prezzo originale']-element['Prezzo'], 2)
            else:
                element['Risparmio'] = None
            # immagine
            url = item.find("img", class_="contain")['data-src']
            if url_is_valid(url):
                element['img_url'] = url
            else:
                element['img_url'] = item.find("img", class_="contain")['src']
            # data di inizio e scadenza
            element["Inizio"] = None
            element["Scadenza"] = scadenza
            # salva dizionario in lista output
            output.append(element)
    driver.quit()   
    return output
    