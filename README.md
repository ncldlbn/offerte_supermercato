 
# Offerte Supermercati

This project is made to provide supermarket discounts as text message on Telegram.
It uses webscraping tools to search for intresting offers on supermarket web pages.

Only the following supermarket web pages are scraped:
- Eurospin Trento

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

1) Clone the repository:

```bash
$ git clone https://github.com/ncldlbn/offerte_supermercato.git
$ cd offerte_supermercato
$ pip install -r requirements.txt
```

2) In **`main.py`** replace:

```bash
/path/to/this/repo
``` 

with local absolute path like:
```bash
/home/folder/offerte_supermercato
```

3) In the folder **`./data/input/`** create new **`token.txt`** file containing the telegram token in the first row and the chatID in the second row, like the example below:

```bash
123456789:thisisafaketelegrambottoken
987654321
```
## Usage

Run the code as a cron job, for example if you want to run it every day at 1 PM place in the crontab the following line:
```bash
0 13 * * * python /home/folder/offerte_supermercato/src/main.py
```