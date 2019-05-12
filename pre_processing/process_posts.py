try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET
try:
	import cPickle as pickle
except ImportError:
	import pickle 

import os.path
import pandas as pd
import argparse
from helper_func import sprint

def process_QuestionId_AskerId(output_dir,Questions):
	output_file = os.path.join(output_dir,"QuestionId_AskerId.csv")
	df = pd.DataFrame({"QuestionId":Questions["QuestionId"],"AskerId":Questions["OwnerUserId"],"CreationDate":Questions["CreationDate"]})
	df.to_csv(output_file,index = True, columns = ["QuestionId","AskerId","CreationDate"])
	sprint(output_dir,"pystack_analysis.log","# question-asker pairs: %d" % len(df))

def process_QuestionId_AcceptedAnswerId(output_dir,Questions):
	QuestionId = []
	AcceptedAnswerId = []
	for qid,aid in zip(Questions["QuestionId"],Questions["AcceptedAnswerId"]):
		if aid:
			QuestionId.append(qid)
			AcceptedAnswerId.append(aid)
	df = pd.DataFrame({"QuestionId":QuestionId,"AcceptedAnswerId":AcceptedAnswerId})
	output_file = os.path.join(output_dir,"QuestionId_AcceptedAnswerId.csv")
	df.to_csv(output_file,index = True, columns = ["QuestionId","AcceptedAnswerId"])
	sprint(output_dir,"pystack_analysis.log","# question-acceptedAnswer pairs: %d" % len(df))

def process_AnswerId_QuestionId(output_dir,Answers):

	output_file = os.path.join(output_dir,"AnswerId_QuestionId.csv")
	df = pd.DataFrame({"QuestionId":Answers["QuestionId"],"AnswerId":Answers["AnswerId"],"Score":Answers["Score"],"CreationDate":Answers["CreationDate"]})
	df.to_csv(output_file,index = True, columns = ["QuestionId","AnswerId","Score","CreationDate"])
	sprint(output_dir,"pystack_analysis.log","# question-answer pairs: %d" % len(df))

def process_AnswerId_AnswererId(output_dir,Answers):

	output_file = os.path.join(output_dir,"AnswerId_AnswererId.csv")
	df = pd.DataFrame({"AnswerId":Answers["AnswerId"],"AnswererId":Answers["OwnerUserId"]})
	df.to_csv(output_file,index = True, columns = ["AnswerId","AnswererId"])
	sprint(output_dir,"pystack_analysis.log","# answer-answerer pairs: %d" % len(df))

def process_question_tags(output_dir,Questions):
	df = pd.DataFrame({"QuestionId":Questions["QuestionId"],"Tags":Questions["Tags"]})
	tags_set = []
	question_tags = {}
	for q,t in zip(df["QuestionId"],df["Tags"]):
		tags = [tag[1:] for tag in t.split(">") if len(tag) > 0]
		tags_set += tags
		question_tags[q] = tags
	
	sprint(output_dir,"pystack_analysis.log","# question with tags: %d" % len(question_tags))
	sprint(output_dir,"pystack_analysis.log","# tags per question: %0.4f" % (sum([len(x) for _,x in question_tags.iteritems()])*1.0/len(question_tags)))
	sprint(output_dir,"pystack_analysis.log","# unique tags: %d" % len(set(tags_set)))
	
	with open(os.path.join(output_dir,"question_tags.pkl"),"wb") as f:
		pickle.dump(question_tags,f)

def process_question_text(dir_path,Questions):
	questions_file = os.path.join(dir_path,"Questions.pkl")
	questions_dict = {}
	for question,title,body in zip(Questions["QuestionId"],Questions["Title"],Questions["Body"]):
		questions_dict[question] = [title,body]

	sprint(dir_path,"pystack_analysis.log","# questions with title and body: %d" % len(questions_dict))

	with open(questions_file,"wb") as f:
		pickle.dump(questions_dict,f)

def process_answer_body(dir_path,Answers):
	answers_file = os.path.join(dir_path,"Answers.pkl")
	answers_body = dict(zip(Answers["AnswerId"],Answers["Body"]))

	sprint(dir_path,"pystack_analysis.log","# answers with body: %d" % len(answers_body))
	with open(answers_file,"wb") as f:
		pickle.dump(answers_body,f)

def questionid_answererid(cate_name):
	questionid_answerid_file = os.path.join(cate_name,"AnswerId_QuestionId.csv")
	q_answer_df = pd.read_csv(questionid_answerid_file)

	answerId_AnswererId_file = os.path.join(cate_name,"AnswerId_AnswererId.csv")
	a_a_df = pd.read_csv(answerId_AnswererId_file)
	a_a_dict = dict(zip(a_a_df["AnswerId"],a_a_df["AnswererId"]))

	ques = []
	answer = []
	answerer = []
	score = []
	creation_date = []

	for q,a,s,c_d in zip(q_answer_df["QuestionId"],q_answer_df["AnswerId"],q_answer_df["Score"],q_answer_df["CreationDate"]):
		if a in a_a_dict:
			ques.append(q)
			answer.append(a)
			answerer.append(a_a_dict[a])
			score.append(s)
			creation_date.append(c_d)

	df = pd.DataFrame({"QuestionId":ques,"AnswerId":answer,"AnswererId":answerer,"Score":score,"CreationDate":creation_date})
	df.to_csv(os.path.join(cate_name,"QuestionId_AnswererId.csv"),index = True, columns = ["QuestionId","AnswerId","AnswererId","Score","CreationDate"])
	sprint(cate_name,"pystack_analysis.log","# question-answer-answerer pairs: %d" % len(df))

def questionid_bestanswererid(cate_name):
	questionid_bestanswerid_file = os.path.join(cate_name,"QuestionId_AcceptedAnswerId.csv")
	q_b_df = pd.read_csv(questionid_bestanswerid_file)
	answerId_AnswererId_file = os.path.join(cate_name,"AnswerId_AnswererId.csv")
	a_a_df = pd.read_csv(answerId_AnswererId_file)
	q_b_dict = dict(zip(q_b_df["QuestionId"],q_b_df["AcceptedAnswerId"]))
	a_a_dict = dict(zip(a_a_df["AnswerId"],a_a_df["AnswererId"]))
	q_l = []
	a_l = []
	aer_l = []
	for q,b in q_b_dict.iteritems():
		if b in a_a_dict:
			q_l.append(q)
			a_l.append(b)
			aer_l.append(a_a_dict[b]) 

	q_ber_df = pd.DataFrame({"QuestionId":q_l,"AcceptedAnswerId":a_l,"AcceptedAnswererId":aer_l})
	q_ber_df.to_csv(os.path.join(cate_name,"QuestionId_AcceptedAnswererId.csv"),index = True, columns = ["QuestionId","AcceptedAnswerId","AcceptedAnswererId"])
	sprint(cate_name,"pystack_analysis.log","# question-bestAnswerer pairs: %d" % len(q_ber_df))

def askerid_answererid(cate_name):
	questionid_askerid_file = os.path.join(cate_name,"QuestionId_AskerId.csv")
	q_asker_df = pd.read_csv(questionid_askerid_file)
	q_asker_dict = {}

	for q,a,q_c_d in zip(q_asker_df["QuestionId"],q_asker_df["AskerId"],q_asker_df["CreationDate"]):
		q_asker_dict[q] = [a,q_c_d]

	q_AnswererId_file = os.path.join(cate_name,"QuestionId_AnswererId.csv")
	q_answerer_df = pd.read_csv(q_AnswererId_file)

	ques = []
	asker = []
	answerer = []
	score = []
	q_creation_date = []
	answer_creation_date = []

	for q,a,s,c_d in zip(q_answerer_df["QuestionId"],q_answerer_df["AnswererId"],q_answerer_df["Score"],q_answerer_df["CreationDate"]):
		if q in q_asker_dict:
			ques.append(q)
			asker.append(q_asker_dict[q][0])
			answerer.append(a)
			score.append(s)
			q_creation_date.append(q_asker_dict[q][1])
			answer_creation_date.append(c_d)

	df = pd.DataFrame({"QuestionId":ques,"AskerId":asker,"AnswererId":answerer,"Score":score,"QuestionCreationDate":q_creation_date,"AnswerCreationDate":answer_creation_date})
	df.to_csv(os.path.join(cate_name,"AskerId_AnswererId.csv"),index = True, columns = ["QuestionId","AskerId","AnswererId","Score","QuestionCreationDate","AnswerCreationDate"])
	sprint(cate_name,"pystack_analysis.log","# question-asker-answerer pairs: %d" % len(df))
	
def process_common_attributes(Posts,elem):
	# common attributes between questions and answers
	try:
		owneruserid = int(elem.attrib["OwnerUserId"])
	except Exception as e:
		#print index,e
		return False
	Posts["CreationDate"].append(elem.attrib["CreationDate"])
	Posts["Score"].append(int(elem.attrib["Score"]))
	Posts["Body"].append(elem.attrib["Body"])
	#Posts["CommentCount"].append(int(elem.attrib["CommentCount"]))
	Posts["OwnerUserId"].append(owneruserid)
	#Posts["LastEditorUserId"].append(int(elem.attrib["LastEditorUserId"]) if ("LastEditorUserId" in elem.attrib) else None)
	return True

def process_element(Posts,elem,PostTypeId):

	index = int(elem.attrib["Id"])
	posttypeid = int(elem.attrib["PostTypeId"])
	
	if (PostTypeId == posttypeid) and (posttypeid == 1):
		# question
		if not process_common_attributes(Posts,elem):
			return
		Posts["QuestionId"].append(index)
		Posts["ViewCount"].append(int(elem.attrib["ViewCount"]))
		Posts["Title"].append(elem.attrib["Title"])
		Posts["Tags"].append(elem.attrib["Tags"])
		Posts["AnswerCount"].append(int(elem.attrib["AnswerCount"]))
		Posts["AcceptedAnswerId"].append(int(elem.attrib["AcceptedAnswerId"]) if ("AcceptedAnswerId" in elem.attrib) else None)
		
	elif (PostTypeId == posttypeid) and (posttypeid == 2):
		# answer
		if not process_common_attributes(Posts,elem):
			return
		Posts["AnswerId"].append(index)
		Posts["QuestionId"].append(int(elem.attrib["ParentId"]))
		
def init_posts(PostTypeId = 1):
	Posts = {}
	Posts["CreationDate"] = []
	Posts["Score"] = []
	Posts["Body"] = []
	Posts["CommentCount"] = []
	Posts["OwnerUserId"] = []
	Posts["LastEditorUserId"] = []
	if PostTypeId == 1:
		# question
		Posts["QuestionId"] = []
		Posts["ViewCount"] = []
		Posts["Title"] = []
		Posts["Tags"] = []
		Posts["AnswerCount"] = []
		Posts["AcceptedAnswerId"] = []
	else:
		# answer
		Posts["AnswerId"] = []
		Posts["QuestionId"] = []
	return Posts

def posts_processing(file_name):
	Questions = init_posts(PostTypeId = 1)
	Answers = init_posts(PostTypeId = 2)
	
	for event,elem in ET.iterparse(file_name):
		if event == "end":
			try:
				#print elem.tag,elem.attrib
				process_element(Questions,elem,PostTypeId = 1)
				process_element(Answers,elem,PostTypeId = 2)
				elem.clear()
			except Exception as e:
				pass
				#print("Exception: %s" % e)

	dir_path = os.path.dirname(os.path.abspath(file_name))
	
	questions_file = os.path.join(dir_path,"Questions.pkl")

	process_QuestionId_AskerId(dir_path,Questions)
	process_QuestionId_AcceptedAnswerId(dir_path,Questions)
	process_AnswerId_QuestionId(dir_path,Answers)
	process_AnswerId_AnswererId(dir_path,Answers)
	questionid_answererid(dir_path)
	questionid_bestanswererid(dir_path)
	askerid_answererid(dir_path)
	process_question_tags(dir_path,Questions)
	process_answer_body(dir_path,Answers)
	process_question_text(dir_path,Questions)

if __name__ == "__main__":
	'''
	process */Posts.xml
	'''
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "../dataset/ai/Posts.xml", help = "input: */Posts.xml, output: *.csv")
	args = parser.parse_args()
	input_file = args.input
	print("processing input file %s " % input_file)
	posts_processing(input_file)
