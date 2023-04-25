import numpy as np
from datetime import datetime
import pandas as pd
from py_vollib.black_scholes import black_scholes as bs
from py_vollib.black_scholes.greeks.analytical import delta, gamma, theta, vega, rho

import yfinance as yf

class option():
    def __init__(self, option: str, start_date: datetime, end_date: datetime, risk_free_rate: float = 0.04):
        self.option = option
        self.ticker, self.expiration_date, self.type, self.strike_price = self.get_option_params()
        self.risk_free_rate = risk_free_rate
        self.df = yf.download(self.ticker, start= start_date, end= end_date, progress=False)
        self.df['log_return'] = np.log(self.df['Close'] / self.df['Close'].shift(1))
        self.df['volatility'] = self.df['log_return'].rolling(21).std() * np.sqrt(252)
        self.get_option_prices()
        self.get_option_greeks()

    def get_option_params(self):
        """
        @description Get the option parameters from the string
        
        @params:
            option: str
                The option string in the format of 'TSLA250620C00180000'
                The characters before the first number are the ticker
                The next 6 characters are the expiration date
                The next 1 letter is the type
                The rest of the characters are the strike price
        
        @return:
            ticker: str
                The ticker of the option
            expiration_date: datetime
                The expiration date of the option
            type: str
                The type of the option
            strike_price: float
                The strike price of the option
        """
        ticker = ''
        expiration_date = ''
        type = ''
        strike_price = ''
        for i in range(len(self.option)):
            if self.option[i].isdigit():
                expiration_date = self.option[i:i+6]
                type = self.option[i+6]
                strike_price = self.option[i+7:]
                break
            else:
                ticker += self.option[i]
        # Extract the strike price and add the decimal point to the strike price
        strike_price = strike_price[:-3] + '.' + strike_price[-2:]
        # Convert the expiration date to datetime
        expiration_date = datetime.strptime(expiration_date, '%y%m%d')
        # Convert the strike price to float
        strike_price = float(strike_price)
        # Convert the type to lower case
        type = type.lower()
        return ticker, expiration_date, type, strike_price

    def get_option_prices(self):
        """
        @description Get the option price

        @params:
            df: dataframe
                The dataframe with index Date and columns Adj Close, Log Return, and Volatility
            type: str
                The type of the option
            strike_price: float
                The strike price of the option
            risk_free_rate: float
                The risk free rate
        
        @return
            option_price: pd.Series
                The option price on each day
        """
        # Compute the option price
        def func(row):
            # if no nan value in the row
            if not row.isnull().values.any():
                # Compute the time to maturity
                time_to_maturity = (self.expiration_date - row.name).days / 365
                # Compute the option price
                option_price = bs(self.type, row['Adj Close'], self.strike_price, time_to_maturity, self.risk_free_rate, row['volatility'])
                return option_price
            else:
                return np.nan
        # Compute the option price
        self.theoretical_prices = self.df.apply(func, axis=1)

    def get_option_greeks(self):
        """
        @decription Get the option greeks

        @params:
            df: dataframe
                The dataframe with index Date and columns Adj Close, Log Return, and Volatility
            type: str
                The type of the option
            strike_price: float
                The strike price of the option
            risk_free_rate: float
                The risk free rate
        
        @return
            delta: pd.Series
                The delta of the option on each day
            gamma: pd.Series
                The gamma of the option on each day
            theta: pd.Series
                The theta of the option on each day
            vega: pd.Series
                The vega of the option on each day
            rho: pd.Series 
                The rho of the option on each day
        """
        # Compute the option greeks
        def func(row):
            # if no nan value in the row
            if not row.isnull().values.any():
                # Compute the time to maturity
                time_to_maturity = (self.expiration_date - row.name).days / 365
                # Compute the option greeks
                option_delta = delta(self.type, row.loc['Adj Close'], self.strike_price, self.risk_free_rate, time_to_maturity, row.volatility)
                option_gamma = gamma(self.type, row.loc['Adj Close'], self.strike_price, self.risk_free_rate, time_to_maturity, row.volatility)
                option_theta = theta(self.type, row.loc['Adj Close'], self.strike_price, self.risk_free_rate, time_to_maturity, row.volatility)
                option_vega = vega(self.type, row.loc['Adj Close'], self.strike_price, self.risk_free_rate, time_to_maturity, row.volatility)
                option_rho = rho(self.type, row.loc['Adj Close'], self.strike_price, self.risk_free_rate, time_to_maturity, row.volatility)
                greeks = pd.Series([option_delta, option_gamma, option_theta, option_vega, option_rho], index=['delta', 'gamma', 'theta', 'vega', 'rho'])
                return greeks
            else:
                return np.nan
        greeks = self.df.apply(func, axis=1)
        self.delta = greeks.apply(lambda x: x['delta'] if type(x) == pd.Series else None)
        self.gamma = greeks.apply(lambda x: x['gamma'] if type(x) == pd.Series else None)
        self.theta = greeks.apply(lambda x: x['theta'] if type(x) == pd.Series else None)
        self.vega = greeks.apply(lambda x: x['vega'] if type(x) == pd.Series else None)
        self.rho = greeks.apply(lambda x: x['rho'] if type(x) == pd.Series else None)
        