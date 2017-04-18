# Multitran_scrapper
The scrapper of multitran.ru

## Starting
- Go to `spiders` folder and open `multitran.py`
- This file includes some settings such as `INPUT_CSV_NAME`. You should change it according your task. The description of settings are available.
- Run `scrapy crawl multitran` from command line
- See file with output data (path can be changed in setting)

## Spiders
- multitran: the parser which translates list of English to Russian words
- multitran_dictionaries: the parser which find full name for abbreviation of dictionary
- multitran_all_dictionaries: the parser which parses all dictionaries from multitran
