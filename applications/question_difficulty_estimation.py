import os.path
import pandas as pd

from evaluation_metrics import pairwise_accuracy
try:
	import cPickle as pickle 
except Exception as e:
	import pickle

def format_creationDate(creationDate):
	'''
	CreationDate="2016-08-02T15:39:14.947"
	'''
	dates = creationDate.split("T")[0]
	times = creationDate.split("T")[1]
	y,mo,d = dates.split("-")
	h,mi,_ = times.split(":")
	return int(y),int(mo),int(d),int(h),int(mi)

def timestaps(creationDate1,creationDate2):
	y1,mo1,d1,h1,mi1 = format_creationDate(creationDate1)
	y2,mo2,d2,h2,mi2 = format_creationDate(creationDate2)
	return (mi2 - mi1)  + (h2 - h1)*60 + (d2-d1)*60*24 + (mo2 - mo1)*60*24*30 + (y2 - y1)*60*24*30*365

def number_of_answers(dir_name):
	# question difficulty is correlated with its number of answers
	questionid_answererid = pd.read_csv(os.path.join(dir_name,"QuestionId_AnswererId.csv"))
	ques_numAnswers_dict = {}
	for q,u in zip(questionid_answererid["QuestionId"],questionid_answererid["AnswererId"]):
		ques_numAnswers_dict[q] = ques_numAnswers_dict.get(q,0) + 1
	return ques_numAnswers_dict

def time_first_answer(dir_name):
	# question difficulty is correlated with its time of the first answers
	ques_creation = pd.read_csv(os.path.join(dir_name,"QuestionId_AskerId.csv"))
	ques_creation_dict = dict(zip(ques_creation["QuestionId"],ques_creation["CreationDate"]))

	questionid_answerid = pd.read_csv(os.path.join(dir_name,"AnswerId_QuestionId.csv"))
	ques_first_answer_time_dict = {}
	for q,t in zip(questionid_answerid["QuestionId"],questionid_answerid["CreationDate"]):
		if q in ques_first_answer_time_dict:
			ques_first_answer_time_dict[q] = min(ques_first_answer_time_dict[q],timestaps(ques_creation_dict.get(q,"2000-08-02T15:40:24.820"),t))
		else:
			ques_first_answer_time_dict[q] = timestaps(ques_creation_dict.get(q,"2000-08-02T15:40:24.820"),t)
	return ques_first_answer_time_dict

def time_best_answer(dir_name):
	# question difficulty is correlated with its time of the first answers
	ques_creation = pd.read_csv(os.path.join(dir_name,"QuestionId_AskerId.csv"))
	ques_creation_dict = dict(zip(ques_creation["QuestionId"],ques_creation["CreationDate"]))

	questionid_answerid = pd.read_csv(os.path.join(dir_name,"AnswerId_QuestionId.csv"))
	answer_creation_dict = dict(zip(questionid_answerid["AnswerId"],questionid_answerid["CreationDate"]))

	ques_bestanswer = pd.read_csv(os.path.join(dir_name,"QuestionId_AcceptedAnswererId.csv"))
	ques_bestanswer_dict = dict(zip(ques_bestanswer["QuestionId"],ques_bestanswer["AcceptedAnswerId"]))

	ques_bestanswer_time_dict = {}
	for q,ba in ques_bestanswer_dict.iteritems():
		ques_bestanswer_time_dict[q] = timestaps(ques_creation_dict.get(q,"2000-08-02T15:40:24.820"),answer_creation_dict[ba])

	return ques_bestanswer_time_dict

def load_dict_from_csv(input_file_name,mapping_file):

	with open(mapping_file,"rb") as f:
		mapping = pickle.load(f)
	if input_file_name.endswith("txt"):
		question_score = pd.read_csv(input_file_name,delim_whitespace = True, header = None)
		question_score_dict = dict(zip(question_score.iloc[:,0],question_score.iloc[:,1]))
	elif input_file_name.endswith("pkl"):
		with open(input_file_name,"rb") as f:
			question_score_dict = pickle.load(f)
	original_post_score = {}
	for q,s in question_score_dict.iteritems():
		if mapping["i2s"][q].startswith("q"):
			#print mapping["i2s"][q],int(mapping["i2s"][q][1:])
			original_post_score[int(mapping["i2s"][q][1:])] =  s
	#with open(input_file_name[:len(input_file_name)-4]+".pkl","wb") as f:
	#	pickle.dump(original_post_score,f)
	#print original_post_score
	return original_post_score

def question_difficulty_estimation_baseline(dir_name,baseline = "number_of_answers"):
	question_bounty = pd.read_csv(os.path.join(dir_name,"QuestionId_Bounty.csv"))
	
	bounty_truth = []
	difficulty_prediction = []

	if baseline == "number_of_answers":
		ques_score_dict = number_of_answers(dir_name)
	if baseline == "time_first_answer":
		ques_score_dict = time_first_answer(dir_name)
	if baseline == "time_best_answer":
		ques_score_dict = time_best_answer(dir_name)
	if baseline == "trueskill":
		ques_score_dict = load_dict_from_csv(os.path.join(dir_name,"competition_graph_index0_trueskill.txt"),os.path.join(dir_name,"competition_graph_id_mapping.pkl"))
	if baseline == "socialagony":
		ques_score_dict = load_dict_from_csv(os.path.join(dir_name,"competition_graph_index0_socialagony.txt"),os.path.join(dir_name,"competition_graph_id_mapping.pkl"))
	if baseline == "HGE":
		ques_score_dict = load_dict_from_csv(os.path.join(dir_name,"competition_graph_index0_HGE_ranking.pkl"),os.path.join(dir_name,"competition_graph_id_mapping.pkl"))
		
	for q,bounty in zip(question_bounty["QuestionId"],question_bounty["Bounty"]):
		if q in ques_score_dict:
			bounty_truth.append(bounty)
			difficulty_prediction.append(ques_score_dict[q])

	print("# questions for difficulty evaluation of %s: %d" % (baseline,len(bounty_truth)))
	acc1,acc2 = pairwise_accuracy(bounty_truth,difficulty_prediction)
	from evaluation_metrics import correlation 
	correlation(bounty_truth,difficulty_prediction,metric = "pearsonr")
	correlation(bounty_truth,difficulty_prediction,metric = "kendalltau")

def question_difficulty_estimation_baselines(dir_name):
	baselines = ["socialagony","trueskill","HGE","number_of_answers","time_first_answer","time_best_answer"]
	#baselines = ["number_of_answers","time_first_answer","time_best_answer"]
	for b in baselines:
		question_difficulty_estimation_baseline(dir_name,baseline = b)

import argparse
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "../dataset/scifi", help = "category name")
	args = parser.parse_args()
	question_difficulty_estimation_baselines(args.input)