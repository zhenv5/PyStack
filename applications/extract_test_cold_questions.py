try:
	import cPickle as pickle 
except Exception as e:
	import pickle
import pandas as pd 
import os.path
import random


def process_ques_asker(cate_name):
	asker_df = pd.read_csv(os.path.join(cate_name,"QuestionId_AskerId.csv"))
	ques_asker_dict = {k:v for k,v in zip(asker_df["QuestionId"],asker_df["AskerId"])}		
	asker_ques_dict = {}
	for a,q in zip(asker_df["AskerId"],asker_df["QuestionId"]):
		if a in asker_ques_dict:
			asker_ques_dict[a].append(q)
		else:
			asker_ques_dict[a] = [q]
	return ques_asker_dict,asker_ques_dict


def new_questions_new_askers_for_test(cate_name,least_number_of_answers_per_question = 5,least_number_of_questions_per_asker = 2):
	test_file = os.path.join(cate_name,"new_questions_new_askers_ques.pkl")
	if False:
		if os.path.isfile(test_file):
			with open(test_file,"rb") as f:
				ques_set = pickle.load(f)
				print("# questions for Test (new questions new askers): %d" % len(ques_set))
				return ques_set
	asker_ques_w_bestAnser_dict = {}
	ques_asker_dict,asker_ques_dict = process_ques_asker(cate_name)
	ques_answerers_dict,answerer_questions_dict = process_ques_answerer(cate_name)

	filterd_ques_answerers = dict(filter(lambda x: len(x[1]) >= least_number_of_answers_per_question, ques_answerers_dict.iteritems()))
	print("# questions having at least %d answers: %d" % (least_number_of_answers_per_question,len(filterd_ques_answerers)))

	filterd_asker_questions = dict(filter(lambda x: len(x[1]) == 1, asker_ques_dict.iteritems()))
	print("# askers having asked  %d questions: %d" % (1,len(filterd_asker_questions)))

	df = pd.read_csv(os.path.join(cate_name,"QuestionId_AcceptedAnswerId.csv"))
	for q,u in zip(df["QuestionId"],df["AcceptedAnswerId"]):
		a = ques_asker_dict[q]
		if a in filterd_asker_questions:
			# a has asked more than a specific number of questions
			if q in filterd_ques_answerers:
				# using the last asked question for test
				# q has more than a specific number of answers
				if a not in asker_ques_w_bestAnser_dict:
					asker_ques_w_bestAnser_dict[a] = [(q,u)]
				else:
					asker_ques_w_bestAnser_dict[a].append((q,u))

	ques_set =set([v[-1][0] for k,v in asker_ques_w_bestAnser_dict.iteritems()])
	print("==== # askers for Test (new questions new asker) : %d" % len(asker_ques_w_bestAnser_dict))
	print("==== # questions for Test (new questions new askers): %d" % len(ques_set))
	with open(test_file,"wb") as f:
		pickle.dump(ques_set,f)
	return ques_set


def new_questions_old_askers_for_test(cate_name,least_number_of_answers_per_question = 5,least_number_of_questions_per_asker = 2):
	
	test_file = os.path.join(cate_name,"new_questions_old_askers_ques.pkl")
	if False:

		if os.path.isfile(test_file):
			with open(test_file,"rb") as f:
				ques_set = pickle.load(f)
				print("# questions for Test (new questions old askers) : %d" % len(ques_set))
				return ques_set
		
	asker_ques_w_bestAnser_dict = {}
	ques_asker_dict,asker_ques_dict = process_ques_asker(cate_name)
	ques_answerers_dict,answerer_questions_dict = process_ques_answerer(cate_name)

	filterd_ques_answerers = dict(filter(lambda x: len(x[1]) >= least_number_of_answers_per_question, ques_answerers_dict.iteritems()))
	print("# questions having at least %d answers: %d" % (least_number_of_answers_per_question,len(filterd_ques_answerers)))

	filterd_asker_questions = dict(filter(lambda x: len(x[1]) >= 2, asker_ques_dict.iteritems()))
	print("# askers having asked at least %d questions: %d" % (least_number_of_questions_per_asker,len(filterd_asker_questions)))

	df = pd.read_csv(os.path.join(cate_name,"QuestionId_AcceptedAnswerId.csv"))
	for q,u in zip(df["QuestionId"],df["AcceptedAnswerId"]):
		a = ques_asker_dict[q]
		if a in filterd_asker_questions:
			# a has asked more than a specific number of questions
			if q in filterd_ques_answerers:
				# using the last asked question for test
				# q has more than a specific number of answers
				if a not in asker_ques_w_bestAnser_dict:
					asker_ques_w_bestAnser_dict[a] = [(q,u)]
				else:
					asker_ques_w_bestAnser_dict[a].append((q,u))

	# corresponding askers should have at least 2 questions which have best answerers
	ques_set =set([v[-1][0] for k,v in asker_ques_w_bestAnser_dict.iteritems() if len(v) > 1])
	#ques_set =set([v[-1][0] for k,v in asker_ques_w_bestAnser_dict.iteritems()])
	print("=== # questions for Test (new questions old askers):  %d" % len(ques_set))
	with open(test_file,"wb") as f:
		pickle.dump(ques_set,f)
	return ques_set

def process_ques_answerer(cate_name):
	file_name = os.path.join(cate_name,"QuestionId_AnswererId.csv")
	df = pd.read_csv(file_name)
	ques_users_dict = {}
	user_ques_dict = {}
	for q,u in zip(df["QuestionId"],df["AnswererId"]):
		if q in ques_users_dict:
			ques_users_dict[q].append(u)
		else:
			ques_users_dict[q] = [u]
		if u in user_ques_dict:
			user_ques_dict[u].append(q)
		else:
			user_ques_dict[u] = [q]
	return ques_users_dict,user_ques_dict

def process_ques_bestAnswerer(cate_name):
	df = pd.read_csv(os.path.join(cate_name,"QuestionId_AcceptedAnswererId.csv"))
	return {k:v for k,v in zip(df["QuestionId"],df["AcceptedAnswererId"])}

def remove_best_answerers(cate_name,test_rate = 0.15):
	# building dataset for resolved questions
	file_name = os.path.join(cate_name,"QuestionId_AnswererId.csv")
	df = pd.read_csv(file_name)
	ques = df["QuestionId"]
	users = df["AnswererId"]

	asker_df = pd.read_csv(os.path.join(cate_name,"QuestionId_AskerId.csv"))
	
	ques_asker_dict = {k:v for k,v in zip(asker_df["QuestionId"],asker_df["AskerId"])}		
	
	asker_ques_dict = {}
	for a,q in zip(asker_df["AskerId"],asker_df["QuestionId"]):
		if a in asker_ques_dict:
			asker_ques_dict[a].append(q)
		else:
			asker_ques_dict[a] = [q]
	ques_users_dict = {}
	user_ques_dict = {}

	for q,u in zip(ques,users):
		if q in ques_users_dict:
			ques_users_dict[q].append(u)
		else:
			ques_users_dict[q] = [u]
		if u in user_ques_dict:
			user_ques_dict[u].append(q)
		else:
			user_ques_dict[u] = [q]
	
	print("# instances in dataset: %d" % len(ques))
	ques_users_dict = dict((k,len(v)) for k,v in ques_users_dict.iteritems())
	user_ques_dict = dict((k,len(v)) for k,v in user_ques_dict.iteritems())
	asker_ques_dict = dict((k,len(v)) for k,v in asker_ques_dict.iteritems())

	print("# users answered more than 1 question: %d" % len(filter(lambda x: x > 1,user_ques_dict.values())))
	print("# questions having more than 1 answer: %d" % len(filter(lambda x: x > 1,ques_users_dict.values())))
	print("# askers having more than 1 question: %d (%d)" % (len(filter(lambda x: x > 1, asker_ques_dict.values())),len(asker_ques_dict)))
	ba_file_name = os.path.join(cate_name,"QuestionId_AcceptedAnswererId.csv")
	df_ba = pd.read_csv(ba_file_name)
	ques_ba = df_ba["QuestionId"]
	users_ba = df_ba["AcceptedAnswererId"]
	
	deleted_instances = set()

	for q,u in zip(ques_ba,users_ba):
		askerID = ques_asker_dict[q]
		if (ques_users_dict.get(q,0) > 1) and (user_ques_dict.get(u,0) > 1) and (asker_ques_dict.get(askerID,0) > 1):
			deleted_instances.add((q,u))
			ques_users_dict[q] = ques_users_dict[q] - 1
			user_ques_dict[u] = user_ques_dict[u] -  1
			asker_ques_dict[askerID] = asker_ques_dict[askerID] - 1

	print("# questions having best answers: %d" % len(ques_ba))
	
	num_test = int(len(ques_ba)*test_rate)
	num = 0
	for (q,u) in deleted_instances:
		for i,(q1,u1) in enumerate(zip(df["QuestionId"],df["AnswererId"])):
			if (q == q1) and (u == u1):
				#if random.random() > test_rate:
				#	break
				df.drop(df.index[i],inplace = True)
				num += 1
				break
		if num >= num_test:
			break
	print("# questions with best answer removed: %d (%0.4f)" % (num,num*1.0/len(ques_ba)))
	print("# instances for training: %d (%0.4f)" % (len(df["QuestionId"]),len(df["QuestionId"])*1.0/len(ques)))
	df.to_csv(os.path.join(cate_name,"QuestionId_AnswererId_Train.csv"),index = True, columns = ["QuestionId","AnswerId","AnswererId","Score"])

import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input",default= "../dataset/bitcoin", help = "input category name")
    parser.add_argument("-r","--test_rate",default = 0.15, type = float, help = "test rate")
    args = parser.parse_args()
    new_questions_new_askers_for_test(args.input)
    new_questions_old_askers_for_test(args.input)
    #remove_best_answerers(args.input,args.test_rate)
