### Applications

#### Build Temporal CQA Graph

* Graph nodes: users (asker, answerer), edges: from asker to answerer
* Usage: ```python build_temporal_graph.py --input ../dataset/ai --initial_date 2018-01-01T15:39:14.947 --interval_by_days 30```
* ```--input```: input stack exchange site, File ```AskerId_AnswererId.csv``` is required. Make sure to run ```pre_processing/pystack.py``` first ([check how to pre-processing Stack Exchange sites](https://github.com/zhenv5/PyStack/blob/master/README.md))
* ```--initial_date```: initial date
* ```--interval_by_days```: interval_by_days to update the initial graph

Output:

* ```AskerIndex_AnswererIndex_2018-01-01_interval_by_month_-1.csv```: initial graph,  all interactions (asker -> answerer) generated before ```initial_date``` are used to construct the initial graph
* ```AskerIndex_AnswererIndex_2018-01-01_interval_by_month_n.csv```: newly added edges between (```initial_date``` + ```interval_by_days``` X (n)) and (```initial_date``` + ```interval_by_days``` X (n+1))
* Nodes which are not in the initial graph are not included in the updated csv (n >= 0)
* ```AskerIndex_AnswererIndex_....csv``` format: ```AskerIndex, AnswererIndex``` per row. Node index starts from 0