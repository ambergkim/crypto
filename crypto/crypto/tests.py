from django.test import TestCase
from crypto.views import create_candlestick_chart, retrieve_ohlc_data
from datetime import datetime

class CandleStickHelperTests(TestCase):
    def test_that_helper_returns_html(self):
        """Tests that the helper will return html"""
        html_data = create_candlestick_chart(
          date_data=[datetime(2021, 1, 1, 0, 0, 0)],
          open_data=["3"],
          high_data=["10"],
          low_data=["1"],
          close_data=["6"]
        )

        self.assertTrue('Plotly' in html_data)

class RetrieveOhlcDataTests(TestCase):
    def test_helper_returns_ok_data(self):
        """Tests that the help will return ok data"""
        start_date = datetime(2021, 8, 29, 0, 0, 0)
        end_date = datetime(2021, 8, 29, 0, 0, 0)

        expected_data = {
          'date_data': [start_date],
          'open_data': [48895.7],
          'high_data': [49653.9],
          'low_data': [47800.0],
          'close_data': [48787.7]
        }

        ohlc_data = retrieve_ohlc_data(
          pair="XXBTZUSD",
          start_date=start_date,
          end_date=end_date,
          interval=1440
        )

        self.assertDictEqual(expected_data, ohlc_data)

class IndexViewTests(TestCase):
    def test_view_loads_correctly(self):
        """Test that we get the correct page and information when
        navigating to the index"""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crypto/index.html')
        self.assertEqual(response.context.get("heading"), "Kraken OHLC Data for pair XXBTZUSD")
        self.assertEqual(response.context.get("start_date"), datetime(2021, 3, 1, 0, 0, 0).strftime("%Y %m %d %Z"))
        self.assertEqual(response.context.get("end_date"), datetime(2021, 4, 1, 0, 0, 0).strftime("%Y %m %d %Z"))
        self.assertEqual(response.context.get("interval"), 1440)
        self.assertTrue('Plotly' in response.context.get("chart"))
        self.assertEqual(response.context.get("mean"), 54688.365625)
        self.assertEqual(response.context.get("median"), 55568.25)
