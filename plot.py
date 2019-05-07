import numpy as np
import matplotlib.pyplot as plt

def plot_price_history(hist):
	''' plot price history '''
	plt.plot(hist, '-')
	plt.xlabel("time steps"); plt.ylabel("price")
	plt.title("price history")
	plt.show()

def plot_price_std(arr):
	''' plot std of price history over simulations'''
	plt.plot(arr, '-')
	plt.xlabel("time steps"); plt.ylabel("std of price")
	plt.title("standard deviation of daily prices")
	plt.show()

def plot_wealth_dist(total):
	total = {"user": total[0], "miner": total[1], "speculator": total[2]}
	total = dict(sorted(total.items(), key=lambda x:x[1]))
	plt.pie(list(total.values()), labels=list(total.keys()) )
	plt.title("wealth distribution post simulation")
	plt.show()

def plot_hash_power_prop(prop):
	''' plot miner proportion '''
	plt.pie(prop)
	plt.title("proportions of miner hash power")
	plt.show()

price_hist = np.load("price_hist.npy")
hash_power = np.load("hash_power.npy")
wealth_dist = np.load("wealth_dist.npy")

plot_price_history(np.mean(price_hist, axis=0))
plot_price_std(np.std(price_hist, axis=0))
plot_wealth_dist(np.mean(wealth_dist, axis=0))
# # plot_hash_power_prop(np.mean(hash_power, axis=0))

keep = 20
arr = np.zeros(keep)
for hp in hash_power:
	arr = np.add(hp[:keep], arr)
arr /= 100
plot_hash_power_prop(arr)
