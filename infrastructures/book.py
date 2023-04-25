# %%
from option import *
import yfinance as yf
class book():
    def __init__(self, start_date, end_date):
        self.holding: dict = {'STOCK': {},
                              'OPTIONS': {}}
        self.start_date = start_date
        self.end_date = end_date

    def create_holding(self, type: str, ticker: str, amount: int):
        if type == 'STOCK':
            self.holding[type][ticker] = {'Amount': amount}
        elif type == 'OPTIONS':
            self.holding[type][ticker] = {'Amount': amount}
    
    def modify_holding(self, type: str, ticker: str, amount: int):
        if type == 'STOCK':
            self.holding[type][ticker]['Amount'] += amount

    def initializing(self):
        self.df_stocks = pd.DataFrame()
        self.df_options = pd.DataFrame()
        self.df_options_theoretical = pd.DataFrame()
        self.options: dict = {}
        for ticker in self.holding['STOCK'].keys():
            df = yf.download(ticker, start= self.start_date, end= self.end_date, progress=False)['Adj Close']
            ticker_col = pd.Series(ticker, index = df.index)
            df = pd.concat([ticker_col, df], axis=1)
            self.df_stocks = pd.concat([self.df_stocks, df])
        for ticker in self.holding['OPTIONS'].keys():
            self.options[ticker] = option(ticker, self.start_date, self.end_date)
            df = yf.download(ticker, start= self.start_date, end= self.end_date, progress=False)['Adj Close']
            ticker_col = pd.Series(ticker, index = df.index)
            df = pd.concat([ticker_col, df], axis=1)
            self.df_options = pd.concat([self.df_options, df])
            df = self.options[ticker].theoretical_prices
            df = pd.concat([ticker_col, df], axis=1)
            self.df_options_theoretical = pd.concat([self.df_options_theoretical, df])

    def get_portfolio_value(self):
        self.df_portfolio_value = pd.DataFrame()
        # Get the total value of all stocks and options
        for ticker in self.holding['STOCK'].keys():
            self.df_portfolio_value[ticker] = self.df_stocks[self.df_stocks[0] == ticker]['Adj Close'] * self.holding['STOCK'][ticker]['Amount']
        for ticker in self.holding['OPTIONS'].keys():
            self.df_portfolio_value[ticker] = self.df_options[self.df_options[0] == ticker]['Adj Close'] * self.holding['OPTIONS'][ticker]['Amount']
        # Get the total value of the portfolio
        self.df_portfolio_value['Total'] = self.df_portfolio_value.sum(axis=1)

    def get_theoretic_value(self):
        self.df_theoretic_value = pd.DataFrame()
        # Get the total value of all stocks and options
        for ticker in self.holding['STOCK'].keys():
            self.df_theoretic_value[ticker] = self.df_stocks[self.df_stocks[0] == ticker]['Adj Close'] * self.holding['STOCK'][ticker]['Amount']
        for ticker in self.holding['OPTIONS'].keys():
            self.df_theoretic_value[ticker] = self.df_options_theoretical[self.df_options_theoretical[0] == ticker][1] * self.holding['OPTIONS'][ticker]['Amount']
        # Get the total value of the portfolio
        self.df_theoretic_value['Total'] = self.df_theoretic_value.sum(axis=1)

    def get_portfolio_greeks(self):
        # self.options stores the greek values in .delta, .gamma, .theta, .vega, .rho
        # Get the total greek values of all assets, including stocks and options
        self.df_portfolio_delta = pd.DataFrame()
        for ticker in self.holding['STOCK'].keys():
            self.df_portfolio_delta[ticker] = 1 * self.holding['STOCK'][ticker]['Amount']
        for ticker in self.holding['OPTIONS'].keys():
            self.df_portfolio_delta[ticker] = self.options[ticker].delta * self.holding['OPTIONS'][ticker]['Amount']
        self.df_portfolio_delta['Total'] = self.df_portfolio_delta.sum(axis=1)
        self.df_portfolio_gamma = pd.DataFrame()
        for ticker in self.holding['STOCK'].keys():
            self.df_portfolio_gamma[ticker] = 0 * self.holding['STOCK'][ticker]['Amount']
        for ticker in self.holding['OPTIONS'].keys():
            self.df_portfolio_gamma[ticker] = self.options[ticker].gamma * self.holding['OPTIONS'][ticker]['Amount']
        self.df_portfolio_gamma['Total'] = self.df_portfolio_gamma.sum(axis=1)
        self.df_portfolio_theta = pd.DataFrame()
        for ticker in self.holding['STOCK'].keys():
            self.df_portfolio_theta[ticker] = 0 * self.holding['STOCK'][ticker]['Amount']
        for ticker in self.holding['OPTIONS'].keys():
            self.df_portfolio_theta[ticker] = self.options[ticker].theta * self.holding['OPTIONS'][ticker]['Amount']
        self.df_portfolio_theta['Total'] = self.df_portfolio_theta.sum(axis=1)
        self.df_portfolio_vega = pd.DataFrame()
        for ticker in self.holding['STOCK'].keys():
            self.df_portfolio_vega[ticker] = 0 * self.holding['STOCK'][ticker]['Amount']
        for ticker in self.holding['OPTIONS'].keys():
            self.df_portfolio_vega[ticker] = self.options[ticker].vega * self.holding['OPTIONS'][ticker]['Amount']
        self.df_portfolio_vega['Total'] = self.df_portfolio_vega.sum(axis=1)
        self.df_portfolio_rho = pd.DataFrame()
        for ticker in self.holding['STOCK'].keys():
            self.df_portfolio_rho[ticker] = 0 * self.holding['STOCK'][ticker]['Amount']
        for ticker in self.holding['OPTIONS'].keys():
            self.df_portfolio_rho[ticker] = self.options[ticker].rho * self.holding['OPTIONS'][ticker]['Amount']
        self.df_portfolio_rho['Total'] = self.df_portfolio_rho.sum(axis=1)
        