import pandas as pd
import os.path

def answers_per_question(dir_name):
	df = pd.read_csv(os.path.join(dir_name,"QuestionId_AnswererId.csv"))
	questions = df["QuestionId"]
	answers = df["AnswerId"]
	q_dict = {}
	for q,a in zip(questions,answers):
		if q in q_dict:
			q_dict[q].append(a)
		else:
			q_dict[q] = [a]
	print("# question-answer pairs: %d" % len(df))
	print("# questions: %d" % len(q_dict))
	print("# avg answers per question: %0.4f" % (len(df)*1.0/len(q_dict)))	


def questions_per_asker(dir_name):
	df = pd.read_csv(os.path.join(dir_name,"QuestionId_AskerId.csv"))
	questions = df["QuestionId"]
	askers = df["AskerId"]
	a_dict = {}
	for q,a in zip(questions,askers):
		if a in a_dict:
			a_dict[a].append(q)
		else:
			a_dict[a] = [q]
	print("# question-asker pairs: %d" % len(df))
	print("# askers: %d" % len(a_dict))
	print("# avg questions per asker: %0.4f" % (len(df)*1.0/len(a_dict)))	

def best_answerers(dir_name):
	df = pd.read_csv(os.path.join(dir_name,"QuestionId_AcceptedAnswererId.csv"))
	best_answerers = df["AcceptedAnswererId"]
	
	print("# Questions having best answerer: %d" % len(best_answerers))

	print("# Unique Best Answerers: %d" % len(set(list(best_answerers))))

import argparse
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "../dataset/android", help = "category name")
	args = parser.parse_args()
	answers_per_question(args.input)
	questions_per_asker(args.input)
	best_answerers(args.input)