import pandas as pd
import os.path
import networkx as nx
import cPickle as pickle

prefix = ""
question_prefix = "q"
answer_prefix = "a"
user_prefix = "u"
tag_prefix = "t"

def sprint(dir_name,file_name,line):
	print line
	with open(os.path.join(dir_name,file_name),"a") as f:
		f.write("%s \n" % line)

def extract_links(file_name,source_node_name,target_node_name,source_node_prefix,target_node_prefix):
	edges = []
	df = pd.read_csv(file_name)
	souce_nodes = df[source_node_name]
	target_nodes = df[target_node_name]
	for s,t in zip(souce_nodes,target_nodes):
		sid = prefix.join((source_node_prefix,str(s)))
		tid = prefix.join((target_node_prefix,str(t)))
		edges.append((sid,tid))
	
	file_dir = os.path.dirname(os.path.abspath(file_name))

	sprint(file_dir,"directed_competition_graph_statistics.log","# edges between %s and %s: %d" % (source_node_name,target_node_name,len(edges)))
	return edges

def tag_question_edges(file_name):
	edges = []
	with open(file_name,"rb") as f:
		question_tags = pickle.load(f)
		for k,v in question_tags.iteritems():
			edges += [("".join((tag_prefix,t)),"".join((question_prefix,str(k)))) for t in v]
	print("# edges between tag and question: %d" % len(edges))
	return edges


def asker_question_edges(file_name):
	# edges are from askers to questions
	return extract_links(file_name = file_name,source_node_name = "AskerId", \
		target_node_name = "QuestionId",source_node_prefix = user_prefix, \
		target_node_prefix = question_prefix)

def answer_answerer_edges(file_name):
	# edges are from answers to users
	return extract_links(file_name = file_name, source_node_name = "AnswerId", \
		target_node_name = "AnswererId", source_node_prefix = answer_prefix, \
		target_node_prefix = user_prefix)

def question_answer_edges(file_name):
	# edges are from question to answers
	return extract_links(file_name = file_name, source_node_name = "QuestionId", \
		target_node_name = "AnswerId", source_node_prefix = question_prefix, \
		target_node_prefix = answer_prefix
		)

def question_answerer_edges(file_name):
	return extract_links(file_name = file_name, source_node_name = "QuestionId", \
		target_node_name = "AnswererId", source_node_prefix = question_prefix, \
		target_node_prefix = user_prefix
		)

def question_bestAnswerer_edges(file_name):
	return extract_links(file_name = file_name, source_node_name = "QuestionId", \
		target_node_name = "AcceptedAnswererId", source_node_prefix = question_prefix, \
		target_node_prefix = user_prefix
		)

def asker_answerer_edges(dir_name):
	q_asker = pd.read_csv(os.path.join(dir_name,"QuestionId_AskerId.csv"))
	q_asker_dict = dict(zip(q_asker["QuestionId"],q_asker["AskerId"]))	
	q_answerer = pd.read_csv(os.path.join(dir_name,"QuestionId_AnswererId.csv"))
	q_answerers_dict = {}
	for q,u in zip(q_answerer["QuestionId"],q_answerer["AnswererId"]):
		if q in q_answerers_dict:
			q_answerers_dict[q].append(u)
		else:
			q_answerers_dict[q] = [u]
	asker_2_answerer_edges = []
	for q,us in q_answerers_dict.iteritems():
		try:
			asker = q_asker_dict[q]
			asker_2_answerer_edges += [(prefix.join((user_prefix,str(asker))),prefix.join((user_prefix,str(u)))) for u in us]
		except Exception as e:
			pass 
	return asker_2_answerer_edges

def user_bestAnswerer_edges(dir_name):
	q_asker = pd.read_csv(os.path.join(dir_name,"QuestionId_AskerId.csv"))
	q_asker_dict = dict(zip(q_asker["QuestionId"],q_asker["AskerId"]))
	q_answerer = pd.read_csv(os.path.join(dir_name,"QuestionId_AcceptedAnswererId.csv"))
	q_answerer_dict = dict(zip(q_answerer["QuestionId"],q_answerer["AcceptedAnswererId"]))

	q_answerer = pd.read_csv(os.path.join(dir_name,"QuestionId_AnswererId.csv"))
	q_answerers_dict = {}
	for q,u in zip(q_answerer["QuestionId"],q_answerer["AnswererId"]):
		if q in q_answerers_dict:
			q_answerers_dict[q].append(u)
		else:
			q_answerers_dict[q] = [u]
	asker_bestAnswerer_edges = []
	other_bestAnswerer_edges = []
	for q,bestAnswerer in q_answerer_dict.iteritems():
		try:
			asker_bestAnswerer_edges.append((prefix.join((user_prefix,str(q_asker_dict[q]))),prefix.join((user_prefix,str(bestAnswerer)))))
		except Exception as e:
			print q,bestAnswerer,"q_asker_dict",e
		#print q,q_answerers_dict[q],bestAnswerer
		try:
			other_bestAnswerer_edges += [(prefix.join((user_prefix,str(u))),prefix.join((user_prefix,str(bestAnswerer)))) for u in q_answerers_dict[q] if u != bestAnswerer]
		except Exception as e:
			print q,bestAnswerer,"q_answerers_dict",e
	sprint(dir_name,"directed_competition_graph_statistics.log","# edges between asker and best answerer: %d" % len(asker_bestAnswerer_edges))
	sprint(dir_name,"directed_competition_graph_statistics.log","# edges between non-best Answerer and best Answerer: %d" % len(other_bestAnswerer_edges))
	return asker_bestAnswerer_edges,other_bestAnswerer_edges

def duplicate_questions_edges(file_name):
	edges = []
	df = pd.read_csv(file_name)
	nodes1 = df["PostId"]
	nodes2 = df["RelatedPostId"]
	types = df["LinkTypeId"]
	for n1,n2,t in zip(nodes1,nodes2,types):
		if int(t) == 3:
			sn1 = prefix.join((question_prefix,str(n1)))
			sn2 = prefix.join((question_prefix,str(n2)))
			edges.append((sn1,sn2))
			edges.append((sn2,sn1))
	print("# duplicate questions: %d" % (len(edges)/2))
	return edges



def extract_edges_from_list(l,is_fully_connected = True):
	# l, a list,[(answer,score)]
	score_dict = {}
	for (a,s) in l:
		if s in score_dict:
			score_dict[s].append(a)
		else:
			score_dict[s] = [a]
	
	number_of_different_scores = len(score_dict)

	if number_of_different_scores == 1:
		return []
	# sorted_score: (score,[answers list])
	sorted_score = sorted(score_dict.iteritems(),key = lambda x: x[0],reverse = False)
	edges = []
	for i in xrange(number_of_different_scores -1):
		source_answers = sorted_score[i][1]
		if is_fully_connected:
			max_j = number_of_different_scores
		else:
			max_j = i + 2
		for j in xrange(i+1,max_j):
			target_answers = sorted_score[j][1]
			for s in source_answers:
				for t in target_answers:
					e = (prefix.join((answer_prefix,str(s))),prefix.join((answer_prefix,str(t))))
					#print e,sorted_score[i][0],sorted_score[j][0]
					edges.append(e)
	return edges


def answers_of_same_question_edges(file_name,is_fully_connected = True):
	df = pd.read_csv(file_name)
	questions = df["QuestionId"]
	answers = df["AnswerId"]
	scores = df["Score"]
	q_dict = {}
	for q,a,s in zip(questions,answers,scores):
		if q in q_dict:
			q_dict[q].append((a,s))
		else:
			q_dict[q] = [(a,s)]
	print("# questions (at least 1 answer): %d" % len(q_dict))
	filtered_questions = filter(lambda x: len(x[1]) > 1,q_dict.iteritems())
	print("# questions (at least 2 answers): %d" % len(filtered_questions))
	sorted_questions = sorted(filtered_questions,key = lambda x: x[1][1],reverse = True)
	#print sorted_questions
	edges = []
	for (q,l) in sorted_questions:
		edges += extract_edges_from_list(l,is_fully_connected = is_fully_connected)
	#print edges
	print("# edges between answers of the same question: %d, is fully connected: %s" % (len(edges),is_fully_connected))
	return edges

def graph_nodes_analysis(g):
	number_nodes = [0,0,0,0]
	for node in g.nodes_iter():
		if node.startswith(question_prefix):
			number_nodes[0] += 1
		elif node.startswith(user_prefix):
			number_nodes[1] += 1
		elif node.startswith(answer_prefix):
			number_nodes[2] += 1
		elif node.startswith(tag_prefix):
			number_nodes[3] += 1
	return number_nodes

def graph_edges_analysis(g):
	number_edges = [0,0,0]
	for (u,v) in g.edges_iter():
		if u[0] == v[0]:
			number_edges[0] += 1
		else:
			if u[0].startswith(question_prefix) and v[0].startswith(user_prefix):
				number_edges[1] += 1
			if u[0].startswith(user_prefix) and v[0].startswith(question_prefix):
				number_edges[2] += 1
	return number_edges





def build_competition_graph(cate_name = "ai", Asker2Question = True, Question2BestAnswerer = True, Asker2BestAnswerer = True, Asker2Answerer = False, adding_duplicate = False, adding_Tag2Question = False, using_answer = False, using_non_bestAnswerer = False, is_fully_connected = True):
	
	g = nx.DiGraph()

	if Asker2Question:
		# asker -> question
		u_q_edges = asker_question_edges(os.path.join(cate_name,"QuestionId_AskerId.csv"))
		g.add_edges_from(u_q_edges)

	if Question2BestAnswerer:

		# question -> bestAnswerer
		q_bu_edges = question_bestAnswerer_edges(os.path.join(cate_name,"QuestionId_AcceptedAnswererId.csv"))
		g.add_edges_from(q_bu_edges)
	
	if Asker2BestAnswerer:
		# asker -> bestAnswerer, non best answerer -> best answerer
		asker_bestAnswerer_edges,other_bestAnswerer_edges = user_bestAnswerer_edges(cate_name)
		g.add_edges_from(asker_bestAnswerer_edges + other_bestAnswerer_edges)

	if Asker2Answerer:
		asker_2_answerer_edges  = asker_answerer_edges(cate_name)
		g.add_edges_from(asker_2_answerer_edges)

	if adding_duplicate:
		# edges between duplicate questions
		duplicate_questions_e = duplicate_questions_edges(os.path.join(cate_name,"PostId_RelatedPostId.csv"))
		g.add_edges_from(duplicate_questions_e)

	if adding_Tag2Question:
		# tag -> question
		t_q_edges = tag_question_edges(os.path.join(cate_name,"question_tags.pkl"))
		g.add_edges_from(t_q_edges)

	if using_answer:
		# question -> answer, answer -> answerer
		a_u_edges = answer_answerer_edges(os.path.join(cate_name,"AnswerId_AnswererId.csv"))
		q_a_edges = question_answer_edges(os.path.join(cate_name,"AnswerId_QuestionId.csv"))
		a_a_edges = answers_of_same_question_edges(os.path.join(cate_name,"AnswerId_QuestionId.csv"),is_fully_connected = is_fully_connected)
		g.add_edges_from(q_a_edges + a_u_edges + a_a_edges)

	if using_non_bestAnswerer:
		# question -> answerer
		q_u_edges = question_answerer_edges(os.path.join(cate_name,"QuestionId_AnswererId.csv"))
		g.add_edges_from(q_u_edges)
	
	sprint(cate_name,"directed_competition_graph_statistics.log","Graph Statistics: # nodes: %d, # edges: %d, is directed acyclic graph: %s" % (g.number_of_nodes(),g.number_of_edges(),nx.is_directed_acyclic_graph(g)))
	number_nodes = graph_nodes_analysis(g)
	sprint(cate_name,"directed_competition_graph_statistics.log","In Graph: # question node, # user node, # answer node, # tag node: %s" % number_nodes)
	number_edges = graph_edges_analysis(g)
	sprint(cate_name,"directed_competition_graph_statistics.log","In Graph: # (user node, user node), # (question node, bestAnswerer node), # (asker node, question node): %s" % number_edges)

	nx.write_gpickle(g,os.path.join(cate_name,"competition_graph.gpickle"))

	return g

def CQARankGraph(cate_name):
	print("building CQARank Competition Graph ...")
	g = build_competition_graph(cate_name = cate_name,Asker2Question = False, Question2BestAnswerer = False, Asker2BestAnswerer = False, Asker2Answerer = True)
	from TrueSkill import graphbased_trueskill
	relative_scores = graphbased_trueskill(g)
	with open(os.path.join(cate_name,"CQARank_User_Expertise_TrueSkill.pkl"),"wb") as f:
		pickle.dump(relative_scores,f)

import argparse
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "../dataset/ai", help = "category name")
	args = parser.parse_args()

	#print("building directed graph...")
	#g = build_competition_graph(cate_name = args.input)
	
	CQARankGraph(args.input)