import bisect, random

import numpy as np
import matplotlib.pyplot as plt

from Agent import Altruist, Miner, Speculator

TIMESTEPS = 500

class Blockchain():
    ''' performs a simulation of a blockchain economy '''
    def __init__(self, coins = 10000):

        # total number of coins
        self.coins = coins

        # current price
        self.price = 10

        self.p_hist = []

        # order lists, contains (p, q, agent)
        self.sell = []
        self.buy = []

        # time step in simulation
        self.curr_step = 0

        # population of agents (Speculators, Altruists)
        self.population = []

        # miner agents on the blockchain
        self.miners = []

    def run(self, timesteps = TIMESTEPS):
        '''
        runs the simulation
        '''

        print('starting simulation for %d timesteps...' %timesteps)

        for i in range(timesteps):
            self.step()

    def step(self):
        ''' performs one time step in the simulation '''

        self.curr_step += 1

        self.new_agents()

        self.mine()

        self.get_transactions()

        self.resolve_transactions()

    def new_agents(self):
        '''
        new agents come into the blockchain
        '''

        # new miners
        self.miners += [Miner() for _ in range(1 + int(np.abs(np.random.normal(1, 1))))]

        # altruists
        self.population += [Altruist() for _ in range(np.abs(int(np.random.normal(2, 2))))]

        # TODO add hoarding effect
        # new speculators
        self.population += [Speculator() for _ in range(random.randint(2, 10))]

    @property
    def total_hashpow(self):
        '''
        :return: total mining power
        '''

        return sum([miner.hashpow for miner in self.miners])

    # TODO add pooling
    def mine(self):
        '''
        miners mine for blocks by randomly selecting winner based on proportional hashpower
        '''

        # total hashpower
        thp = self.total_hashpow

        # probablity of mining next block
        probs = [miner.hashpow / thp for miner in self.miners]

        # select winner
        winner = np.random.choice(self.miners, p=probs)

        # winner gains newly minted coins
        winner.bitcoins += 100

    def get_transactions(self):
        '''
        adds transactions to the order lists
        '''

        # miners make transactions
        for agent in self.miners:
            b, p, q = agent.make_transactions(self.price)

            if b == 0:  # buy
                # use bisect to insert into sorted list
                bisect.insort(self.buy, (p, q, agent))
            elif b == 1:  # sell
                bisect.insort(self.sell, (p, q, agent))

        # agents make transactions
        for agent in self.population:
            b, p, q = agent.make_transactions(self.price)

            if b == 0: # buy
                # use bisect to insert into sorted list
                bisect.insort(self.buy, (p, q, agent))
            elif b == 1: # sell
                bisect.insort(self.sell, (p, q, agent))

    def resolve_transactions(self):
        '''
        performs transactions by matching buy and sell orders
        '''

        print(self.buy)
        print(self.sell)

        # buy list is reversed
        i = len(self.buy) - 1

        j = 0

        transaction = False

        while i >= 0 and j < len(self.sell):
            p_b, q_b, buyer = self.buy[i]
            p_s, q_s, seller = self.sell[j]

            if p_b >= p_s: # hit! make transaction

                transaction = True

                # use the lesser quantity
                q_t = min(q_b, q_s)
                q_b -= q_t
                q_s -= q_t

                print("---transaction---")
                print(buyer, '|||||', seller)
                print(q_t, '    ', p_b)

                # update buyer and seller wallets
                buyer.capital_to_coins(q_t, p_b)
                seller.coins_to_capital(q_t, p_b)

                print(buyer, '|||||', seller)

                if q_b == 0: # all bought, move on
                    i -= 1
                else: # update residual quantity
                    self.buy[i] = (p_b, q_b, buyer)

                if q_s == 0: # all sold
                    j += 1
                else: # update residual quantity
                    self.sell[j] = (p_s, q_s, seller)

                # maximum transaction price right now
                self.price = p_b

            else: # no hits left, go to next time step

                # market crashing...
                if not transaction:
                    self.price = p_s

                break

        # update order lists
        self.buy = []#self.buy[i:]
        self.sell = []#self.sell[j:]
        self.p_hist.append(self.price)
        print('\n', self.curr_step, ") Price: ", self.price, "\n")


x = Blockchain()
x.run()

plt.plot(x.p_hist, '-')
plt.show()


