try:
	import cPickle as pickle
except Exception as e:
	import pickle
import pandas as pd
import os.path

def content_processing(dir_path):
	question_bounty = pd.read_csv(os.path.join(dir_path,"QuestionId_Bounty.csv"))
	questions_file = os.path.join(dir_path,"Questions.pkl")
	question_tags_file = os.path.join(dir_path,"question_tags.pkl")
	with open(questions_file,"rb") as f:
		questions = pickle.load(f)
	with open(question_tags_file,"rb") as f:
		question_tags = pickle.load(f)

	ques_content_tags_bounty = {}

	for q,s in zip(question_bounty["QuestionId"],question_bounty["Bounty"]):
		ques_content_tags_bounty[q] = [q,questions.get(q,[]),question_tags.get(q,[]),s]
	
	with open(os.path.join(dir_path,"QuestionId_Content_Tags_Bounty.pkl"),"wb") as f:
		pickle.dump(ques_content_tags_bounty,f)

import argparse
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "dataset/scifi", help = "category name")
	args = parser.parse_args()
	content_processing(args.input)
