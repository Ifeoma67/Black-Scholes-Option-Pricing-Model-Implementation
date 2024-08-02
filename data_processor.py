import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import logging
from utils import retry_on_exception

class DataProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @retry_on_exception(max_attempts=3, delay=1)
    def fetch_stock_data(self, ticker, start_date, end_date):
        """Fetch stock data from Yahoo Finance."""
        self.logger.info(f"Fetching stock data for {ticker} from {start_date} to {end_date}")
        return yf.download(ticker, start=start_date, end=end_date)

    @retry_on_exception(max_attempts=3, delay=1)
    def fetch_option_data(self, ticker, expiration_date=None):
        """Fetch option chain data for a given expiration date or the next available one."""
        stock = yf.Ticker(ticker)
        
        if expiration_date is None:
            # Get the next available expiration date
            expiration_dates = stock.options
            if not expiration_dates:
                raise ValueError("No option data available for this ticker.")
            expiration_date = expiration_dates[0]
        
        self.logger.info(f"Fetching option data for {ticker} with expiration date {expiration_date}")
        options = stock.option_chain(expiration_date)
        return options.calls, options.puts, expiration_date


    def preprocess_data(self, stock_data, calls, puts, expiration_date):
        """Preprocess stock and option data for analysis."""
        self.logger.info("Starting data preprocessing")

        try:
            # Preprocess stock data
            stock_data['Returns'] = np.log(stock_data['Adj Close'] / stock_data['Adj Close'].shift(1))
            stock_data['Volatility'] = stock_data['Returns'].rolling(window=252).std() * np.sqrt(252)
            
            # Handle NaN values in volatility
            if stock_data['Volatility'].isna().all():
                self.logger.warning("Not enough data to calculate volatility. Using a default value of 0.2")
                stock_data['Volatility'] = 0.2
            else:
                stock_data['Volatility'] = stock_data['Volatility'].fillna(method='ffill')
            
            # Debug information for calls and puts
            self.logger.info(f"Calls type: {type(calls)}")
            self.logger.info(f"Puts type: {type(puts)}")
            self.logger.info(f"Calls shape: {calls.shape if hasattr(calls, 'shape') else 'N/A'}")
            self.logger.info(f"Puts shape: {puts.shape if hasattr(puts, 'shape') else 'N/A'}")
            self.logger.info(f"Calls columns: {calls.columns.tolist() if hasattr(calls, 'columns') else 'N/A'}")
            self.logger.info(f"Puts columns: {puts.columns.tolist() if hasattr(puts, 'columns') else 'N/A'}")

            # Combine calls and puts
            calls['optionType'] = 'call'
            puts['optionType'] = 'put'
            options = pd.concat([calls, puts], ignore_index=True)
            
            self.logger.info(f"Successfully combined options. Shape: {options.shape}")
            self.logger.info(f"Combined options columns: {options.columns.tolist()}")

            # Log information about options
            self.logger.info(f"Number of call options: {len(calls)}")
            self.logger.info(f"Number of put options: {len(puts)}")
            self.logger.info(f"Total number of options: {len(options)}")
            
            if not options.empty and 'strike' in options.columns:
                self.logger.info(f"Strike price range: {options['strike'].min()} to {options['strike'].max()}")
            else:
                self.logger.warning("No strike price data available in options")
            
            self.logger.info(f"Expiration date: {expiration_date}")
            
            # Calculate time to expiration in years
            current_date = datetime.now(timezone.utc).date()
            expiration_date = pd.to_datetime(expiration_date).date()
            options['TimeToExpiration'] = max((expiration_date - current_date).days / 365, 0)

            # Merge stock data with options data
            latest_stock_price = stock_data['Adj Close'].iloc[-1]
            options['UnderlyingPrice'] = latest_stock_price
            
            if 'impliedVolatility' in options.columns:
                options['ImpliedVolatility'] = options['impliedVolatility']
            else:
                self.logger.warning("Implied volatility data not available in options data")
                options['ImpliedVolatility'] = np.nan
            
            self.logger.info("Data preprocessing completed successfully")
            return stock_data, options

        except Exception as e:
            self.logger.error(f"Error in data preprocessing: {str(e)}", exc_info=True)
            raise

    def filter_options(self, options, moneyness_range=(0.8, 1.2)):
        """Filter options based on moneyness."""
        try:
            options['Moneyness'] = options['UnderlyingPrice'] / options['strike']
            filtered_options = options[(options['Moneyness'] >= moneyness_range[0]) & (options['Moneyness'] <= moneyness_range[1])].copy()
            
            if filtered_options.empty:
                self.logger.warning(f"No options found within moneyness range {moneyness_range}")
                self.logger.info(f"Moneyness range in data: {options['Moneyness'].min()} to {options['Moneyness'].max()}")
                
                # Expand the range if no options are found
                expanded_range = (options['Moneyness'].min(), options['Moneyness'].max())
                filtered_options = options.copy()
                self.logger.info(f"Expanded moneyness range to {expanded_range}")
            
            return filtered_options
        except Exception as e:
            self.logger.error(f"Error in filtering options: {str(e)}", exc_info=True)
            raise