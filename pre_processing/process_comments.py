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

def comments_processing(input_file):
	d = {"PostId":[],"UserId":[],"Score":[],"Text":[],"CreationDate":[]}
	for event,elem in ET.iterparse(input_file):
			if event == "end":
				try:
					postid = int(elem.attrib["PostId"])
					userid = int(elem.attrib["UserId"])
					score = int(elem.attrib["Score"])
					creationdate = elem.attrib["CreationDate"]
					text = elem.attrib["Text"]

					d["PostId"].append(postid)
					d["UserId"].append(userid)
					d["Score"].append(score)
					d["CreationDate"].append(creationdate)
					d["Text"].append(text)
					#print elem.tag,elem.attrib
					elem.clear()
				except Exception as e:
					pass
					#print e
	assert len(d["PostId"]) == len(d["UserId"]) and len(d["UserId"]) == len(d["Score"]) and len(d["Score"]) == len(d["CreationDate"]) and len(d["Score"]) == len(d["Text"])
	
	file_dir = os.path.dirname(os.path.abspath(input_file))
	postid_userid_file = os.path.join(file_dir,"PostId_CommenterId.csv")
	comments_file = os.path.join(file_dir,"PostId_CommenterId_Text.pkl")

	df1 = pd.DataFrame(d)
	df1.to_csv(postid_userid_file,index = False, columns = ["PostId","UserId","Score"])
	print("output file: %s" % postid_userid_file)
	sprint(file_dir,"pystack_analysis.log","# PostId-Comment pairs: %d" % len(df1))
	print("output file: %s" % comments_file)
	with open(comments_file,"wb")  as f:
		pickle.dump(d,f)

if __name__ == "__main__":
	'''
	process */Comments.xml
	'''
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "../dataset/ai/Comments.xml", help = "input: */Comments.xml, output: */Comments.csv")
	args = parser.parse_args()
	input_file = args.input
	print("input file %s " % input_file)
	comments_processing(input_file)