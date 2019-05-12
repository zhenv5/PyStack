# PyStack: Powerful Python Toolkit for Analyzing Stack Exchange Sites

This tooklit provides several useful Python scripts for processing [stack exchange data dump](https://archive.org/details/stackexchange)

## Requirements

* Python 2.7
* [pandas](http://pandas.pydata.org/)
* [xml.etree.ElementTree](https://docs.python.org/2/library/xml.etree.elementtree.html)
* [cPickle or pickle](https://docs.python.org/3/library/pickle.html)

## PyStack

### Usage

* download your interested Stack Exchange site data (*.stackexchange.com.7z) from [stack exchange data dump](https://archive.org/details/stackexchange), such as ```ai.stackexchange.com.7z```
* unzip ```ai.stackexchange.com.7z``` to directory: ```dataset/ai```
* ```cd pre_precessing```
* execute: ```python pystack.py --input ../dataset/ai/ --task all```

#### Parameters of ```pystack.py```

* input: file directory which saves Posts.xml, PostLinks.xml, Votes.xml, Badges.xml, and Comments.xml. In above example, input is ```dataset/ai```
* task: can be selected from [Posts, PostLinks, Votes, Badges, Comments, and All], Each task corresponding a python file. By default, task is set as ```all```.

#### Outputs of ```pystack.py```

* Outputs will be saved in corresponding ```.csv``` and ```.pkl```.
* Analysis/Statistics of the Stack Exchange Site will be saved in file ```pystack_analysis.log```.
* We will describe the details in each task individually.

### Process Posts.xml

#### Usage

```
python process_posts.py --input ../dataset/ai/Posts.xml
```

OR

```
python pystack.py --input ../dataset/ai/ --task Posts
```

#### Output

* QuestionId_AskerId.csv
* QuestionId_AnswererId.csv
* QuestionId_AcceptedAnswererId.csv
* AnswerId_QuestionId.csv
* AnswerId_AnswererId.csv
* AskerId_AnswererId.csv
* question_tags.pkl: A dict pickle file, of which key is question id, and its value is a list of tags
* Questions.pkl: A dict pickle file, of which key is question id, and its value is a list of [question title, question body]
* Answers.pkl: A dict pickle file, of which key is answer id, and its value is corresponding body

### Process PostLinks.xml

#### Usage 

```
python process_postlinks.py --input ../dataset/ai/PostLinks.xml
```

OR

```
python pystack.py --input ../dataset/ai/ --task PostLinks
```

#### Output

* PostId_RelatedPostId.csv: PostId -> RelatedPostId if LinkTypeId = 1; PostId is a duplicate of RelatedPostId if LinkTypedId = 3
* Duplicate_Questions.csv: Duplicate question pairs
* Related_Questions_Source2Target.csv: There is a link from a souce question to a target question

### Process Votes.xml

#### Usage

```
python process_votes.py --input ../dataset/ai/Votes.xml
```

OR

```
python pystack.py --input ../dataset/ai/ --task Votes
```


#### Output

* QuestionId_Bounty.csv: columns = ["QuestionId","Bounty"], index = False

### Process Badges.xml

#### Usage

```
python process_badges.py --input ../dataset/ai/Badges.xml
```

OR

```
python pystack.py --input ../dataset/ai/ --task Badges
```

#### Output

* Badges.csv, columns = ["UserId","BadgeName","BadgeDate"], index = False

### Process Comments.xml

#### Usage

```
python process_comments.py --input ../dataset/ai/Comments.xml
```

OR

```
python pystack.py --input ../dataset/ai/ --task Comments
```

#### Output

* PostId_CommenterId.csv: index = False, columns = ["PostId","UserId","Score"], UserId gave a comment on PostId (Question or Answer(?)). And the number of up-votes he/she get is Score
* PostId_CommenterId_Text.pkl: d = {"PostId":[],"UserId":[],"Score":[],"Text":[],"CreationDate":[]}

## Questions

### How to unzip a *.7z file

* Install ```p7zip``` if not already installed: ```sudo apt-get install p7zip```
* To install the command line utility ```sudp atp-get install p7zip-full```
* Or [Install p7zip on Mac OSX](http://macappstore.org/p7zip/)
* execute command to extract a *.7z file: ```7za x *.7z```

## Discuss

This code is written for research. It aims to help you start to do your analysi on Stack Exchange Sites without the dirty preprocessing work. 

Feel free to post any questions or comments.

## Citation

If you use this code, please consider to cite [QDEE: Question Difficulty and Expertise Estimation in Community Question Answering Sites](https://github.com/zhenv5/QDEE) and [ColdRoute: effective routing of cold questions in stack exchange sites
](https://link.springer.com/article/10.1007%2Fs10618-018-0577-7)
