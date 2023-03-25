# -----------------------------------------------------------------------------
# LIBRERIE
# -----------------------------------------------------------------------------
import sqlite3
from functions import offerte, invia_a_Telegram, salva_nel_db, confronta
from WebScraping import eurospin1

# -----------------------------------------------------------------------------
# URLs PAGINE WEB OFFERTE (aggiungere qui urls altre pagine)
# -----------------------------------------------------------------------------
# pagina promozioni eurospin Trento
eurospin1_url = 'https://www.eurospin.it/promozioni/'

# -----------------------------------------------------------------------------
# FILE e PERCORSI
# -----------------------------------------------------------------------------
# path to this repo
path = "/home/nicola/Projects/offerte_supermercato/"

# database offerte già inviate
db_path = path + "data/offerte.db"
# lista parole chiave
key_path = path + "data/keywords.txt"
# token e id bot telegram
token = path + "data/bot.txt"

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
# Scraping pagine web supermercati -> lista offerte il cui nome prodotto
# corrisponde alle parole chiave del file 'keywords.txt'
offerte_eurospin1 = eurospin1(eurospin1_url, key_path)

# Lista delle offerte da tutti i supermercati
tutte_le_offerte = offerte_eurospin1 # + offerte_eurospin2 + offerte_poli + ...

# Confronto con lista vecchie offerte (sul db) ed estrazione di quelle nuove
# che non sono state ancora inviate
vecchie_offerte = offerte(db_path)
nuove_offerte = confronta(tutte_le_offerte, vecchie_offerte)

# Se ci sono nuove offerte allora inviale su telegram e salvale nel db.
# Alla fine del processo, salva le modifiche al db e chiudilo  
if nuove_offerte:
    db = sqlite3.connect(db_path)
    for prodotto in nuove_offerte:
        invia_a_Telegram(token, prodotto)
        salva_nel_db(db, prodotto)
    db.commit()
    db.close()
    