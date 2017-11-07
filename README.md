# PyStack: Powerful Python Toolkit for Analyzing Stack Exchange Sites

This tooklit provides several useful Python scripts for processing [stack exchange data dump](https://archive.org/details/stackexchange)

## Requirements

* Python 2.7
* [pandas](http://pandas.pydata.org/)
* [xml.etree.ElementTree](https://docs.python.org/2/library/xml.etree.elementtree.html)
* [cPickle or pickle](https://docs.python.org/3/library/pickle.html)

## PyStack

### Usage

```
python pystack.py --input dataset/ai/ --task all
```

* input: file directory which saves Posts.xml, PostLinks.xml, Votes.xml, Badges.xml, and Comments.xml
* task: can be selected from [Posts, PostLinks, Votes, Badges, Comments, and All], Each task corresponding a python file

### Output

* Outputs will be saved in corresponding ```.csv``` and ```.pkl```.
We will describe each task individually.

### Process Posts.xml

#### Usage

```
python process_posts.py --input dataset/bitcoin/Posts.xml
```

#### Output

* QuestionId_AskerId.csv
* QuestionId_AnswererId.csv
* QuestionId_AcceptedAnswererId.csv
* ...
* question_tags.pkl: A dict pickle file, of which key is question id, and its value is a list of tags


### Process PostLinks.xml

#### Usage 

```
python process_postlinks.py --input dataset/bitcoin/PostLinks.xml
```

#### Output

* PostId_RelatedPostId.csv: PostId -> RelatedPostId if LinkTypeId = 1; PostId is a duplicate of RelatedPostId if LinkTypedId = 3
* Duplicate_Questions.csv: Duplicate question pairs
* Related_Questions_Source2Target.csv: There is a link from a souce question to a target question

### Process Votes.xml

#### Usage

```
python process_votes.py --input dataset/ai/Votes.xml
```

#### Output

* QuestionId_Bounty.csv: columns = ["QuestionId","Bounty"], index = False

### Process Badges.xml

#### Usage

```
python process_badges.py --input dataset/ai/Badges.xml
```

#### Output

* Badges.csv, columns = ["UserId","BadgeName","BadgeDate"], index = False



### Process Comments.xml

#### Usage

```
python process_comments.py --input dataset/ai/Comments.xml
```

#### Output

* PostId_CommenterId.csv: index = False, columns = ["PostId","UserId","Score"], UserId gave a comment on PostId (Question or Answer(?)). And the number of up-votes he/she get is Score
* PostId_CommenterId_Text.pkl: d = {"PostId":[],"UserId":[],"Score":[],"Text":[],"CreationDate":[]}

