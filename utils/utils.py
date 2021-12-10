import datetime as dt
from datetime import datetime
import re


class Utils:

    def __init__(self):
        pass

    @staticmethod
    def date_formats(date):
        """
            Given a date type string, get four formats date needed in the project

            Parameters:
            date -- string with a date
        """
        dt_string = date
        dt_list = re.split('-| |:', date)
        dt_datetime = datetime(*[int(x)
                                 for x in dt_list], tzinfo=dt.timezone.utc)
        dt_unix = int(dt_datetime.timestamp())
        formats = {
            'unixtime': dt_unix,
            'string': dt_string,
            'list': dt_list,
            'datetime': dt_datetime,
            }

        return formats
