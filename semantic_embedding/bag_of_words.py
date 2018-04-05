import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import os.path
import cPickle as pickle

from semantic_core import embedding_mapping_between_answer_and_user

def bow_embedding(cate_name):
	from semantic_core import posts_processing
	questions,answers,users = posts_processing(os.path.join(cate_name,"Posts.xml"))
	doc_ques = dict(("".join(("q",str(q))),t) for q,t in questions.iteritems())
	doc_answers = dict(("".join(("a",str(a))),t) for a,t in answers.iteritems())
	#doc_users = dict(("".join(("u",str(u))),t) for u,t in users.iteritems())

	docs = doc_ques.copy()
	docs.update(doc_answers)
	doc_ids = docs.keys()
	doc_values = docs.values()
	#, stop_words='english'
	# max_df 0.5 -> 0.85; min_df 2 -> 1
	vectorizer = TfidfVectorizer(sublinear_tf = True, max_df = 0.75, min_df = 2)
	features = vectorizer.fit_transform(doc_values)
	feature_names = vectorizer.get_feature_names()
	print("# docs: %d, # features: %d " % (features.shape[0],features.shape[1]))

	ques_dict = {}
	answer_dict = {}

	for k,v in zip(doc_ids,features):
		key = int(k[1:])
		if k[0] == "q":
			ques_dict[key] = v 
		elif k[0] == "a":
			answer_dict[key] = v

	user_dict = embedding_mapping_between_answer_and_user(cate_name,answer_dict)

	print("# embeddings for questions, answers, users: %d, %d, %d" % (len(ques_dict),len(answer_dict),len(user_dict)))

	with open(os.path.join(cate_name,"question_bow.pkl"),"wb") as f:
		pickle.dump(ques_dict,f)
	with open(os.path.join(cate_name,"answer_bow.pkl"),"wb") as f:
		pickle.dump(answer_dict,f)
	with open(os.path.join(cate_name,"user_bow.pkl"),"wb") as f:
		pickle.dump(user_dict,f)

import argparse
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "../dataset/ai", help = "input category name")
	args = parser.parse_args()
	bow_embedding(args.input)