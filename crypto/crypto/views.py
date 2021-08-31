import requests
import statistics
import time

import plotly.graph_objects as go

from datetime import date, datetime, timezone, timedelta
from django.shortcuts import render


def create_candlestick_chart(
  date_data: list,
  open_data: list,
  high_data: list,
  low_data: list,
  close_data: list
) -> str:
    """
    Creates html that will display a candlestick chart of the data provided.

            Parameters:
                    data_data (list): A list of date objects per interval.
                    open_data (list): A list of opening numbers per interval.
                    high_data (list): A list of high numbers per interval.
                    low_data (list): A list of low numbers per interval.
                    close_data (list): A list of closing numbers per interval.

            Returns:
                    (str): An html string of the candlestick chart.
    """
    fig = go.Figure(
      data=[
        go.Candlestick(
          x=date_data,
          open=open_data,
          high=high_data,
          low=low_data,
          close=close_data
        )
      ]
    )

    return fig.to_html()

def retrieve_ohlc_data(pair: str, start_date: datetime, end_date: datetime, interval: int) -> dict:
    """
    Retrieves the requested data from Kraken and processes it
    so that it's easier for the the chart to build from.

          Parameters:
                  pair (str): Currency pair code from Kraken. Example. XXBTZUSD
                  start_date (datetime): A python datetime object. The earliest date we want to query
                  end_date (datetime): A python datetime object. The latest date we want to keep.
                  interval (int): The timeframe interval in minutes. Choices: 1 5 15 30 60 240 1440 10080 21600

          Returns:
                  data (dict): Containing keys with arrays of data. Keys include date_data, open_data, high_data, low_data, close_data
    """
    # Offset the start date by one less day because for some reason
    # Kraken will not return the first day.
    start_offset = start_date - timedelta(days=1)
    start_timestamp = start_offset.replace(tzinfo=timezone.utc).timestamp()

    end_timestamp = end_date.replace(tzinfo=timezone.utc).timestamp()

    req_url = f'https://api.kraken.com/0/public/OHLC?pair={pair}&since={str(start_timestamp)}&interval={str(interval)}'

    resp = requests.get(req_url)

    # Response comes with two keys, error and result
    resp_dict = resp.json()

    # The results key has two keys, the PAIR (XXBTZUSD) and last
    results = resp_dict.get("result")

    # retrieve PAIR information
    pair_info = results.get(pair)

    data = {
      "date_data": [],
      "open_data": [],
      "high_data": [],
      "low_data": [],
      "close_data": []
    }

    # Go through the items on the list one by one
    for day in pair_info:
        # Best guess for what the values are that comes through
        # The documentation does not really explain
        # timestamp, open, high, low, close, VWAP volume?, trades
        ts, open_p, high_p, low_p, close_p, vwa_price, volume, trades = day
        
        # Check that the timestamp is at or equal to the end time
        # If we hit a time that's later, we don't look at the rest
        # as they are later than what we want
        if ts > end_timestamp:
           break

        # Convert timestamp to dateime object
        day_dateobj = datetime.utcfromtimestamp(ts)

        data["date_data"].append(day_dateobj)
        data["open_data"].append(float(open_p))
        data["high_data"].append(float(high_p))
        data["low_data"].append(float(low_p))
        data["close_data"].append(float(close_p))

    return data


def index(request):
    """
    Index page at path '/'
    """
    pair = "XXBTZUSD"
    start_date = datetime(2021, 3, 1, 0, 0, 0)
    end_date = datetime(2021, 4, 1, 0, 0, 0)
    interval = 1440

    context = {
        "heading": f"Kraken OHLC Data for pair {pair}",
        "start_date": start_date.strftime("%Y %m %d %Z"),
        "end_date": end_date.strftime("%Y %m %d %Z"),
        "interval": interval
    }

    # Retrieve our data from Kraken
    data = retrieve_ohlc_data(
      pair=pair, # Bitcoin to USD
      start_date=start_date,
      end_date=end_date,
      interval=interval # 24 hours interval
      # having smaller intervals will not return as far back 
      # as our start date This is because Kraken limits the 
      # number of results we can get back and it returns up 
      # to the most recent transactions.
    )

    # Create our chart
    context["chart"] = create_candlestick_chart(
      date_data=data.get("date_data"),
      open_data=data.get("open_data"),
      high_data=data.get("high_data"),
      low_data=data.get("low_data"),
      close_data=data.get("close_data"),
    )

    # Calculate mean and median
    all_data = data.get("open_data") + data.get("high_data") + data.get("low_data") + data.get("close_data")

    context["mean"] = statistics.mean(all_data)
    context["median"] = statistics.median(all_data)

    return render(request, "crypto/index.html", context)
