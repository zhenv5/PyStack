try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

import os.path
import pandas as pd
import argparse


def duplicte_questions(cate_name):
	df = pd.read_csv(os.path.join(cate_name,"PostId_RelatedPostId.csv"))
	result = df.groupby("LinkTypeId")
	q1 = []
	q2 = []
	for k,v in result:
		d = pd.DataFrame({"QuestionId":v["PostId"],"RelatedQuestionId":v["RelatedPostId"]})
		if k == 3:
			print("Processing duplicate questions...")
			print("# duplicate questions: %d" % len(d))
			file_name = "Duplicate_Questions.csv"
		if k == 1:
			print("Processing related questions...")
			print("# related questions: %d" % len(d))
			file_name = "Related_Questions_Source2Target.csv"

		d.to_csv(os.path.join(cate_name,file_name),index = False, columns = ["QuestionId","RelatedQuestionId"])
		print("file saved to: %s" % file_name)
	print("***********************************")

def postlinks_processing(input_file):
	d = {"PostId":[],"RelatedPostId":[],"LinkTypeId":[]}
	for event,elem in ET.iterparse(input_file):
			if event == "end":
				try:
					postid = int(elem.attrib["PostId"])
					relatedpostid = int(elem.attrib["RelatedPostId"])
					linktypeid = int(elem.attrib["LinkTypeId"])
					d["PostId"].append(postid)
					d["RelatedPostId"].append(relatedpostid)
					d["LinkTypeId"].append(linktypeid)
					#print elem.tag,elem.attrib
					elem.clear()
				except Exception as e:
					pass
					#print e
	#file_dir = os.path.dirname(input_file)
	file_dir = os.path.dirname(os.path.abspath(input_file))
	postid_relatedpostid_file = os.path.join(file_dir,"PostId_RelatedPostId.csv")
	
	df1 = pd.DataFrame(d)
	df1.to_csv(postid_relatedpostid_file,index = True, columns = ["PostId","RelatedPostId","LinkTypeId"])
	print("***********************************")
	print("output file: %s" % postid_relatedpostid_file)
	duplicte_questions(file_dir)

if __name__ == "__main__":
	'''
	process */PostLinks.xml
	'''
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "dataset/ai/PostLinks.xml", help = "input: */PostLinks.xml, output: */Comments.csv")
	args = parser.parse_args()
	input_file = args.input
	print("input file %s " % input_file)
	postlinks_processing(input_file)