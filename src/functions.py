# In questo file sono contenute le funzioni per gestire le offerte lette dalla
# pagina web, inviarle su Telegram, gestire il DB per tenere traccia delle
# offerte già inviate.

# -----------------------------------------------------------------------------
# LIBRERIE
# -----------------------------------------------------------------------------
import telegram
import datetime
import sqlite3
from urllib.parse import urlparse

# -----------------------------------------------------------------------------
# Legge il database con le offerte già inviate, elimina le offerte già scadute,
# restituisce una lista con le offerte già inviate.
# -----------------------------------------------------------------------------
def offerte(database_path):
    database = sqlite3.connect(database_path)
    c = database.cursor()
    ieri = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%d-%m')
    c.execute('DELETE FROM last WHERE Scadenza = ?', (ieri,))
    c.execute('SELECT * FROM last')
    old = c.fetchall()
    database.commit()
    database.close()
    return old
    
# -----------------------------------------------------------------------------
# BOT TELEGRAM: prende in input il percorso con il file che contiene il token e
# l'id del bot telegram e il dizionario che contiene le informazioni del 
# prodotto da inviare.
# -----------------------------------------------------------------------------
def invia_a_Telegram(tkn, item):
    # Impostare il token e l'ID del bot Telegram
    bot_info = open(tkn,"r")
    bot_token = bot_info.readline().strip('\n')
    ID = bot_info.readline().strip('\n')
    # Inizializzare il bot Telegram
    bot = telegram.Bot(token=bot_token)
    # Invia un messaggio per ogni prodotto
    message = item['Negozio'] + '\n\n' + item['Prodotto'] + '\n' + '€' + str(item['Prezzo'])
    if item['Risparmio'] is not None:
        message = message + ' (- €'+ str('{0:.2f}'.format(item['Risparmio'])) + ')' 
    if item['Quantità'] is not None:
        message = message + '\n' + item['Quantità'] 
    if item['Prezzo unitario'] is not None:
        message = message + '\n' + item['Prezzo unitario']
    message = message + '\n\n' + 'L\'offerta scade il ' + item['Scadenza']
    bot.send_document(chat_id=ID, 
                      document=item['img_url'], 
                      caption=message)
        
 # -----------------------------------------------------------------------------
 # Salva nel DB un prodotto nuovo
 # -----------------------------------------------------------------------------   
def salva_nel_db(database, item):
    cursor = database.cursor()
    cursor.execute('INSERT INTO last (Negozio, Prodotto, Marca, Inizio, Scadenza, Prezzo_originale, Prezzo, Risparmio, Prezzo_unitario, Quantità, img_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
              (item['Negozio'], item['Prodotto'], item['Marca'], item['Inizio'], item['Scadenza'], item['Prezzo originale'], item['Prezzo'], item['Risparmio'], item['Prezzo unitario'], item['Quantità'], item['img_url']))
    
# -----------------------------------------------------------------------------
# Filtro per selezionare i prodotti che contengono le parole chiave della lista
# -----------------------------------------------------------------------------
def filtro(title, key):
    for word in key:
        if len(word) > 0:
            if all(w in title.lower() for w in word.split()):
                return True
          
# -----------------------------------------------------------------------------
# Confronta le offerte appena lette dalla pagina web con le offerte contenute 
# nel DB e restituisce quelle nuove da inviare
# -----------------------------------------------------------------------------           
def confronta(all_offers, old_offers):
    new_offers = []
    for new in all_offers:
        presente = False
        for old in old_offers:
            if (new['Negozio'] == old[0] and 
                new['Prodotto'] == old[1] and 
                new['Marca'] == old[2] and
                new['Inizio'] == old[3] and
                new['Scadenza'] == old[4] and
                new['Prezzo originale'] == old[5] and
                new['Prezzo'] == old[6] and
                new['Prezzo unitario'] == old[8] and
                new['Quantità'] == old[9] and
                new['img_url'] == old[10]):
                presente = True
        if not presente:
            new_offers.append(new)
    return new_offers

# -----------------------------------------------------------------------------
# Controlla se un url è valido. Serve per verificare di aver estratto l'url
# corretto per le immagini dei prodotti.
# ----------------------------------------------------------------------------- 
def url_is_valid(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False