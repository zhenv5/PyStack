import argparse
import os.path

def preprocessing_main(cate_name,task_name):
	task_name = task_name.lower()
	if task_name == "posts" or task_name == "all":
		from process_posts import posts_processing
		posts_processing(os.path.join(cate_name,"Posts.xml"))
	if task_name == "postlinks" or task_name == "all":
		from process_postlinks import postlinks_processing
		postlinks_processing(os.path.join(cate_name,"PostLinks.xml"))
	if task_name == "votes" or task_name == "all":
		from process_votes import bounty_processing
		bounty_processing(os.path.join(cate_name,"Votes.xml"))
	if task_name == "badges":
		from process_badges import badges_processing
		badges_processing(os.path.join(cate_name,"Badges.xml"))
	if task_name == "comments":
		from process_comments import comments_processing
		comments_processing(os.path.join(cate_name,"Comments.xml"))

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--input",default= "../dataset/ai", help = "input category name")
	parser.add_argument("-t","--task",default= "all", help = "task names: Posts, PostLinks, Votes, Badges, Comments, and All")
	args = parser.parse_args()
	preprocessing_main(args.input,args.task)
