def format_creationDate(creationDate):
	'''
	CreationDate="2016-08-02T15:39:14.947"
	'''
	dates = creationDate.split("T")[0]
	times = creationDate.split("T")[1]
	y,mo,d = dates.split("-")
	h,mi,_ = times.split(":")
	return int(y),int(mo),int(d),int(h),int(mi)
