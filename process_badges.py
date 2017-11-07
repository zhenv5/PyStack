try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

import os.path
import pandas as pd
import argparse
from helper_func import sprint

def badges_processing(file_name):
	index = []
	UserId = [] 
	BadgeName = []
	BadgeDate = []

	for event,elem in ET.iterparse(file_name):
		if event == "end":
			try:
				#print elem.tag,elem.attrib
				ind = int(elem.attrib["Id"])
				userid = int(elem.attrib["UserId"])
				badgename = elem.attrib["Name"]
				badgedate = elem.attrib["Date"]
				#print ind,userid,badgename,badgedate
				index.append(ind)
				UserId.append(userid)
				BadgeName.append(badgename)
				BadgeDate.append(badgedate)
				elem.clear()
			except Exception as e:
				pass

	dir_path = os.path.dirname(os.path.abspath(file_name))
	output_file = os.path.join(dir_path,"Badges.csv")
	print("output file: %s" % output_file)
	df =pd.DataFrame({"UserId":UserId,"BadgeName":BadgeName,"BadgeDate":BadgeDate})
	df.to_csv(output_file,index = False,columns = ["UserId","BadgeName","BadgeDate"])
	sprint(dir_path,"pystack_analysis.log","# users having badges: %d" % len(df))
	

if __name__ == "__main__":
	'''
	process */Badges.xml
	'''
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "dataset/ai/Badges.xml", help = "input: */Badges.xml, output: */Badges.csv")
	args = parser.parse_args()
	input_file = args.input
	print("input file %s " % input_file)
	badges_processing(input_file)
