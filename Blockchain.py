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
		# self.population = []
		self.altruists = []
		self.speculators = []
		# miner agents on the blockchain
		self.miners = []

		# number of agents (actual) at each time step
		self.miner_counts = []
		self.altruist_counts = []
		self.speculator_counts = []

	# generate lists of agents before simulation
	def generate_agents(self):

		# available number of agents in each category
		num_miners = TIMESTEPS * 5
		num_altruists = TIMESTEPS * 12
		num_speculators = TIMESTEPS * 20
		total = num_miners + num_altruists + num_speculators

		# pareto wealth distribution; decide on param
		capitals = np.random.pareto(3, total) * 10000

		self.available_miners = [Miner(capitals[i]) for i in range(num_miners)]
		self.available_altruists = [Altruist(capitals[j]) for j in range(num_miners, num_altruists + num_miners)]
		self.available_speculators = [Speculator(capitals[k]) for k in range(num_altruists + num_miners, total)]

	def run(self, timesteps = TIMESTEPS):
		'''
		runs the simulation
		'''
		self.generate_agents()

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
		miner_count = 1 + int(np.abs(np.random.normal(3, 1)))
		altruist_count = np.abs(int(np.random.normal(10, 2)))
		n = self.consec_growth()
		speculator_count = random.randint(0, n**2)

		# extract agents from the agent list
		self.miners += self.available_miners[:miner_count]
		self.altruists += self.available_altruists[:altruist_count]
		self.speculators += self.available_speculators[:speculator_count]
		self.available_miners = self.available_miners[miner_count:]
		self.available_altruists = self.available_altruists[altruist_count:]
		self.available_speculators = self.available_speculators[speculator_count:]

		# record number of agents currently in the simulation
		if self.curr_step == 1:
			self.altruist_counts.append(altruist_count)
			self.miner_counts.append(miner_count)
			self.speculator_counts.append(speculator_count)
		else:
			self.altruist_counts.append(self.altruist_counts[-1] + altruist_count)
			self.miner_counts.append(self.miner_counts[-1] + miner_count)
			self.speculator_counts.append(self.speculator_counts[-1] + speculator_count)

		# # new miners
		# self.miners += [Miner() for _ in range(1 + int(np.abs(np.random.normal(3, 1))))]
		#
		# # altruists
		# self.population += [Altruist() for _ in range(np.abs(int(np.random.normal(10, 2))))]
		#
		# # use consecutive price hikes to account for hoarding effect
		# n = self.consec_growth()
		#
		# # more spectators likely to hoard in the more consecutive price hikes
		# self.population += [Speculator() for _ in range(random.randint(0, n**2))]

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
		for agent in self.altruists+self.speculators:
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

		# print(self.buy)
		# print(self.sell)

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

	def hash_power_proportions(self):
		''' plot miner proportion '''
		thp = self.total_hashpow
		pies = [miner.hashpow / thp for miner in self.miners]
		pies.sort()
		plt.pie(pies)
		plt.title("proportions of miner hash power")
		plt.show()

	def price_history(self):
		''' plot price history '''
		plt.plot(self.p_hist, '-')
		plt.xlabel("time steps"); plt.ylabel("price")
		plt.title("price history")
		plt.show()

	def num_agents_over_time(self):
		X = range(TIMESTEPS)
		plt.plot(X, self.altruist_counts, label="users")
		plt.plot(X, self.speculator_counts, label="speculators")
		plt.plot(X, self.miner_counts, label="miners")
		plt.legend()
		plt.xlabel("time steps"); plt.ylabel("number of agents")
		plt.title("number of agents over time")
		plt.show()

	def bitcoin_holding_history

	# call all plotting here, comment out ones not needed
	def plots(self):
		self.price_history()
		self.hash_power_proportions()
		self.num_agents_over_time()

chain = Blockchain()
chain.run()
chain.plots()
