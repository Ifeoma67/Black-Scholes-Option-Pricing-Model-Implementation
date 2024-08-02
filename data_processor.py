import pandas as pd
import numpy as np
import yfinance as yf
import logging
from utils import retry_on_exception

class DataProcessor:
    """
    A class to handle data fetching and preprocessing for the Black-Scholes model.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @retry_on_exception(max_attempts=3, delay=1)
    def fetch_stock_data(self, ticker, start_date, end_date):
        """Fetch stock data from Yahoo Finance."""
        self.logger.info(f"Fetching stock data for {ticker} from {start_date} to {end_date}")
        return yf.download(ticker, start=start_date, end=end_date)['Adj Close']

    @staticmethod
    def calculate_returns(prices):
        """Calculate logarithmic returns from price data."""
        return np.log(prices / prices.shift(1))

    @staticmethod
    def calculate_volatility(returns, window=252):
        """Calculate rolling volatility from returns data."""
        return returns.rolling(window=window).std() * np.sqrt(252)

    def preprocess_data(self, data):
        """Preprocess the stock data for use in the Black-Scholes model."""
        self.logger.info("Preprocessing stock data")
        data = data.dropna()
        data = pd.DataFrame(data)  # Ensure data is a DataFrame
        data['Returns'] = self.calculate_returns(data['Adj Close'])
        data['Volatility'] = self.calculate_volatility(data['Returns'])
        return data