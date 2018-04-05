try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

import cPickle as pickle
import os.path
import pandas as pd
import argparse

from gensim.models import doc2vec
from collections import namedtuple


def get_sentenses(posts,type_prefix):
	sentences = []
	#analyzedDocument = namedtuple('AnalyzedDocument', 'ID')
	for k,v in posts.iteritems():
		words = v.lower().split()
		tags = ["".join((type_prefix,str(k)))]
		sentences.append(doc2vec.LabeledSentence(words= words, tags=tags))
	#print sentences
	return sentences

def embedding_mapping_between_answer_and_user(cate_name,model):
	df = pd.read_csv(os.path.join(cate_name,"QuestionId_AnswererId.csv"))
	ques = df["QuestionId"]
	ans = df["AnswerId"]
	user = df["AnswererId"]
	
	user_dict_question_answer = {}
	for q,a,u in zip(ques,ans,user):
		if u not in user_dict_question_answer:
			user_dict_question_answer[u] = {}
		a_key = "".join(("a",str(a)))
		user_dict_question_answer[u][q] = model.docvecs[a_key].tolist()
	return user_dict_question_answer

def doc2vec_training(cate_name,embed_user_explictly = False):
	from semantic_core import posts_processing
	questions,answers,users = posts_processing(os.path.join(cate_name,"Posts.xml"))
	q_doc = get_sentenses(questions,"q")
	u_doc = get_sentenses(users,"u")
	a_doc = get_sentenses(answers,"a")
	if embed_user_explictly:
		docs = q_doc + u_doc + a_doc
	else:
		docs = q_doc + a_doc

	# size 64 -> 128
	model = doc2vec.Doc2Vec(docs, size = 32, window = 4, min_count = 2, workers = 4)

	ques_dict = {}
	answer_dict = {}
	

	for q,_ in questions.iteritems():
		q_key = "".join(("q",str(q)))
		ques_dict[q] = model.docvecs[q_key].tolist()
	for a,_ in answers.iteritems():
		a_key = "".join(("a",str(a)))
		answer_dict[a] = model.docvecs[a_key].tolist()

	user_dict = {}
	if embed_user_explictly:
		for u,_ in users.iteritems():
			u_key = "".join(("u",str(u)))
			user_dict[u] = model.docvecs[u_key].tolist()
	else:
		user_dict = embedding_mapping_between_answer_and_user(cate_name,model)

	print("Embedding: # questions: %d, # answers: %d, # users: %d" % (len(ques_dict),len(answer_dict),len(user_dict)))

	with open(os.path.join(cate_name,"question_doc2vec.pkl"),"wb") as f:
		pickle.dump(ques_dict,f)
	with open(os.path.join(cate_name,"answer_doc2vec.pkl"),"wb") as f:
		pickle.dump(answer_dict,f)
	with open(os.path.join(cate_name,"user_doc2vec.pkl"),"wb") as f:
		pickle.dump(user_dict,f)
 
	q_ba_file = os.path.join(cate_name,"QuestionId_AcceptedAnswererId.csv")
	q_ba_df = pd.read_csv(q_ba_file)

	q_feature = []
	ba_feature = []

	for q,ba in zip(q_ba_df["QuestionId"],q_ba_df["AcceptedAnswererId"]):
		q_key = "".join(("q",str(q)))
		ba_key = "".join(("u",str(ba)))
		
		q_feature.append(model.docvecs[q_key].tolist())
		if embed_user_explictly:

			ba_feature.append(model.docvecs[ba_key].tolist())
		else:
			ba_feature.append(user_dict[ba][q])
	with open(os.path.join(cate_name,"question_w_bestAnswerer_doc2vec.pkl"),"wb") as f:
		pickle.dump(q_feature,f)
	with open(os.path.join(cate_name,"bestAnswerer_doc2vec.pkl"),"wb") as f:
		pickle.dump(ba_feature,f)
	print("%s:# questions having best answer: %d # instances in features: %d, # instances in labels: %d" % (cate_name, q_ba_df.shape[0],len(q_feature),len(ba_feature)))

	assert q_ba_df.shape[0] == len(q_feature) and q_ba_df.shape[0] == len(ba_feature), "Error, # questions does not match # embeddings"


import argparse
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "../dataset/ai", help = "input category name")
	args = parser.parse_args()
	doc2vec_training(args.input)
