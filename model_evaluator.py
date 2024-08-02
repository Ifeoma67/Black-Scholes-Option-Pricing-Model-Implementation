import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import logging

class ModelEvaluator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_metrics(self, y_true, y_pred):
        """Calculate evaluation metrics for the model."""
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        
        self.logger.info(f"Model Evaluation Metrics: MAE={mae:.4f}, MSE={mse:.4f}, RMSE={rmse:.4f}, R2={r2:.4f}")
        
        return {'MAE': mae, 'MSE': mse, 'RMSE': rmse, 'R2': r2}

    def plot_predicted_vs_actual(self, y_true, y_pred):
        """Plot predicted vs actual option prices."""
        plt.figure(figsize=(10, 6))
        plt.scatter(y_true, y_pred, alpha=0.5)
        plt.plot([min(y_true), max(y_true)], [min(y_true), max(y_true)], 'r--', lw=2)
        plt.xlabel('Market Price')
        plt.ylabel('Model Price')
        plt.title('Predicted vs Actual Option Prices')
        plt.savefig('predicted_vs_actual.png')
        plt.close()
        
        self.logger.info("Predicted vs Actual plot saved as 'predicted_vs_actual.png'")

    def analyze_performance_by_strike(self, options):
        """Analyze model performance across different strike prices."""
        options['PriceDiff'] = options['ModelPrice'] - options['lastPrice']
        options['PriceDiffPct'] = options['PriceDiff'] / options['lastPrice']

        plt.figure(figsize=(10, 6))
        plt.scatter(options['strike'], options['PriceDiffPct'])
        plt.xlabel('Strike Price')
        plt.ylabel('Price Difference (%)')
        plt.title('Model Performance Across Strike Prices')
        plt.savefig('performance_by_strike.png')
        plt.close()

        self.logger.info("Performance by strike plot saved as 'performance_by_strike.png'")

    def analyze_performance_by_expiration(self, options):
        """Analyze model performance across different expiration dates."""
        plt.figure(figsize=(10, 6))
        plt.scatter(options['TimeToExpiration'], options['PriceDiffPct'])
        plt.xlabel('Time to Expiration (Years)')
        plt.ylabel('Price Difference (%)')
        plt.title('Model Performance Across Expiration Dates')
        plt.savefig('performance_by_expiration.png')
        plt.close()

        self.logger.info("Performance by expiration plot saved as 'performance_by_expiration.png'")