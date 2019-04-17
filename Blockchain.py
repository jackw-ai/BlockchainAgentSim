import bisect, random

import numpy as np
import matplotlib.pyplot as plt

from Agent import Altruist, Miner, Speculator

TIMESTEPS = 300

class Blockchain():
    ''' performs a simulation of a blockchain economy '''
    def __init__(self, coins = 10000):

        # total number of coins
        self.coins = coins

        # current price, starts at 10
        self.price = 10

        # whether spectators hoard (more come in when prices increase)
        self.hoard = True

        # whether miners continue to increase hashpower
        self.pool = True

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
        self.miners += [Miner() for _ in range(1 + int(np.abs(np.random.normal(3, 1))))]

        # altruists
        self.population += [Altruist() for _ in range(np.abs(int(np.random.normal(10, 2))))]

        # use consecutive price hikes to account for hoarding effect
        n = self.consec_growth()

        # more spectators likely to hoard in the more consecutive price hikes
        self.population += [Speculator() for _ in range(random.randint(0, n**2))]

    @property
    def block_reward(self):
        ''' block reward steadily decreases '''
        return 100.0 / (self.curr_step**0.1)

    def consec_growth(self):
        ''' count number of consecutive price hikes starting from latest price'''

        if not self.hoard:
            # if not hoarding, spectators enter uniformly random
            return 4

        c = 0

        for i in reversed(range(1, len(self.p_hist))):
            if self.p_hist[i] > self.p_hist[i - 1]:
                c += 1
            else:
                break
        return c

    @property
    def total_hashpow(self):
        '''
        :return: total mining power
        '''

        return sum([miner.hashpow for miner in self.miners])

    def plot_miners(self):
        ''' plot miner proportion '''
        thp = self.total_hashpow
        pies = [miner.hashpow / thp for miner in self.miners]
        pies.sort()
        plt.pie(pies)
        plt.show()

    def plot_price(self):
        ''' plot price history '''
        plt.plot(self.p_hist, '-')
        plt.show()

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
        winner.bitcoins += self.block_reward

    def get_transactions(self):
        '''
        adds transactions to the order lists
        '''

        # miners make transactions
        for agent in self.miners:

            if self.pool:
                # decide whether to upgrade equipment
                agent.assess_equipment()

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
x.plot_miners()
x.plot_price()



