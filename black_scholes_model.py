import numpy as np
from scipy.stats import norm
import logging

class BlackScholesModel:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def d1(self, S, K, T, r, sigma):
        return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    def d2(self, S, K, T, r, sigma):
        return self.d1(S, K, T, r, sigma) - sigma * np.sqrt(T)

    def call_price(self, S, K, T, r, sigma):
        self.logger.debug(f"Calculating call price: S={S}, K={K}, T={T}, r={r}, sigma={sigma}")
        if np.isnan(sigma) or sigma <= 0 or T < 0:
            self.logger.warning(f"Invalid input for call price: sigma={sigma}, T={T}")
            return np.nan
        if T == 0:
            return max(S - K, 0)  # Intrinsic value at expiration
        d1 = self.d1(S, K, T, r, sigma)
        d2 = self.d2(S, K, T, r, sigma)
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        self.logger.debug(f"Calculated call price: {price}")
        return price

    def put_price(self, S, K, T, r, sigma):
        self.logger.debug(f"Calculating put price: S={S}, K={K}, T={T}, r={r}, sigma={sigma}")
        if np.isnan(sigma) or sigma <= 0 or T < 0:
            self.logger.warning(f"Invalid input for put price: sigma={sigma}, T={T}")
            return np.nan
        if T == 0:
            return max(K - S, 0)  # Intrinsic value at expiration
        d1 = self.d1(S, K, T, r, sigma)
        d2 = self.d2(S, K, T, r, sigma)
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        self.logger.debug(f"Calculated put price: {price}")
        return price

    def delta(self, S, K, T, r, sigma, option_type='call'):
        if T == 0:
            return 1 if S > K else 0 if S < K else 0.5
        d1 = self.d1(S, K, T, r, sigma)
        if option_type == 'call':
            return norm.cdf(d1)
        elif option_type == 'put':
            return norm.cdf(d1) - 1
        else:
            raise ValueError("option_type must be 'call' or 'put'")

    def gamma(self, S, K, T, r, sigma):
        if T == 0:
            return 0
        d1 = self.d1(S, K, T, r, sigma)
        return norm.pdf(d1) / (S * sigma * np.sqrt(T))

    def vega(self, S, K, T, r, sigma):
        if T == 0:
            return 0
        d1 = self.d1(S, K, T, r, sigma)
        return S * norm.pdf(d1) * np.sqrt(T)

    def theta(self, S, K, T, r, sigma, option_type='call'):
        if T == 0:
            return 0
        d1 = self.d1(S, K, T, r, sigma)
        d2 = self.d2(S, K, T, r, sigma)
        common_term = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
        if option_type == 'call':
            return common_term - r * K * np.exp(-r * T) * norm.cdf(d2)
        elif option_type == 'put':
            return common_term + r * K * np.exp(-r * T) * norm.cdf(-d2)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

    def rho(self, S, K, T, r, sigma, option_type='call'):
        if T == 0:
            return 0
        d2 = self.d2(S, K, T, r, sigma)
        if option_type == 'call':
            return K * T * np.exp(-r * T) * norm.cdf(d2)
        elif option_type == 'put':
            return -K * T * np.exp(-r * T) * norm.cdf(-d2)
        else:
            raise ValueError("option_type must be 'call' or 'put'")