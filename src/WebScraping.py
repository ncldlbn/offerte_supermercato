#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from functions import filtro
import datetime
import requests

def eurospin1(url, key):
    scraped = []
    
    with open(key) as file:
        keywords = file.read().split("\n")
        
    weburl = requests.get(url)
    soup = BeautifulSoup(weburl.content, 'html.parser')
    items = soup.find_all("div", class_="sn_promo_grid_item_ct")
    
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
            
            scraped.append(element)
            
    return scraped