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

        # Fetch and preprocess data
        stock_data = data_processor.fetch_stock_data(CONFIG['TICKER'], CONFIG['START_DATE'], CONFIG['END_DATE'])
        calls, puts, expiration_date = data_processor.fetch_option_data(CONFIG['TICKER'])
        
        logger.info(f"Calls data shape: {calls.shape}")
        logger.info(f"Puts data shape: {puts.shape}")
        logger.info(f"Calls columns: {calls.columns.tolist()}")
        logger.info(f"Puts columns: {puts.columns.tolist()}")
        
        if calls.empty or puts.empty:
            logger.error("No options data available. Exiting.")
            return
        
        stock_data, options = data_processor.preprocess_data(stock_data, calls, puts, expiration_date)

        # Log more information about the data
        logger.info(f"Number of options before filtering: {len(options)}")
        logger.info(f"Option types: {options['optionType'].value_counts().to_dict()}")
        logger.info(f"Options columns: {options.columns.tolist()}")

        # Set up parameters
        S = stock_data['Adj Close'].iloc[-1]
        r = CONFIG['RISK_FREE_RATE']
        sigma = stock_data['Volatility'].iloc[-1]

        logger.info(f"Stock price: {S:.2f}, Risk-free rate: {r:.2f}, Volatility: {sigma:.2f}")

        # Filter options
        filtered_options = data_processor.filter_options(options)
        
        logger.info(f"Number of options after filtering: {len(filtered_options)}")

        if filtered_options.empty:
            logger.warning("No valid options data after filtering. Check your data and parameters.")
            return
            
        # Calculate model prices
        filtered_options['ModelPrice'] = filtered_options.apply(
            lambda row: bs_model.call_price(S, row['strike'], row['TimeToExpiration'], r, sigma) 
            if row['optionType'] == 'call' 
            else bs_model.put_price(S, row['strike'], row['TimeToExpiration'], r, sigma),
            axis=1
        )

        # Log some information about the calculated prices
        logger.info(f"Model price statistics: {filtered_options['ModelPrice'].describe()}")
        logger.info(f"Number of NaN model prices: {filtered_options['ModelPrice'].isna().sum()}")

        # Remove rows with NaN model prices
        valid_options = filtered_options.dropna(subset=['ModelPrice'])

        # Remove rows with NaN model prices
        valid_options = filtered_options.dropna(subset=['ModelPrice'])
        
        logger.info(f"Number of options with valid model prices: {len(valid_options)}")

        if valid_options.empty:
            logger.warning("No valid options data after calculating model prices. Check your parameters.")
            return

        # Evaluate model
        market_prices = valid_options['lastPrice']
        model_prices = valid_options['ModelPrice']
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
        logger.error(f"An error occurred: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()