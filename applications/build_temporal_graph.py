import pandas as pd
import os.path
from helper_funs import format_creationDate
from collections import defaultdict

def days_difference(date1,date2):
	y1,m1,d1,_,_ = format_creationDate(date1)
	y2,m2,d2,_,_ = format_creationDate(date2)
	from datetime import date
	date_start = date(y1, m1, d1)
	date_end = date(y2, m2, d2)
	delta = date_end - date_start
	return delta.days

def extract_asker_2_answerer_edges(cate_name = "../dataset/android", initial_date = "2018-01-01T15:39:14.947", interval_by_days = 30):
	asker_answerer_file = os.path.join(cate_name,"AskerId_AnswererId.csv")
	df = pd.read_csv(asker_answerer_file)
	edges = defaultdict(list)
	for asker, answerer, answer_creation_date in zip(df["AskerId"], df["AnswererId"], df["AnswerCreationDate"]):
		days = days_difference(initial_date,answer_creation_date)
		if days <= 0:
			edges[-1].append((asker,answerer))
		else:
			index = days / interval_by_days
			edges[index].append((asker,answerer))
	for k,v in edges.iteritems():
		print("date interval index: %d, # edges: %d" % (k, len(v)))
	return edges

def make_nodeId_start_from_0(edges_dict):
	originalid_2_id0 = {}
	id0_2_originalid = {}
	new_edges_dict = defaultdict(list)
	for k,v in edges_dict.iteritems():
		for (n1,n2) in v:
			if n1 not in originalid_2_id0:
				new_n1 = len(originalid_2_id0)
				originalid_2_id0[n1] = new_n1
				id0_2_originalid[new_n1] = n1 
			else:
				new_n1 = originalid_2_id0[n1]
			if n2 not in originalid_2_id0:
				new_n2 = len(originalid_2_id0)
				originalid_2_id0[n2] = new_n2
				id0_2_originalid[new_n2] = n2
			else:
				new_n2 = originalid_2_id0[n2]
			new_edges_dict[k].append((new_n1,new_n2))
	print("========Node index starts from 0 now========")
	for k,v in new_edges_dict.iteritems():
		print("date interval index: %d, # edges: %d" % (k, len(v)))
	return new_edges_dict


def filter_new_nodes(edges_dict):
	from sets import Set 
	nodes_set = Set()
	map(lambda (x,y): nodes_set.update(Set([x,y])), edges_dict[-1])
	print("# nodes in the initial graph: %d" % len(nodes_set))
	filtered_edges_dict = defaultdict(list)
	for k,v in edges_dict.iteritems():
		filtered_edges_dict[k] = [(s,t) for s,t in v if s in nodes_set and t in nodes_set]
	print("========Filtering nodes========")
	for k,v in filtered_edges_dict.iteritems():
		print("date interval index: %d, # edges: %d" % (k, len(v)))
	return filtered_edges_dict

	
def build_asker_2_answerer_network(cate_name = "../dataset/android", initial_date = "2018-01-01T15:39:14.947", interval_by_days = 30):
	original_edges_dict = extract_asker_2_answerer_edges(cate_name = cate_name, initial_date = initial_date, interval_by_days = interval_by_days)
	# remove new nodes
	filtered_edges_dict = filter_new_nodes(original_edges_dict)
	# node index starts from 0
	edges = make_nodeId_start_from_0(filtered_edges_dict)
	
	for k,v in edges.iteritems():
		df = pd.DataFrame({"AskerIndex":[n for n,_ in v], "AnswererIndex":[n for _,n in v]})
		save_file_name = os.path.join(cate_name,"AskerIndex_AnswererIndex_" + initial_date[:10] + "_interval_by_month_" + str(k) +".csv")
		print save_file_name
		df.to_csv(save_file_name,index = False, columns = ["AskerIndex","AnswererIndex"], header = False)


import argparse
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "../dataset/ai", help = "category name")
	parser.add_argument("--initial_date", default = "2018-01-01T15:39:14.947", help = "initial date")
	parser.add_argument("--interval_by_days", default = 30, help = "days interval")
	args = parser.parse_args()
	cate_name = args.input
	build_asker_2_answerer_network(cate_name = args.input, initial_date = args.initial_date, interval_by_days = args.interval_by_days)
	

	
