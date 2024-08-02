import logging
import time
from functools import wraps

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename='black_scholes_analysis.log')

def retry_on_exception(max_attempts, delay):
    """Decorator to retry a function on exception."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    logging.warning(f"Attempt {attempts} failed. Retrying in {delay} seconds. Error: {str(e)}")
                    time.sleep(delay)
        return wrapper
    return decorator