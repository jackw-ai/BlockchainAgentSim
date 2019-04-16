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

    def __lt__(self, other):
        return True

    @abstractmethod
    def __str__(self):
        pass

class Altruist(Agent):
    ''' An Altruist agent uses the blockchain for various purposes that are not speculative or malicious '''

    def __init__(self):
        super().__init__()

        # variance of price, range [0, 1.0], higher --> greater deviation from market price
        self.d = random.uniform(0.1, 0.5)

        # determines proportion of wealth to use for transaction
        self.b = 0.2

    def make_transactions(self, price):
        ''' randomly makes transactions for daily use '''

        super().make_transactions(price)

        c = random.randint(0, 12)
        if c < 5: # buy

            # get desired transaction price
            p_t = price + random.uniform(-0.5 * self.d * price, 0.8 * self.d * price)

            # proportion of wealth to use
            proportion = self.b + random.uniform(-0.05 * self.d, 0.1 * self.d)

            # quantity of bitcoin
            q_t = int((proportion * self.capital) / p_t)

            if q_t > 0:
                # 0 is buy
                return (0, p_t, q_t)

        elif c < 10: # sell

            # get desired transaction price
            p_t = price + random.uniform(-0.8 * self.d * price, 0.5 * self.d * price)

            # proportion of wealth to use
            proportion = self.b + random.uniform(-0.1 * self.d, 0.05 * self.d)

            # quantity of bitcoins to use
            q_t = int((proportion * self.bitcoins))

            if q_t > 0:
                # 1 is sell
                return (1, p_t, q_t)

        # no trade
        return (-1, 0, 0)

    def __str__(self):
        super().__str__()
        return '(altruist, coins %d, capital %d)' %(self.bitcoins, self.capital)


class Miner(Agent):
    ''' A Miner agent uses the blockchain to mine for profit '''

    def __init__(self):
        super().__init__()

        # variance of price, range [0, 1.0], higher --> greater deviation from market price
        self.d = 0.0

        # determines proportion of wealth to use for transaction
        self.b = 0.2

        # mining power
        self.hashpow = random.uniform(10, 150)

    def make_transactions(self, price):
        ''' tendancy to sell bitcoins '''

        super().make_transactions(price)

        c = random.randint(0, 12)

        # miners have a lot less incentive to buy
        if c < 2: # buy

            # get desired transaction price
            p_t = price + random.uniform(-0.5 * self.d * price, 0.8 * self.d * price)

            # proportion of wealth to use
            proportion = self.b + random.uniform(-0.05 * self.d, 0.1 * self.d)

            # quantity of bitcoin
            q_t = int((proportion * self.capital) / p_t)

            if q_t > 0:
                # 0 is buy
                return (0, p_t, q_t)

        # tendency to sell bitcoin and cashout
        elif c < 10: # sell

            # get desired transaction price
            p_t = price + random.uniform(-0.8 * self.d * price, 0.5 * self.d * price)

            # proportion of wealth to use
            proportion = self.b + random.uniform(-0.1 * self.d, 0.05 * self.d)

            # quantity of bitcoins to use
            q_t = int((proportion * self.bitcoins))

            if q_t > 0:
                # 1 is sell
                return (1, p_t, q_t)

        # no trade
        return (-1, 0, 0)

    def __str__(self):
        super().__str__()
        return '(miner, coins %d, capital %d)' %(self.bitcoins, self.capital)


class Speculator(Agent):
    ''' A Speculator agent buys when the price rises and sells when the price drops '''

    def __init__(self):
        super().__init__()

        # variance of price, range [0, 1.0], higher --> greater deviation from market price
        self.d = random.uniform(0.2, 0.8)

        # determines proportion of wealth to use for transaction
        self.b = 0.2

        # compares price to previous price
        self.p_prev = 0

    def make_transactions(self, price):
        ''' buys when prices go up, sells when prices go down '''

        super().make_transactions(price)

        c = random.randint(0, 9)

        # miners have a lot less incentive to buy
        if c < 5 and price > self.p_prev: # buy

            # get desired transaction price
            p_t = price + random.uniform(-0.2 * self.d * price, 0.8 * self.d * price)

            # proportion of wealth to use
            proportion = self.b + random.uniform(-0.05 * self.d, 0.1 * self.d)

            # quantity of bitcoin
            q_t = int((proportion * self.capital) / p_t)

            self.p_prev = price

            if q_t > 0:
                # 0 is buy
                return (0, p_t, q_t)

        # tendency to sell bitcoin and cashout
        elif c > 4 and price < self.p_prev: # sell

            # get desired transaction price
            p_t = price + random.uniform(-0.8 * self.d * price, 0.2 * self.d * price)

            # proportion of wealth to use
            proportion = self.b + random.uniform(-0.1 * self.d, 0.05 * self.d)

            # quantity of bitcoins to use
            q_t = int((proportion * self.bitcoins))

            self.p_prev = price

            if q_t > 0:
                # 1 is sell
                return (1, p_t, q_t)

        # no trade
        return (-1, 0, 0)

    def __str__(self):
        super().__str__()
        return '(speculator, coins %d, capital %d)' %(self.bitcoins, self.capital)




