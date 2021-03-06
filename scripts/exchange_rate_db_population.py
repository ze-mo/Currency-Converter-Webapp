from cassandra.cluster import Cluster
import requests
import time
import itertools
from datetime import datetime
import datetime
import logging
import os

cluster = Cluster()
session = cluster.connect('forex_data')
#...
<<<<<<< HEAD
API_KEY = ''
=======
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
>>>>>>> e4209f8 (Added logger and replaced print statements with logging)

formatter = logging.Formatter('%(asctime)s | %(name)s | %(message)s')

file_handler = logging.FileHandler("scripts/db_population.log")
error_file_handler = logging.FileHandler("scripts/db_population.log")

file_handler.setLevel(logging.INFO)
error_file_handler.setLevel(logging.ERROR)

error_file_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(error_file_handler)

list_of_currencies = ['BGN', 'GBP', 'USD', 'CNY', 'CHF', 'EUR']
list_of_permutations = list(itertools.permutations(list_of_currencies))
set_of_paired_currencies = set()
for perm_tuple in list_of_permutations:
    set_of_paired_currencies.add(perm_tuple[0] + perm_tuple[1])

def populate_db(pairs):
    """Submits a request to the Alphavantage API with the parameters set for each permutation of the currencies list.
    After the data is retrieved, it's upserted into the rates_by_pairs table, where each record represents a currency pair 
    with its exchange rate at a 15 minute interval."""

    counter = 0
    for pair in pairs:
        url = f'https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={pair[:3]}&to_symbol={pair[3:]}&interval=15min&outputsize=compact&apikey={os.environ.get("FOREX_API_KEY")}'
        r = requests.get(url)
        data_dict = r.json()
        logger.info(r.status_code)
        try:
            values_by_date = data_dict["Time Series FX (15min)"]
            last_refreshed_api = data_dict["Meta Data"]["4. Last Refreshed"]
            last_refresh_date = datetime.datetime.strptime(last_refreshed_api, '%Y-%m-%d %H:%M:%S')
            for key, value in values_by_date.items():
                key_date_obj = datetime.datetime.strptime(key, '%Y-%m-%d %H:%M:%S')
                tdelta = datetime.timedelta(minutes=45)
                limit = last_refresh_date - tdelta
                if key_date_obj > limit:
                    logger.info(f'{pair} | {key_date_obj} not included')
                    continue
                else:
                    refreshed = key
                    close_value = value["4. close"]
                    session.execute(f"INSERT INTO rates_by_pairs (pair, last_refreshed, exchange_rate, id) VALUES ('{pair}', '{refreshed}', {close_value}, now()) if not exists")
            counter += 1
            logger.info(f'{pair} Added... ')


        except Exception as e:
            logger.exception(e)
        
        if counter == 5:
            logger.info('Sleeping 60 seconds... ')
            time.sleep(60)
            counter = 0

if __name__ == "__main__":
<<<<<<< HEAD
    populate_db(set_of_pairs)
    print("Finished")
=======
    populate_db(set_of_paired_currencies)
    logger.info("Finished")
>>>>>>> e4209f8 (Added logger and replaced print statements with logging)
