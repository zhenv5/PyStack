from gensim import corpora, models
import gensim
import os.path
from semantic_core import embedding_mapping_between_answer_and_user
from scipy.sparse import csr_matrix
import cPickle as pickle

def embedding(lda_model,dictionary,corpus,num_topics):
	emb_dict = {}
	for q,v in corpus.iteritems():
		dist = lda_model[dictionary.doc2bow(v.split())]
		emb_dict[q] = [0] * num_topics
		for index,v in dist:
			emb_dict[q][index] = v
		emb_dict[q] = csr_matrix(emb_dict[q])
	return emb_dict

def lda_embedding(cate_name,num_topics = 5):
	from semantic_core import posts_processing
	questions,answers,users = posts_processing(os.path.join(cate_name,"Posts.xml"))
	texts = questions.values() + answers.values()
	texts = [text.split() for text in texts]
	#print texts
	# turn our tokenized documents into a id <-> term dictionary
	dictionary = corpora.Dictionary(texts)
	#print dictionary
	dictionary.filter_extremes(no_below=3, no_above=0.3)
	#print dictionary
	# convert tokenized documents into a document-term matrix
	corpus = [dictionary.doc2bow(text) for text in texts]
	# generate LDA model
	ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics= num_topics, id2word = dictionary, passes=20)
	
	ques_dict = embedding(ldamodel,dictionary, questions,num_topics)
	answer_dict = embedding(ldamodel,dictionary, answers,num_topics)
	# 100 -> 200
	print(ldamodel.print_topics(num_topics=num_topics, num_words=5))

	user_dict = embedding_mapping_between_answer_and_user(cate_name,answer_dict)
	
	print("# embeddings for questions, answers, users: %d, %d, %d" % (len(ques_dict),len(answer_dict),len(user_dict)))

	with open(os.path.join(cate_name,"question_lda.pkl"),"wb") as f:
		pickle.dump(ques_dict,f)
	with open(os.path.join(cate_name,"answer_lda.pkl"),"wb") as f:
		pickle.dump(answer_dict,f)
	with open(os.path.join(cate_name,"user_lda.pkl"),"wb") as f:
		pickle.dump(user_dict,f)

import argparse
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "../dataset/ai", help = "input category name")
	parser.add_argument("-n","--number_topics",default = 200, help = "number of topics")
	args = parser.parse_args()
	lda_embedding(args.input,num_topics = args.number_topics)