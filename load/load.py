import krakenex
from pykrakenapi import KrakenAPI
import numpy as np
import time


class Loader:

    def __init__(self, api=KrakenAPI(krakenex.API())):
        self.api = api
        self.pairs = {}
        self.data = {}

    def get_all_pairs(self):
        """
            Save a complete list of all pairs by connecting to the KRAKEN api.
        """
        self.pairs = self.api.get_tradable_asset_pairs().loc[:, [
            'altname', 'wsname']]

    def load_thousand_trades(self, pair, date_initial):
        """
            We get a thousand ticks (max) of a currency pair by connecting to the KRAKEN API.

            Parameters:
            pair -- string with the name of crytocurrency pair
            date_initial -- date from which we will get our ticks
        """
        # We obtain the thousand records from the indicated date
        trades, last_trade = self.api.get_recent_trades(pair, date_initial)

        # We sort by the date of each record and reset the index
        trades = trades.sort_values('time', ascending=False)
        trades = trades.reset_index()

        # We get the first tick and the last tick
        first_trade = trades['time'].iloc[-1]
        last_trade = trades['time'].iloc[0]
        return {'first': first_trade, 'last': last_trade, 'trades': trades}

    def load_historic(self, pair, date_initial, date_final):
        """
            We get all trades between two dates

            Parameters:
            pair -- string with the name of crytocurrency pair
            date_initial -- date from which we will get all our ticks
            date_final -- date until which we get our ticks
        """
        # We initialize the dataframe of the trades
        data_pair = []

        # We save our start date
        last_date_load = date_initial

        while last_date_load <= date_final:
            # We obtain the corresponding records between our dates
            split = self.load_thousand_trades(pair, last_date_load)
            # We collect our data
            data_pair.append(split)
            # We update our start date
            last_date_load = split['last']
            # We sleep the connection with a random of a uniform so that KRAKEN does not block us
            time.sleep(np.random.uniform(1, 1.5))

            print(pair + ': ' + 'Loading from ' + str(split['trades']['dtime'].iloc[-1]) + ' to ' + str(
                split['trades']['dtime'].iloc[0]))

        # We save our download in the corresponding attribute
        self.data[pair] = data_pair
