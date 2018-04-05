from trueskill import Rating, quality_1vs1, rate_1vs1 
import networkx as nx
import numpy as np
import time
from datetime import datetime
import random 

def compute_trueskill(pairs,players):
	if not players:
		for u,v in pairs:
			if u not in players:
				players[u] = Rating()
			if v not in players:
				players[v] = Rating()

	start = time.time()
	random.shuffle(pairs)
	for u,v in pairs:
		players[v],players[u] = rate_1vs1(players[v],players[u])

	end = time.time()
	print("time used in computing true skill (per iteration): %0.4f s" % (end - start))
	return players

def get_players_score(players,n_sigma):
	relative_score = {}
	for k,v in players.iteritems():
		relative_score[k] = players[k].mu - n_sigma * players[k].sigma
	return relative_score

def trueskill_ratings(pairs,iter_times = 15,n_sigma = 3,threshold = 0.85):
	start = datetime.now()
	players = {}
	for i in xrange(iter_times):
		print("========= Trueskill iteration times: %d =========" % (i + 1))
		players = compute_trueskill(pairs,players)
		relative_scores = get_players_score(players,n_sigma = n_sigma)
		
	end = datetime.now()
	time_used = end - start
	print("time used in computing true skill: %0.4f s, iteration time is: %i" % ((time_used.seconds),(i+1)))
	return relative_scores

def graphbased_trueskill(g,iter_times = 15,n_sigma = 3,threshold = 0.95):
	relative_scores = trueskill_ratings(g.edges(),iter_times = iter_times,n_sigma = n_sigma,threshold = threshold)
	#print relative_scores
	return relative_scores


def main(graph_file_name = "/home/sunjiank/Dropbox/Data/cit-Patents/cit-Patents.txt"):
	if graph_file_name.endswith(".txt") or graph_file_name.endswith(".edges"):
		g = nx.read_edgelist(graph_file_name,create_using = nx.DiGraph(),nodetype = int)
	elif graph_file_name.endswith(".gpkl") or graph_file_name.endswith(".gpickle"):
		g = nx.read_gpickle(graph_file_name)
	return graphbased_trueskill(g)

import argparse
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-g","--graph" , type = str, default = " ", help = "graph edges list file")
	args = parser.parse_args()
	edges_file_name = args.graph
	#main(edges_file_name = "Data/cit-Patents/cit-Patents.txt")
	#main(edges_file_name = "/dataset/Java/competition_graph.edges")
	main(edges_file_name)
