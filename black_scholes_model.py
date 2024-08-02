import numpy as np
from scipy.stats import norm
import logging

class BlackScholesModel:
    """
    A class to implement the Black-Scholes option pricing model.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def d1(self, S, K, T, r, sigma):
        """Calculate d1 parameter for Black-Scholes formula."""
        return (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))

    def d2(self, S, K, T, r, sigma):
        """Calculate d2 parameter for Black-Scholes formula."""
        return self.d1(S, K, T, r, sigma) - sigma*np.sqrt(T)

    def call_price(self, S, K, T, r, sigma):
        """Calculate the price of a European call option."""
        d1 = self.d1(S, K, T, r, sigma)
        d2 = self.d2(S, K, T, r, sigma)
        return S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)

    def put_price(self, S, K, T, r, sigma):
        """Calculate the price of a European put option."""
        d1 = self.d1(S, K, T, r, sigma)
        d2 = self.d2(S, K, T, r, sigma)
        return K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)

    def delta(self, S, K, T, r, sigma, option_type='call'):
        """
        Calculate the Delta of an option.
        
        Delta measures the rate of change in the option price with respect to the change in the underlying asset's price.
        """
        d1 = self.d1(S, K, T, r, sigma)
        if option_type.lower() == 'call':
            return norm.cdf(d1)
        elif option_type.lower() == 'put':
            return norm.cdf(d1) - 1
        else:
            raise ValueError("option_type must be 'call' or 'put'")

    def gamma(self, S, K, T, r, sigma):
        """
        Calculate the Gamma of an option.
        
        Gamma measures the rate of change in Delta with respect to the change in the underlying asset's price.
        """
        d1 = self.d1(S, K, T, r, sigma)
        return norm.pdf(d1) / (S * sigma * np.sqrt(T))

    def vega(self, S, K, T, r, sigma):
        """
        Calculate the Vega of an option.
        
        Vega measures sensitivity to volatility.
        """
        d1 = self.d1(S, K, T, r, sigma)
        return S * norm.pdf(d1) * np.sqrt(T)

    def theta(self, S, K, T, r, sigma, option_type='call'):
        """
        Calculate the Theta of an option.
        
        Theta measures the sensitivity of the option price to the passage of time.
        """
        d1 = self.d1(S, K, T, r, sigma)
        d2 = self.d2(S, K, T, r, sigma)
        common_term = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
        
        if option_type.lower() == 'call':
            return common_term - r * K * np.exp(-r * T) * norm.cdf(d2)
        elif option_type.lower() == 'put':
            return common_term + r * K * np.exp(-r * T) * norm.cdf(-d2)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

    def rho(self, S, K, T, r, sigma, option_type='call'):
        """
        Calculate the Rho of an option.
        
        Rho measures sensitivity to the interest rate.
        """
        d2 = self.d2(S, K, T, r, sigma)
        if option_type.lower() == 'call':
            return K * T * np.exp(-r * T) * norm.cdf(d2)
        elif option_type.lower() == 'put':
            return -K * T * np.exp(-r * T) * norm.cdf(-d2)
        else:
            raise ValueError("option_type must be 'call' or 'put'")