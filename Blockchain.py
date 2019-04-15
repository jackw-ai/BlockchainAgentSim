import time

class Blockchain():

    def __init__(self, coins = 10000):

        # total number of coins
        self.coins = coins

        # current price
        self.price = 10

        # order lists
        self.sell = []
        self.buy = []

        # time step in simulation
        self.step = 0

        # population of users (Miners, Speculators, Altruists)
        self.population = {'M' : 1000, 'S' : 10, 'A': 20}

    def step(self):
        ''' performs one time step in the simulation '''

        self.day += 1

        self.new_agents()

        self.mine()

        self.get_transactions()

        self.resolve_transactions()

    def new_agents(self):
        '''
        new agents come into the blockchain
        '''

        # new miners
        pass


    # TODO
    def mine(self):
        '''
        miners mine for blocks
        '''
        self.coins += 100


    def get_transactions(self):
        '''
        adds transactions to the order lists
        '''


    def resolve_transactions(self):
        '''
        performs transactions by matching buy and sell orders
        '''

        self.buy.sort(reverse = True)
        self.sell.sort()

        i = j = 0

        while i < len(self.buy) and j < len(self.sell):
            p_b, q_b = self.buy[i]
            p_s, q_s = self.sell[j]

            if p_b <= p_s: # hit! make transaction

                # use the lesser quantity
                q_t = min(q_b, q_s)
                q_b -= q_t
                q_s -= q_t

                t_count += q_t
                t_p += q_t * p_b

                if q_b == 0: # all bought, move on
                    i += 1
                else: # update residual quantity
                    self.buy[i] = (p_b, q_b)

                if q_s == 0: # all sold
                    j += 1
                else: # update residual quantity
                    self.sell[j] = (p_s, q_s)

                # maximum transaction price right now
                self.price = p_b

            else: # no hits left, go to next time step
                break


        # update order lists
        self.buy = self.buy[i:]
        self.sell = self.sell[j:]
        print(self.price)






