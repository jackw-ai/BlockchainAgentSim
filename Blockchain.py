import bisect, random

from Agent import Altruist

class Blockchain():

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

    def run(self, timesteps = 10):
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

    # TODO
    def new_agents(self):
        '''
        new agents come into the blockchain
        '''

        # new miners

        # new speculators

        # altruists
        self.population += [Altruist() for _ in range(random.randint(2, 10))]

    # TODO
    def mine(self):
        '''
        miners mine for blocks
        '''
        self.coins += 100

    # TODO
    def get_transactions(self):
        '''
        adds transactions to the order lists
        '''

        # miners make transactions
        for agent in self.population:
            b, p, q = agent.make_transactions(self.price)

            if b == 0:
                # use bisect to insert into sorted list
                bisect.insort(self.buy, (p, q, agent))
            else:
                bisect.insort(self.sell, (p, q, agent))

    def resolve_transactions(self):
        '''
        performs transactions by matching buy and sell orders
        '''

        # buy list is reversed
        i = len(self.buy) - 1

        j = 0

        while i >= 0 and j < len(self.sell):
            p_b, q_b, buyer = self.buy[i]
            p_s, q_s, seller = self.sell[j]

            if p_b >= p_s: # hit! make transaction

                # use the lesser quantity
                q_t = min(q_b, q_s)
                q_b -= q_t
                q_s -= q_t

                # update buyler and seller wallets
                buyer.capital_to_coins(q_t, p_b)
                seller.coins_to_capital(q_t, p_b)

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
                break

        # update order lists
        self.buy = self.buy[i:]
        self.sell = self.sell[j:]
        self.p_hist.append(self.price)
        print(self.price)


x = Blockchain()
x.run()


