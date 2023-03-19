#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import telegram

def Send_to_Telegram(data):
    
    # Impostare il token del bot Telegram
    bot_info = open("../data/input/bot.txt","r")
    bot_token = bot_info.readline().strip('\n')
    ID = bot_info.readline().strip('\n')

    # Inizializzare il bot Telegram
    bot = telegram.Bot(token=bot_token)

    # Invia un messaggio per ogni elemento nel JSON
    for item in data:
        
        message = item['Prodotto'] + '\n' + '€' + str(item['Prezzo'])
        if item['Risparmio'] is not None:
            message = message + ' (- €'+ str('{0:.2f}'.format(item['Risparmio'])) + ')' 
        if item['Quantità'] is not None:
            message = message + '\n' + item['Quantità'] 
        if item['Prezzo unitario'] is not None:
            message = message + '\n' + item['Prezzo unitario']
        message = message + '\n\n' + 'L\'offerta scade il ' + item['Scadenza']
        
        bot.send_document(chat_id=ID, document=item['img_url'], caption=message)
