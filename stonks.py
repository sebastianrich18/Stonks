"""

things to do:
    Save time and purchise price of stock
    OAUTH?

"""

import requests
import json
import time
from secret import apikey

class Account:
    def __init__(self, json, cash=None):
        if cash == None:
            self.name = json.get('name')
            self.cash = json.get('cash')
            self.positions = json.get('positions')
        else:
            self.name = json
            self.cash = cash

    def __str__(self):
        string = "Name: " + self.name + "\n"
        string = "Value: $" + str(self.getValue()) + "\n"
        string += "Cash: $" + str(self.cash) + "\n"
        string += "Postions: \n"
        for x in self.positions:
            string += "\t" + str(x[1]) + " shares of " + x[0] + " worth $" + str(getPrice(x[0]) * x[1]) + "\n"
        return string

    @staticmethod
    def getAccount():
        with open('account.json') as f:
            data = json.load(f)
        return data

    def saveAccount(self):
        obj = {
            "name": self.name,
            "cash": self.cash,
            "positions": self.positions
        }

        with open('account.json', 'w') as f:
            json.dump(obj, f)

    def getValue(self):
        total = self.cash
        for p in self.positions:
            total += getPrice(p[0]) * p[1]
        return total

    def buy(self, ticker, shares):
        price = getPrice(ticker) * shares
        tickers = []
        for x in self.positions:
            tickers.append(x[0])

        if(self.cash >= price):
            if ticker not in tickers:
                self.cash -= price
                self.positions.append([ticker, shares, price / shares, int(time.time())])
            else:
                self.cash -= price
                i = 0
                for t in tickers:
                    if ticker == t:
                        self.positions[i][1] += shares
                        break
                    i += 1
            
            self.saveAccount()
            print(ticker, "Order placed for $", price)
        else:
            print("Order costs $", price, " you only have $", self.cash)

    def sell(self, ticker, shares):
        price = getPrice(ticker) * shares
        tickers = []
        for x in self.positions:
            tickers.append(x[0])
        i = 0
        for x in tickers:

            if(ticker == x):
                if self.positions[i][1] - shares > 0:
                    self.positions[i][1] -= shares
                    self.cash += price

                elif self.positions[i][1] - shares == 0:
                    self.positions.remove(self.positions[i])
                    self.cash += price

                elif self.positions[i][1] - shares < 0:
                    print("You only hold ", self.positions[i][1], "shares")
                    break
            
                self.saveAccount()
                print("Sold", ticker, "for", price)
                break
            i += 1

    def getPL(self):
        pl=[]
        for i in range(len(self.positions)):
            pruchPrice = self.positions[i][2]
            mktPrice = getPrice(self.positions[i][0])
            pl.append((mktPrice - pruchPrice) * self.positions[i][1])
        return pl

priceCache = {}
def getPrice(ticker):
    if ticker not in priceCache.keys():
        url = "https://api.tdameritrade.com/v1/marketdata/" + ticker + "/quotes"
        params = {"apikey": apikey}
        print("making api call")
        response = requests.get(url + "?apikey=" + apikey)
        price = json.loads(response.text).get(ticker).get('lastPrice')
        priceCache[ticker] = price
        return price
    else:
        return priceCache[ticker]


account = Account(Account.getAccount())
print(account.getPL())