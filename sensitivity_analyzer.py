import numpy as np
import matplotlib.pyplot as plt
import logging

class SensitivityAnalyzer:
    def __init__(self, model):
        self.model = model
        self.logger = logging.getLogger(__name__)

    def parameter_sensitivity(self, param, base_value, range_pct, steps, **kwargs):
        param_range = np.linspace(base_value * (1 - range_pct), 
                                  base_value * (1 + range_pct), 
                                  steps)
        prices = [self.model.call_price(**{**kwargs, param: value}) for value in param_range]
        
        plt.figure(figsize=(10, 6))
        plt.plot(param_range, prices)
        plt.title(f'Sensitivity to {param}')
        plt.xlabel(param)
        plt.ylabel('Option Price')
        plt.grid(True)
        plt.savefig(f'sensitivity_{param}.png')
        plt.close()
        
        self.logger.info(f"Sensitivity analysis for {param} saved as 'sensitivity_{param}.png'")

    def plot_greeks(self, S, K, T, r, sigma):
        S_range = np.linspace(0.5 * K, 1.5 * K, 100)
        
        deltas = [self.model.delta(s, K, T, r, sigma) for s in S_range]
        gammas = [self.model.gamma(s, K, T, r, sigma) for s in S_range]
        vegas = [self.model.vega(s, K, T, r, sigma) for s in S_range]
        thetas = [self.model.theta(s, K, T, r, sigma) for s in S_range]
        rhos = [self.model.rho(s, K, T, r, sigma) for s in S_range]
        
        plt.figure(figsize=(15, 10))
        plt.subplot(2, 3, 1)
        plt.plot(S_range, deltas)
        plt.title('Delta')
        plt.subplot(2, 3, 2)
        plt.plot(S_range, gammas)
        plt.title('Gamma')
        plt.subplot(2, 3, 3)
        plt.plot(S_range, vegas)
        plt.title('Vega')
        plt.subplot(2, 3, 4)
        plt.plot(S_range, thetas)
        plt.title('Theta')
        plt.subplot(2, 3, 5)
        plt.plot(S_range, rhos)
        plt.title('Rho')
        plt.tight_layout()
        plt.savefig('greeks.png')
        plt.close()
        
        self.logger.info("Greeks plot saved as 'greeks.png'")