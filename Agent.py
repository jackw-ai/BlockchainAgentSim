import random

import numpy as np

from abc import ABC, abstractmethod

TYPES = ['S', 'A', 'M']

class Agent(ABC):
    ''' abstract agent class '''

    def __init__(self):
        super().__init__()
        self.capital = random.randint(1000, 1000000)
        self.bitcoins = 0

    @abstractmethod
    def make_transactions(self, price):
        '''
        returns transaction if there is one for the agent of form
        [0/1, (price, quantity)]

        0 == buy, 1 == sell
        '''
        pass

    def tx_price(self, market_price):
        ''' returns transaction price given market price (added noise to pricing) '''
        pass

    def coins_to_capital(self, q, p):
        ''' turns capital to bitcoins '''
        self.capital += q * p
        self.bitcoins -= q

    def capital_to_coins(self, q, p):
        ''' turns bitcoins to capital '''
        self.capital -= q * p
        self.bitcoins += q


class Altruist(Agent):
    ''' An Altruist agent uses the blockchain for various purposes that are not speculative or malicious '''

    def __init__(self):
        super().__init__()

        # variance of price, range [0, 1.0], higher --> greater deviation from market price
        self.d = 0.8

        # determines proportion of wealth to use for transaction
        self.b = 0.2

    def make_transactions(self, price):
        super().make_transactions(price)

        if random.randint(0, 1) == 0: # buy
            # get desired transaction price
            p_t = price + random.uniform(-0.5 * self.d * price, 0.8 * self.d * price)

            # proportion of wealth to use
            proportion = self.b + random.uniform(-0.05 * self.d, 0.1 * self.d)

            # quantity of bitcoin
            q_t = int((proportion * self.capital) / p_t)

            # 0 is buy
            return (0, p_t, q_t)

        else: # sell

            # get desired transaction price
            p_t = price + random.uniform(-0.8 * self.d * price, 0.5 * self.d * price)

            # proportion of wealth to use
            proportion = self.b + random.uniform(-0.1 * self.d, 0.05 * self.d)

            # quantity of bitcoin
            q_t = int((proportion * self.capital) / p_t)

            # 0 is buy
            return (1, p_t, q_t)



