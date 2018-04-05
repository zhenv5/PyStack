try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

from nltk import word_tokenize
from nltk.corpus import stopwords
import string
from nltk.stem.wordnet import WordNetLemmatizer
import pandas as pd
import os.path
from collections import Counter


def embedding_mapping_between_answer_and_user(cate_name,feature_dict):
	df = pd.read_csv(os.path.join(cate_name,"QuestionId_AnswererId.csv"))
	ques = df["QuestionId"]
	ans = df["AnswerId"]
	user = df["AnswererId"]
	
	user_dict_question_answer = {}
	for q,a,u in zip(ques,ans,user):
		if u not in user_dict_question_answer:
			user_dict_question_answer[u] = {}
		user_dict_question_answer[u][q] = feature_dict[a]
	return user_dict_question_answer


def clean(doc):

	############
	############
	############
	#import nltk
	#nltk.download()
	# select Corpora/wordnet and Corpora/stopwords to download
	############
	############
	############
	doc = remove_symbols(doc)
	stop = set(stopwords.words('english'))
	exclude = set(string.punctuation) 
	lemma = WordNetLemmatizer()
   	stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
	punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
	normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
	return normalized

#doc_clean = [clean(doc).split() for doc in doc_complete]


def remove_symbols(s):
	s = s.replace("<p>"," ")
	s = s.replace("</p>"," ")
	s = s.replace("<ul>"," ")
	s = s.replace("</ul>", " ")
	s = s.replace("<li>", " ")
	s = s.replace("</li>"," ")
	s = s.replace("\n"," ")

	'''
	import string
	for char in string.punctuation:
		print char
		s.replace(char," ")
	'''
	return s

def posts_processing(file_name,use_question_body = False, use_question_title= True):
	questions = {}
	answers = {}
	users = {}
	owners = []
	#stop = stopwords.words('english') + list(string.punctuation)
	
	for event,elem in ET.iterparse(file_name):
		if event == "end":
			try:
				index = int(elem.attrib["Id"])
				posttypeid = int(elem.attrib["PostTypeId"])
				owneruserid = int(elem.attrib["OwnerUserId"])
				owners.append(owneruserid)
				text = elem.attrib["Body"]
				#text = remove_symbols(text)
				text = clean(text)
				if posttypeid == 1:
					# question
					title = elem.attrib["Title"]
					#title = remove_symbols(title)
					title = clean(title)

					tags = " ".join([tag[1:] for tag in elem.attrib["Tags"].split(">") if len(tag) > 0])
					
					if use_question_title and use_question_body:
						# use question body and title
						text = " ".join((text,title))
						questions[index] = text
					else:
						if use_question_body:				
							# only use question body
							questions[index] = text
						elif use_question_title:
							# only use question title
							questions[index] = title
						else:
							questions[index] = {}
				else:
					#text = " ".join([i for i in word_tokenize(text.lower()) if i not in stop])
					answers[index] = text
					if owneruserid in users:
						users[owneruserid] += text 
						#users[owneruserid] = " ".join((users[owneruserid],text))
					else:
						users[owneruserid] = text
				elem.clear()
			except Exception as e:
				print e
				#pass
	print("------------------")
	print("# questions: %d" % len(questions))
	print("# answers: %d" % len(answers))
	print("# answerers: %d" % len(users))
	print("# question-answer pairs: %d" % len(owners))
	print("# unique users: %s" % len(set(owners)))
	print("------------------")
	return questions,answers,users


def question_tags(file_name):
	questions = {}
	for event,elem in ET.iterparse(file_name):
		if event == "end":
			try:
				index = int(elem.attrib["Id"])
				posttypeid = int(elem.attrib["PostTypeId"])
				owneruserid = int(elem.attrib["OwnerUserId"])			
				if posttypeid == 1:
					# question
					tags = " ".join([tag[1:] for tag in elem.attrib["Tags"].split(">") if len(tag) > 0])
					
					questions[index] = tags
			except Exception as e:
				#print e
				pass
	print("------------------")
	print("# questions with tags: %d" % len(questions))
	print("------------------")
	return questions


def filter_tokens(text_tokens_dict):
	tokens = []
	for k, v in text_tokens_dict.iteritems():
		tokens += v.keys()
	tokens_c = Counter(tokens)
	#print tokens_c
	tokens_s = set([k for k,v in tokens_c.iteritems() if v >= 2])
	#print tokens_s
	for k,v in text_tokens_dict.iteritems():
		new_v = {}
		for new_k,_ in v.iteritems():
			if new_k in tokens_s:
				new_v[new_k] = 1
		text_tokens_dict[k] = new_v
	return text_tokens_dict


def count_tokens(item_texts_dict,text_prefix,token_filtering=False):
	text_tokens_dict = {}
	for k,v in item_texts_dict.iteritems():
		new_v = Counter(["".join((text_prefix,token)) for token in v.split() if not token.startswith("hrefhttp")])
		
		#text_tokens_dict[k] = new_v
		text_tokens_dict[k] = Counter(new_v.keys())
		#text_tokens_dict[k] = new_v

	if token_filtering:
		text_tokens_dict = filter_tokens(text_tokens_dict)
	return text_tokens_dict

def build_tokens(cate_name):
	questions,answers,users = posts_processing(os.path.join(cate_name,"Posts.xml"))
	ques_tags_dict = question_tags(os.path.join(cate_name,"Posts.xml"))
	ques = count_tokens(questions,"q")
	answ = count_tokens(answers,"a")
	user = count_tokens(users,"u")
	ques_tags = count_tokens(ques_tags_dict,"t")
	#print ques_tags
	save_file = os.path.join(cate_name,"posts.pkl")

	with open(save_file,"wb") as f:
		import cPickle as pickle 
		pickle.dump({"questions":ques,"answers":answ,"users":user,"tags":ques_tags},f)

import argparse
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "../dataset/bitcoin", help = "input category name")
	args = parser.parse_args()
	build_tokens(args.input)

