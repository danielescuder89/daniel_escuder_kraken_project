import pandas as pd


class Wrangler:

    def __init__(self):
        pass

    @staticmethod
    def clean_data(data_original):
        """
            We clean the data obtained from the Api and
            we are left with a treatable dataframe

            Parameters:
            date_original -- dataframe with our original trades
        """
        clean_data = {}
        # We consolidate a final dataframe
        for i, j in data_original.items():
            pair_data = pd.concat([x['trades'] for x in j])

            # We delete the same trades and also in the same instant of time
            pair_data = pair_data.drop_duplicates()

            # We get the necessary fields
            pair_data = pair_data[['dtime', 'price', 'volume', 'time']]

            # We order by instant of time
            pair_data = pair_data.sort_values('dtime', ascending=False)
            clean_data[i] = pair_data

        return clean_data
