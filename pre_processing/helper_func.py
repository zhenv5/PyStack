import os.path

def sprint(dir_name,file_name,line):
	print line
	with open(os.path.join(dir_name,file_name),"a") as f:
		f.write("%s \n" % line)