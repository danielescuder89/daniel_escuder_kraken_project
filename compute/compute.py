class Computer:

    def __init__(self, data):
        self.data = {'trades': data}

    def compute_vwap(self, price='price', volume='volume',
                     time='dtime', interval='1 minute'):
        """
            Volume-weighted average price calculation.

            Update class attributes:

                Σ (volume * price) / total volume

            Parameters:
            price -- string with the name of first argument of the ratio
            volume -- string with the name of second argument of the ratio
            time -- column name with dates of the trades
            interval -- input that defines the time interval (bin) defining the trades perimeter
        """
        # We initialize our dataframe for the vwap
        vwap_df = self.data['trades']

        # Based on the frequency parameter, we get the parameter for the resample
        if interval == "1 minute":
            interval_resample = '1Min'
        elif interval == "5 minutes":
            interval_resample = '5Min'
        elif interval == "30 minutes":
            interval_resample = '30Min'
        elif interval == "60 minutes":
            interval_resample = 'H'
        elif interval == "Daily":
            interval_resample = 'D'
        elif interval == "Weekly":
            interval_resample = 'W'
        else:
            interval_resample = 'M'

        pxv = price + 'x' + volume

        # We calculate price*volume for the weighting
        vwap_df[pxv] = vwap_df[price] * vwap_df[volume]

        # We add based on our time interval
        vwap_df = vwap_df.resample(interval_resample, on=time).agg({
            'volume': 'sum', pxv: 'sum'})

        # We calculate the ratio
        vwap_df[price] = vwap_df[pxv] / vwap_df[volume]

        # We save in our main attribute
        self.data['vwap'] = vwap_df
