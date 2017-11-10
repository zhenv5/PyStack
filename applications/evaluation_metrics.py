# (C) Mathieu Blondel, November 2013
# License: BSD 3 clause

import numpy as np

from scipy import stats
def pearson(x,y):
    v,p = stats.pearsonr(x,y)
    
    print("# elements: %d, pearson correlation: %0.6f, p-value: %0.6f" % (len(x),v,p))
    return v


def ranking_precision_score(y_true, y_score, k=10):
    """Precision at rank k

    Parameters
    ----------
    y_true : array-like, shape = [n_samples]
        Ground truth (true relevance labels).

    y_score : array-like, shape = [n_samples]
        Predicted scores.

    k : int
        Rank.

    Returns
    -------
    precision @k : float
    """
    unique_y = np.unique(y_true)

    if len(unique_y) > 2:
        raise ValueError("Only supported for two relevance levels.")

    pos_label = unique_y[1]
    n_pos = np.sum(y_true == pos_label)

    order = np.argsort(y_score)[::-1]
    y_true = np.take(y_true, order[:k])
    n_relevant = np.sum(y_true == pos_label)

    # Divide by min(n_pos, k) such that the best achievable score is always 1.0.
    return float(n_relevant) / min(n_pos, k)


def average_precision_score(y_true, y_score, k=10):
    """Average precision at rank k

    Parameters
    ----------
    y_true : array-like, shape = [n_samples]
        Ground truth (true relevance labels).

    y_score : array-like, shape = [n_samples]
        Predicted scores.

    k : int
        Rank.

    Returns
    -------
    average precision @k : float
    """
    unique_y = np.unique(y_true)

    if len(unique_y) > 2:
        raise ValueError("Only supported for two relevance levels.")

    pos_label = unique_y[1]
    n_pos = np.sum(y_true == pos_label)

    order = np.argsort(y_score)[::-1][:min(n_pos, k)]
    y_true = np.asarray(y_true)[order]

    score = 0
    for i in xrange(len(y_true)):
        if y_true[i] == pos_label:
            # Compute precision up to document i
            # i.e, percentage of relevant documents up to document i.
            prec = 0
            for j in xrange(0, i + 1):
                if y_true[j] == pos_label:
                    prec += 1.0
            prec /= (i + 1.0)
            score += prec

    if n_pos == 0:
        return 0

    return score / n_pos


def dcg_score(y_true, y_score, k=10, gains="exponential"):
    """Discounted cumulative gain (DCG) at rank k

    Parameters
    ----------
    y_true : array-like, shape = [n_samples]
        Ground truth (true relevance labels).

    y_score : array-like, shape = [n_samples]
        Predicted scores.

    k : int
        Rank.

    gains : str
        Whether gains should be "exponential" (default) or "linear".

    Returns
    -------
    DCG @k : float
    """
    order = np.argsort(y_score)[::-1]
    y_true = np.take(y_true, order[:k])
    if gains == "exponential":
        gains = 2 ** y_true - 1
    elif gains == "linear":
        gains = y_true
    else:
        raise ValueError("Invalid gains option.")

    # highest rank is 1 so +2 instead of +1
    discounts = np.log2(np.arange(len(y_true)) + 2)
    return np.sum(gains / discounts)


def ndcg_score(y_true, y_score, k=10, gains="exponential"):
    """Normalized discounted cumulative gain (NDCG) at rank k

    Parameters
    ----------
    y_true : array-like, shape = [n_samples]
        Ground truth (true relevance labels).

    y_score : array-like, shape = [n_samples]
        Predicted scores.

    k : int
        Rank.

    gains : str
        Whether gains should be "exponential" (default) or "linear".

    Returns
    -------
    NDCG @k : float
    """
    best = dcg_score(y_true, y_true, k, gains)
    actual = dcg_score(y_true, y_score, k, gains)
    return actual / best

def rndcg_score(y_true, y_score, k=10, gains="exponential"):
    """Relative Normalized discounted cumulative gain (NDCG) at rank k

    Parameters
    ----------
    y_true : array-like, shape = [n_samples]
        Ground truth (true relevance labels).

    y_score : array-like, shape = [n_samples]
        Predicted scores.

    k : int
        Rank.

    gains : str
        Whether gains should be "exponential" (default) or "linear".

    Returns
    -------
    NDCG @k : float
    """
    best = dcg_score(y_true, y_true, k, gains)
    worst = dcg_score(y_true,[-y for y in y_true],k,gains)
    actual = dcg_score(y_true, y_score, k, gains)
    return (actual - worst) / (best - worst)

# Alternative API.

def dcg_from_ranking(y_true, ranking):
    """Discounted cumulative gain (DCG) at rank k

    Parameters
    ----------
    y_true : array-like, shape = [n_samples]
        Ground truth (true relevance labels).

    ranking : array-like, shape = [k]
        Document indices, i.e.,
            ranking[0] is the index of top-ranked document,
            ranking[1] is the index of second-ranked document,
            ...

    k : int
        Rank.

    Returns
    -------
    DCG @k : float
    """
    y_true = np.asarray(y_true)
    ranking = np.asarray(ranking)
    rel = y_true[ranking]
    gains = 2 ** rel - 1
    discounts = np.log2(np.arange(len(ranking)) + 2)
    return np.sum(gains / discounts)


def ndcg_from_ranking(y_true, ranking):
    """Normalized discounted cumulative gain (NDCG) at rank k

    Parameters
    ----------
    y_true : array-like, shape = [n_samples]
        Ground truth (true relevance labels).

    ranking : array-like, shape = [k]
        Document indices, i.e.,
            ranking[0] is the index of top-ranked document,
            ranking[1] is the index of second-ranked document,
            ...

    k : int
        Rank.

    Returns
    -------
    NDCG @k : float
    """
    k = len(ranking)
    best_ranking = np.argsort(y_true)[::-1]
    best = dcg_from_ranking(y_true, best_ranking[:k])
    return dcg_from_ranking(y_true, ranking) / best


def kendall_tau(x1,x2):
    '''
    input: 
        x1: ground truth
        x2: predicted_ranking_value
    output: kendall tau correlation coefficient
    '''
    import scipy.stats as stats
    tau, p_value = stats.kendalltau(x1, x2)
    print("tau: %0.4f, p-value: %0.4f" % (tau,p_value))
    return tau 



def pairwise_accuracy_risky(x1,x2):
    '''
    input: 
        x1: ground truth
        x2: predicted_ranking_value
    output: pairwise accuracy
    '''
    correct_pairs = 0
    wrong_pairs = 0
    num_gt = len(x1)
    for i in xrange(num_gt - 1):
        for j in xrange(i+1,num_gt):
            if x1[i] != x1[j]:
                if (x2[i] >= x2[j] and x1[i] > x1[j]) or (x2[i] <= x2[j] and x1[i] < x1[j]):
                    correct_pairs += 1
                else:
                    wrong_pairs += 1
    try:
        print("# correct pairs: %d, # wrong pairs: %d, total pairs: %d, precision (Risky): %0.4f" % (correct_pairs,wrong_pairs,correct_pairs + wrong_pairs,correct_pairs*1.0/(wrong_pairs+correct_pairs)))
        return correct_pairs*1.0/(wrong_pairs+correct_pairs)
    except Exception as e:
        print("# of correct pairs: %d, # of wrong pairs: %d" % (correct_pairs,wrong_pairs))
        return None

def pairwise_accuracy_tradition(x1,x2):
    '''
    input: 
        x1: ground truth
        x2: predicted_ranking_value
    output: pairwise accuracy
    '''
    correct_pairs = 0
    wrong_pairs = 0
    num_gt = len(x1)
    for i in xrange(num_gt - 1):
        for j in xrange(i+1,num_gt):
            if (x1[i] != x1[j]) and (x2[j] != x2[i]):
                if (x2[i] > x2[j] and x1[i] > x1[j]) or (x2[i] < x2[j] and x1[i] < x1[j]):
                    correct_pairs += 1
                else:
                    wrong_pairs += 1
    try:
        print("# correct pairs: %d, # wrong pairs: %d, total pairs: %d, precision (tradition): %0.4f" % (correct_pairs,wrong_pairs,correct_pairs + wrong_pairs,correct_pairs*1.0/(wrong_pairs+correct_pairs)))
        return correct_pairs*1.0/(wrong_pairs+correct_pairs)
    except Exception as e:
        print("# of correct pairs: %d, # of wrong pairs: %d" % (correct_pairs,wrong_pairs))
        return None



def pairwise_accuracy(x1,x2):
    '''
    input: 
        x1: ground truth
        x2: predicted_ranking_value
    output: pairwise accuracy
    '''

    acc1 = pairwise_accuracy_tradition(x1,x2)
    acc2 = pairwise_accuracy_risky(x1,x2)
    return acc1,acc2 
   

def pairwise_accuracy_2(ground_truth,predicted_score_dict,nodetype = str):
    
    num_correct_pairs = 0
    num_wrong_pairs = 0

    for gt in ground_truth:
        q1,q2 = gt
        q1 = nodetype(q1)
        q2 = nodetype(q2)
        if predicted_score_dict[q1] <= predicted_score_dict[q2]:
            num_correct_pairs += 1
        else:
            num_wrong_pairs += 1
    accu = num_correct_pairs*1.0/(num_correct_pairs + num_wrong_pairs)
    print("# of correct pairs: %d, # of wrong pairs: %d, accuracy: %0.4f" % (num_correct_pairs,num_wrong_pairs,accu))
    return accu 


def question_difficulty_estimation_evaluation(que_coins_dict,nodes_score_dict):
    
    qid_qgrade = {}
    predicted_qid_qgrade = {}
    
    for k,v in que_coins_dict.iteritems():
        if k in nodes_score_dict:
            qid_qgrade[k] = v
            predicted_qid_qgrade[k] = nodes_score_dict[k]
    
    print("# of questions which have ground truth: %d ?= %d" % (len(qid_qgrade),len(predicted_qid_qgrade)))
    predicted = []
    ground_truth = []

    for k,v in predicted_qid_qgrade.iteritems():
        predicted.append(v)
        ground_truth.append(qid_qgrade[k])

    print("# of questions in ground truth: %d, in predicted set: %d" % (len(ground_truth),len(predicted)))
    
    from letor_metrics import kendall_tau 
    from letor_metrics import pairwise_accuracy
    #print("kendall tau performance: ")
    #kendall_tau(ground_truth,predicted)
    print("pairwise accuracy performance: ")
    pairwise_accuracy(ground_truth,predicted)



if __name__ == '__main__':

    
    x1 = [6,5,4,3,2,1]
    x2 = [1,2,3,4,4,5]
    print rndcg_score(x1,x2,6)
    print ndcg_score(x1,x2,6)
    kendall_tau(x1,x2)
    pairwise_accuracy(x1,x2)

  
    '''
    # Check that some rankings are better than others
    assert dcg_score([5, 3, 2], [2, 1, 0]) > dcg_score([4, 3, 2], [2, 1, 0])
    assert dcg_score([4, 3, 2], [2, 1, 0]) > dcg_score([1, 3, 2], [2, 1, 0])

    assert dcg_score([5, 3, 2], [2, 1, 0], k=2) > dcg_score([4, 3, 2], [2, 1, 0], k=2)
    assert dcg_score([4, 3, 2], [2, 1, 0], k=2) > dcg_score([1, 3, 2], [2, 1, 0], k=2)

    # Perfect rankings
    assert ndcg_score([5, 3, 2], [2, 1, 0]) == 1.0
    assert ndcg_score([2, 3, 5], [0, 1, 2]) == 1.0
    assert ndcg_from_ranking([5, 3, 2], [0, 1, 2]) == 1.0

    assert ndcg_score([5, 3, 2], [2, 1, 0], k=2) == 1.0
    assert ndcg_score([2, 3, 5], [0, 1, 2], k=2) == 1.0
    assert ndcg_from_ranking([5, 3, 2], [0, 1]) == 1.0

    # Check that sample order is irrelevant
    assert dcg_score([5, 3, 2], [2, 1, 0]) == dcg_score([2, 3, 5], [0, 1, 2])

    assert dcg_score([5, 3, 2], [2, 1, 0], k=2) == dcg_score([2, 3, 5], [0, 1, 2], k=2)

    # Check equivalence between two interfaces.
    assert dcg_score([5, 3, 2], [2, 1, 0]) == dcg_from_ranking([5, 3, 2], [0, 1, 2])
    assert dcg_score([1, 3, 2], [2, 1, 0]) == dcg_from_ranking([1, 3, 2], [0, 1, 2])
    assert dcg_score([1, 3, 2], [0, 2, 1]) == dcg_from_ranking([1, 3, 2], [1, 2, 0])
    assert ndcg_score([1, 3, 2], [2, 1, 0]) == ndcg_from_ranking([1, 3, 2], [0, 1, 2])

    assert dcg_score([5, 3, 2], [2, 1, 0], k=2) == dcg_from_ranking([5, 3, 2], [0, 1])
    assert dcg_score([1, 3, 2], [2, 1, 0], k=2) == dcg_from_ranking([1, 3, 2], [0, 1])
    assert dcg_score([1, 3, 2], [0, 2, 1], k=2) == dcg_from_ranking([1, 3, 2], [1, 2])
    assert ndcg_score([1, 3, 2], [2, 1, 0], k=2) == \
            ndcg_from_ranking([1, 3, 2], [0, 1])

    # Precision
    assert ranking_precision_score([1, 1, 0], [3, 2, 1], k=2) == 1.0
    assert ranking_precision_score([1, 1, 0], [1, 0, 0.5], k=2) == 0.5
    assert ranking_precision_score([1, 1, 0], [3, 2, 1], k=3) == \
            ranking_precision_score([1, 1, 0], [1, 0, 0.5], k=3)

    # Average precision
    from sklearn.metrics import average_precision_score as ap
    assert average_precision_score([1, 1, 0], [3, 2, 1]) == ap([1, 1, 0], [3, 2, 1])
    assert average_precision_score([1, 1, 0], [3, 1, 0]) == ap([1, 1, 0], [3, 1, 0])
    '''