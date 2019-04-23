import random

import numpy as np

from collections import deque

from abc import ABC, abstractmethod


class Agent(ABC):
	''' abstract agent class '''

	def __init__(self):
		super().__init__()

		# wealth follows a lognormal (right skewed) distribution
		# self.capital = np.random.lognormal(1, 2) * 10000 #random.randint(1000, 1000000)
		self.bitcoins = 0
		# self.loss_tolerance = 0.2

	@abstractmethod
	def make_transactions(self, price):
		'''
		returns transaction if there is one for the agent of form
		[0/1, (price, quantity)]

		0 == buy, 1 == sell
		'''
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
		''' prevent sorting issues '''
		return True

	@abstractmethod
	def __str__(self):
		pass

class Altruist(Agent):
	''' An Altruist agent uses the blockchain for various purposes that are not speculative or malicious '''

	def __init__(self, capital):
		super().__init__()

		self.capital = capital

		# variance of price, range [0, 1.0], higher --> greater deviation from market price
		self.d = 0.1 * np.random.normal(0.05, 0.05)

		# determines proportion of wealth to use for transaction
		self.b = 0.1

	def make_transactions(self, price):
		''' randomly makes transactions for daily use '''
		super().make_transactions(price)

		c = random.randint(0, 500)

		if c < 5: # buy

			# get desired transaction price
			p_t = price + random.uniform(-2.0 * self.d * price, 2.0 * self.d * price)

			# proportion of wealth to use
			proportion = self.b + random.uniform(-0.05 * self.d, 0.1 * self.d)

			# quantity of bitcoin
			q_t = int((proportion * self.capital) / p_t)

			if q_t > 0:
				# 0 is buy
				return (0, p_t, q_t)

		elif c < 10: # sell

			# get desired transaction price
			p_t = price + random.uniform(-0.9 * self.d * price, 0.5 * self.d * price)

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

	def __init__(self, capital):
		super().__init__()

		self.capital = capital

		# variance of price, range [0, 1.0], higher --> greater deviation from market price
		self.d = 0.05

		# determines proportion of wealth to use for transaction
		self.b = 0.3

		# investment rate
		self.g = 0.1

		# mining power
		self.hashpow = random.uniform(10, 150)

	def make_transactions(self, price):
		''' tendancy to sell bitcoins '''

		super().make_transactions(price)

		c = random.randint(0, 30)

		# miners have a lot less incentive to buy
		if c < 1: # buy

			# get desired transaction price
			p_t = price + random.uniform(-0.5 * self.d * price, 0.5 * self.d * price)

			# proportion of wealth to use
			proportion = self.b + random.uniform(-0.05 * self.d, 0.1 * self.d)

			# quantity of bitcoin
			q_t = int((proportion * self.capital) / p_t)

			if q_t > 0:
				# 0 is buy
				return (0, p_t, q_t)

		# tendency to sell bitcoin and cashout
		elif c < 25: # sell

			# get desired transaction price
			p_t = price + random.uniform(-0.8 * self.d * price, 0.2 * self.d * price)

			# proportion of wealth to use
			proportion = self.b + random.uniform(-0.1 * self.d, 0.05 * self.d)

			# quantity of bitcoins to use
			q_t = int((proportion * self.bitcoins))

			if q_t > 0:
				# 1 is sell
				return (1, p_t, q_t)

		# no trade
		return (-1, 0, 0)

	def assess_equipment(self):
		''' determines whether to invest in new equipment and increase hashpower'''
		buy = random.uniform(0, 500)

		if buy < 10: # invest in new equipment
			# resources to invest
			resources = self.capital * self.g
			self.capital -= resources
			self.hashpow = self.get_hashpow(resources, self.hashpow)


	@staticmethod
	def get_hashpow(resources, curr_hashpow):
		''' determine hashpower based on resources'''
		return resources**2 * 0.54 + curr_hashpow

	def __str__(self):
		super().__str__()
		return '(miner, coins %d, capital %d)' %(self.bitcoins, self.capital)


class Speculator(Agent):
	''' A Speculator agent buys when the price rises and sells when the price drops '''

	def __init__(self, capital):
		super().__init__()

		self.capital = capital

		# variance of price, range [0, 1.0], higher --> greater deviation from market price
		self.d = abs(np.random.normal(1, 0.5))

		# determines proportion of wealth to use for transaction
		self.b = 0.1

		# compares price to previous price
		self.p_prev = 0.001

		# speculators take into account price variation history
		self.interval = 1 + int(np.abs(np.random.normal(3, 1.5)))
		self.history = deque(maxlen = self.interval)

		# prefill history
		for _ in range(self.interval):
			self.history.append(8)

		# price variation lowerbound, buy/sell depending on price variance vs tolerance
		self.lower = np.random.normal(1.01, 0.05)

		# price variation upperbound, buy/sell depending on price variance vs tolerance
		self.upper = np.random.normal(1.6, 0.2)

	def make_transactions(self, price):
		''' buys when prices go up, sells when prices go down '''

		super().make_transactions(price)

		# introduce randomness to account for other factors
		c = random.randint(0, 10)

		# price variance
		ratio = price / self.history[0]

		# speculators take into account how price has changed in short term
		if c < 5 and ((self.upper > ratio > self.lower) or (1 / ratio < 0.9)): # price has increased a lot, we buy

			# get desired transaction price
			p_t = price + random.uniform(-0.2 * self.d * price, 0.8 * self.d * price)

			# proportion of wealth to use
			proportion = self.b + random.uniform(-0.05 * self.d, 0.1 * self.d)

			# quantity of bitcoin
			q_t = int((proportion * self.capital) / p_t)

			#self.p_prev = price

			if q_t > 0:
				self.history.append(price)
				# 0 is buy
				return (0, p_t, q_t)

		# tendency to sell bitcoin and cashout if prices are not growing fast enough
		elif c < 5: # sell either because price is falling or has made enough

			# get desired transaction price
			p_t = price + random.uniform(-8.9 * self.d * price, 0.1 * self.d * price)

			# proportion of wealth to use
			proportion = self.b + random.uniform(-0.1 * self.d, 0.05 * self.d)

			# quantity of bitcoins to use
			q_t = int((proportion * self.bitcoins))

			#self.p_prev = price

			if q_t > 0:
				self.history.append(price)

				# 1 is sell
				return (1, p_t, q_t)

		self.history.append(price)

		# no trade
		return (-1, 0, 0)

	def __str__(self):
		super().__str__()
		return '(speculator, coins %d, capital %d)' %(self.bitcoins, self.capital)
