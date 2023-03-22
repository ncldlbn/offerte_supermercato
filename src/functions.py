import telegram
import datetime

def offerte(database):
    c = database.cursor()
    ieri = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%d-%m')
    c.execute('DELETE FROM last WHERE Scadenza = ?', (ieri,))
    database.commit()
    c.execute('SELECT * FROM last')
    database.commit()
    return c.fetchall()
    
    
def invia_a_Telegram(item):
    # Impostare il token del bot Telegram
    bot_info = open("/home/nicola/Projects/offerte_supermercato/data/input/bot.txt","r")
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
                      caption=message,
                      parse_mode=telegram.ParseMode.MARKDOWN)
        
    
def salva_nel_db(database, item):
    cursor = database.cursor()
    cursor.execute('INSERT INTO last (Negozio, Prodotto, Marca, Inizio, Scadenza, Prezzo_originale, Prezzo, Risparmio, Prezzo_unitario, Quantità, img_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
              (item['Negozio'], item['Prodotto'], item['Marca'], item['Inizio'], item['Scadenza'], item['Prezzo originale'], item['Prezzo'], item['Risparmio'], item['Prezzo unitario'], item['Quantità'], item['img_url']))
    
        
def filtro(title, key):
    for word in key:
        if len(word) > 0:
            if all(w in title.lower() for w in word.split()):
                return True
          
            
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
