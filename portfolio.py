#Burak Yesil
import pandas as pd
import pandas_datareader as pdr
import datetime as dt
import math

class Portfolio:

    def __init__(self, shares, start, end):
        self.shares = shares
        self.start = start
        self.end = end
        self.tickers = list(shares.keys())

        self.Average_return = 0.0 #default value will be changed in semiDeviation function
        self.Portfolio_Values = []
        self.semi_deviation = None
        self.max_value = 0.0 #default value will be changed in semiDeviation function
        self.min_value = 0.0 #default value will be changed in semiDeviation function
        self.daily_price_changes = None
        self.total_daily_portfolio_values = []
        self.pct_change = None

    def semiDeviation(self):
        '''This function calculates the semi deviation of the portfolio. It starts off by doing an
        API request to retrieve the price history data of each of the different stocks, adds the
        weights of each stock ticker, and combines all the daily values to calculate the daily values
        of the entire portfolio. Next, it calculates the percent change of the portfolio value between 
        each trading day. Next, the mean of the percent change is taken to calculate the average return,
        which is used to calculate the Deviations (percent change - average change). Then we get the sum of
        each negative deviations squared and divde it by the total number of both positive and negative deviations,
        giving us the semi variance. Finally, we take the square root of the semi variance to get the semi deviation
        and return that value.
        '''

        if (self.semi_deviation != None):
            return self.semi_deviation


        for key in self.shares.items():
            for ticker in self.shares.keys():
                #Adding weights to prices
                self.close_prices = list(pdr.DataReader(ticker, "yahoo", self.start, self.end)["Adj Close"])
                self.close_price_weighted = list(map(lambda x: x * self.shares[ticker] , self.close_prices))
                
                #Adding weighted daily prices to total value list
                for i in range(len(self.close_price_weighted)):
                    self.total_daily_portfolio_values.append(0)
                    self.total_daily_portfolio_values[i] += self.close_price_weighted[i]


        #Calculating percent change or return
        self.total_daily_portfolio_values = [i for i in self.total_daily_portfolio_values if i != 0] #used to remove 0s caused by API error
        self.total_daily_portfolio_values_series = pd.Series(self.total_daily_portfolio_values)
        self.pct_change = self.total_daily_portfolio_values_series.pct_change()  

        #Also, storing daily value changes for portfolio
        self.daily_price_changes = self.total_daily_portfolio_values_series.diff().dropna()

        #Calculating the average return
        self.Average_return = self.pct_change.mean()

        #Calculating deviations squared and semi-variance

        self.Deviations = list(map(lambda x: x -  self.Average_return, self.pct_change))
        self.Deviations_size = len(self.Deviations)
        self.Negative_Deviations = list(filter(lambda x: x<0, self.Deviations))
        self.Negative_Deviations_Squared = list(map(lambda x: x**2, self.Negative_Deviations))
        
        self.Semi_Variance = sum(self.Negative_Deviations_Squared)/self.Deviations_size
        self.Semi_Deviation = math.sqrt(self.Semi_Variance)

        return self.Semi_Deviation
        




    def monthlyVolatility(self):
        '''Calculates how wildly the value of the portfolio goes up and down.'''
        self.total_daily_portfolio_values = []

        for key in self.shares.items():
            for ticker in self.shares.keys():
                #Adding weights to prices
                self.close_prices = list(pdr.DataReader(ticker, "yahoo", self.start, self.end)["Adj Close"])
                self.close_price_weighted = list(map(lambda x: x * self.shares[ticker] , self.close_prices))
                
                #Adding weighted daily prices to total value list
                for i in range(len(self.close_price_weighted)):
                    self.total_daily_portfolio_values.append(0)
                    self.total_daily_portfolio_values[i] += self.close_price_weighted[i]


        #Calculating percent change or return
        self.total_daily_portfolio_values = [i for i in self.total_daily_portfolio_values if i != 0]
        self.total_daily_portfolio_values_series = pd.Series(self.total_daily_portfolio_values)
    
        self.pct_change = self.total_daily_portfolio_values_series.pct_change()

        return self.pct_change.std()*math.sqrt(21)
    



    def var(self):
        """semiDeviation function is called to set the daily_price_changes variables
         value and stores the semideviation result in global variable to provide quick solutions
        for future semiDeviation function calls. (Memoization)"""

        self.semiDeviation() 
        return self.daily_price_changes.quantile(.05)




    def sortinoRatio(self):
        """The Sortino ratio measures the risk-adjusted return of the portfolio."""
        #Calculating the average return
        self.downside_deviation = self.semiDeviation() #returns downside_deviation and updates the value of Average_return
        self.risk_free_rate = .05 #three month treasury rate

        Sortino_ratio = (self.Average_return - self.risk_free_rate)/self.downside_deviation
        return Sortino_ratio


    def maxDrawDown(self):
        self.semiDeviation()
        self.max_price_drop = self.daily_price_changes.min()
        self.prior_value = self.total_daily_portfolio_values[(self.daily_price_changes.idxmin())-1]
        return (self.max_price_drop/self.prior_value)

        