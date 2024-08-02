import logging
from black_scholes_model import BlackScholesModel
from data_processor import DataProcessor
from model_evaluator import ModelEvaluator
from sensitivity_analyzer import SensitivityAnalyzer
from utils import setup_logging
from config import CONFIG
from ethical_considerations import ethical_check, log_ethical_considerations

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting Black-Scholes model analysis")
        
        ethical_check()
        
        bs_model = BlackScholesModel()
        data_processor = DataProcessor()
        model_evaluator = ModelEvaluator()
        sensitivity_analyzer = SensitivityAnalyzer(bs_model)

        # Fetch data
        stock_data = data_processor.fetch_stock_data(CONFIG['TICKER'], CONFIG['START_DATE'], CONFIG['END_DATE'])
        calls, puts, expiration_date = data_processor.fetch_option_data(CONFIG['TICKER'])
        
        # Preprocess data
        stock_data, options = data_processor.preprocess_data(stock_data, calls, puts, expiration_date)
        
        # Filter options based on moneyness
        filtered_options = data_processor.filter_options(options)

        # Set up parameters
        S = stock_data['Adj Close'].iloc[-1]
        r = CONFIG['RISK_FREE_RATE']
        sigma = stock_data['Volatility'].iloc[-1]

        logger.info(f"Stock price: {S:.2f}, Risk-free rate: {r:.2f}, Volatility: {sigma:.2f}")

        # Calculate model prices
        filtered_options['ModelPrice'] = filtered_options.apply(
            lambda row: bs_model.call_price(S, row['strike'], row['TimeToExpiration'], r, sigma) 
            if row['optionType'] == 'call' 
            else bs_model.put_price(S, row['strike'], row['TimeToExpiration'], r, sigma),
            axis=1
        )

        # Evaluate model
        market_prices = filtered_options['lastPrice']
        model_prices = filtered_options['ModelPrice']
        metrics = model_evaluator.calculate_metrics(market_prices, model_prices)
        logger.info(f"Model Evaluation Metrics: {metrics}")

        # Plot results
        model_evaluator.plot_predicted_vs_actual(market_prices, model_prices)

        # Analyze model performance across different strikes and expiration dates
        model_evaluator.analyze_performance_by_strike(filtered_options)
        model_evaluator.analyze_performance_by_expiration(filtered_options)

        # Sensitivity analysis
        for option in filtered_options.iloc[:5].itertuples():  # Analyze first 5 options
            sensitivity_analyzer.parameter_sensitivity('S', S, 0.2, 100, K=option.strike, T=option.TimeToExpiration, r=r, sigma=sigma)
            sensitivity_analyzer.plot_greeks(S, option.strike, option.TimeToExpiration, r, sigma)

        log_ethical_considerations()

        logger.info("Black-Scholes model analysis completed successfully")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()