# -*- coding: utf-8 -*-
"""
Statistics for topic models and BoW matrices (doc-term-matrices).

Markus Konrad <markus.konrad@wzb.eu>
"""
from __future__ import division

import itertools

import numpy as np
from scipy.sparse import issparse


#%% Common statistics from BoW matricses


def get_doc_lengths(dtm):
    if isinstance(dtm, np.matrix):
        dtm = dtm.A
    if dtm.ndim != 2:
        raise ValueError('`dtm` must be a 2D array/matrix')

    res = np.sum(dtm, axis=1)
    if res.ndim != 1:
        return res.A.flatten()
    else:
        return res


def get_doc_frequencies(dtm, min_val=1, proportions=False):
    """
    For each word in the vocab of `dtm` (i.e. its columns), return how often it occurs at least `min_val` times.
    If `proportions` is True, return proportions scaled to the number of documents instead of absolute numbers.
    """
    if dtm.ndim != 2:
        raise ValueError('`dtm` must be a 2D array/matrix')

    doc_freq = np.sum(dtm >= min_val, axis=0)

    if doc_freq.ndim != 1:
        doc_freq = doc_freq.A.flatten()

    if proportions:
        return doc_freq / dtm.shape[0]
    else:
        return doc_freq


def get_codoc_frequencies(dtm, min_val=1, proportions=False):
    """
    For each unique pair of words `w1, w2` in the vocab of `dtm` (i.e. its columns), return how often both occur
    together at least `min_val` times. If `proportions` is True, return proportions scaled to the number of documents
    instead of absolute numbers.
    """
    if dtm.ndim != 2:
        raise ValueError('`dtm` must be a 2D array/matrix')

    n_docs, n_vocab = dtm.shape
    if n_vocab < 2:
        raise ValueError('`dtm` must have at least two columns (i.e. 2 unique words)')

    word_in_doc = dtm >= min_val

    codoc_freq = {}
    for w1, w2 in itertools.combinations(range(n_vocab), 2):
        if issparse(dtm):
            w1_in_docs = word_in_doc[:, w1].A.flatten()
            w2_in_docs = word_in_doc[:, w2].A.flatten()
        else:
            w1_in_docs = word_in_doc[:, w1]
            w2_in_docs = word_in_doc[:, w2]

        freq = np.sum(w1_in_docs & w2_in_docs)
        if proportions:
            freq /= n_docs
        codoc_freq[(w1, w2)] = freq

    return codoc_freq


def get_term_frequencies(dtm):
    if isinstance(dtm, np.matrix):
        dtm = dtm.A
    if dtm.ndim != 2:
        raise ValueError('`dtm` must be a 2D array/matrix')

    res = np.sum(dtm, axis=0)
    if res.ndim != 1:
        return res.A.flatten()
    else:
        return res


def get_term_proportions(dtm):
    """
    Return the term proportions given the document-term matrix `dtm`
    """
    unnorm = get_term_frequencies(dtm)

    if unnorm.sum() == 0:
        raise ValueError('`dtm` does not contain any tokens (is all-zero)')
    else:
        return unnorm / unnorm.sum()


#%% Common statistics from topic-word or document-topic distribution


def get_marginal_topic_distrib(doc_topic_distrib, doc_lengths):
    """
    Return marginal topic distribution p(T) (topic proportions) given the document-topic distribution (theta)
    `doc_topic_distrib` and the document lengths `doc_lengths`. The latter can be calculated with `get_doc_lengths()`.
    """
    unnorm = (doc_topic_distrib.T * doc_lengths).sum(axis=1)
    return unnorm / unnorm.sum()


def get_marginal_word_distrib(topic_word_distrib, p_t):
    """
    Return the marginal word distribution p(w) (term proportions derived from topic model) given the
    topic-word distribution (phi) `topic_word_distrib` and the marginal topic distribution p(T) `p_t`.
    The latter can be calculated with `get_marginal_topic_distrib()`.
    """
    return (topic_word_distrib.T * p_t).sum(axis=1)


#%% General scores functions


def _words_by_score(words, score, least_to_most, n=None):
    """
    Order a vector of `words` by a `score`, either `least_to_most` or reverse. Optionally return only the top `n`
    results.
    """
    if words.shape != score.shape:
        raise ValueError('`words` and `score` must have the same shape')

    if n is not None and (n <= 0 or n > len(words)):
        raise ValueError('`n` must be in range [0, len(words)]')

    indices = np.argsort(score)
    if not least_to_most:
        indices = indices[::-1]

    ordered_words = words[indices]

    if n is not None:
        return ordered_words[:n]
    else:
        return ordered_words


#%% Saliency (Chuang et al. 2012)


def get_word_saliency(topic_word_distrib, doc_topic_distrib, doc_lengths):
    """
    Calculate word saliency according to Chuang et al. 2012.
    saliency(w) = p(w) * distinctiveness(w)
    """
    p_t = get_marginal_topic_distrib(doc_topic_distrib, doc_lengths)
    p_w = get_marginal_word_distrib(topic_word_distrib, p_t)

    return p_w * get_word_distinctiveness(topic_word_distrib, p_t)


def _words_by_salience_score(vocab, topic_word_distrib, doc_topic_distrib, doc_lengths, n=None, least_to_most=False):
    """Return words in `vocab` ordered by saliency score."""
    saliency = get_word_saliency(topic_word_distrib, doc_topic_distrib, doc_lengths)
    return _words_by_score(vocab, saliency, least_to_most=least_to_most, n=n)


def get_most_salient_words(vocab, topic_word_distrib, doc_topic_distrib, doc_lengths, n=None):
    """
    Order the words from `vocab` by "saliency score" (Chuang et al. 2012) from most to least salient. Optionally only
    return the `n` most salient words.
    """
    return _words_by_salience_score(vocab, topic_word_distrib, doc_topic_distrib, doc_lengths, n)


def get_least_salient_words(vocab, topic_word_distrib, doc_topic_distrib, doc_lengths, n=None):
    """
    Order the words from `vocab` by "saliency score" (Chuang et al. 2012) from least to most salient. Optionally only
    return the `n` least salient words.
    """
    return _words_by_salience_score(vocab, topic_word_distrib, doc_topic_distrib, doc_lengths, n, least_to_most=True)


#%% Distinctiveness (Chuang et al. 2012)


def get_word_distinctiveness(topic_word_distrib, p_t):
    """
    Calculate word distinctiveness according to Chuang et al. 2012.
    distinctiveness(w) = KL(P(T|w), P(T)) = sum_T(P(T|w) log(P(T|w)/P(T)))
    with P(T) .. marginal topic distribution
         P(T|w) .. prob. of a topic given a word
    """
    topic_given_w = topic_word_distrib / topic_word_distrib.sum(axis=0)
    return (topic_given_w * np.log(topic_given_w.T / p_t).T).sum(axis=0)


def _words_by_distinctiveness_score(vocab, topic_word_distrib, doc_topic_distrib, doc_lengths, n=None,
                                    least_to_most=False):
    """Return words in `vocab` ordered by distinctiveness score."""
    p_t = get_marginal_topic_distrib(doc_topic_distrib, doc_lengths)
    distinct = get_word_distinctiveness(topic_word_distrib, p_t)

    return _words_by_score(vocab, distinct, least_to_most=least_to_most, n=n)


def get_most_distinct_words(vocab, topic_word_distrib, doc_topic_distrib, doc_lengths, n=None):
    """
    Order the words from `vocab` by "distinctiveness score" (Chuang et al. 2012) from most to least distinctive.
    Optionally only return the `n` most distinctive words.
    """
    return _words_by_distinctiveness_score(vocab, topic_word_distrib, doc_topic_distrib, doc_lengths, n)


def get_least_distinct_words(vocab, topic_word_distrib, doc_topic_distrib, doc_lengths, n=None):
    """
    Order the words from `vocab` by "distinctiveness score" (Chuang et al. 2012) from least to most distinctive.
    Optionally only return the `n` least distinctive words.
    """
    return _words_by_distinctiveness_score(vocab, topic_word_distrib, doc_topic_distrib, doc_lengths, n,
                                           least_to_most=True)


#%% Relevance (Sievert and Shirley 2014)


def get_topic_word_relevance(topic_word_distrib, doc_topic_distrib, doc_lengths, lambda_):
    """
    Calculate the topic-word relevance score with a lambda parameter `lambda_` according to Sievert and Shirley 2014.
    relevance(w,T|lambda) = lambda * log phi_{w,t} + (1-lambda) * log (phi_{w,t} / p(w))
    with phi  .. topic-word distribution
         p(w) .. marginal word probability
    """
    p_t = get_marginal_topic_distrib(doc_topic_distrib, doc_lengths)
    p_w = get_marginal_word_distrib(topic_word_distrib, p_t)

    logtw = np.log(topic_word_distrib)
    loglift = np.log(topic_word_distrib / p_w)

    return lambda_ * logtw + (1-lambda_) * loglift


def _check_relevant_words_for_topic_args(vocab, rel_mat, topic):
    if rel_mat.ndim != 2:
        raise ValueError('`rel_mat` must be a 2D array or matrix')

    if len(vocab) != rel_mat.shape[1]:
        raise ValueError('the length of the `vocab` array must match the number of columns in `rel_mat`')

    if not 0 <= topic < rel_mat.shape[0]:
        raise ValueError('`topic` must be a topic index in range [0,%d)' % rel_mat.shape[0])


def get_most_relevant_words_for_topic(vocab, rel_mat, topic, n=None):
    """
    Get words from `vocab` for `topic` ordered by most to least relevance (Sievert and Shirley 2014) using the relevance
    matrix `rel_mat` obtained from `get_topic_word_relevance()`.
    Optionally only return the `n` most relevant words.
    """
    _check_relevant_words_for_topic_args(vocab, rel_mat, topic)
    return _words_by_score(vocab, rel_mat[topic], least_to_most=False, n=n)


def get_least_relevant_words_for_topic(vocab, rel_mat, topic, n=None):
    """
    Get words from `vocab` for `topic` ordered by least to most relevance (Sievert and Shirley 2014) using the relevance
    matrix `rel_mat` obtained from `get_topic_word_relevance()`.
    Optionally only return the `n` least relevant words.
    """
    _check_relevant_words_for_topic_args(vocab, rel_mat, topic)
    return _words_by_score(vocab, rel_mat[topic], least_to_most=True, n=n)


#%% Other functions


def generate_topic_labels_from_top_words(topic_word_distrib, doc_topic_distrib, doc_lengths, vocab,
                                         n_words=None, lambda_=1, labels_glue='_', labels_format='{i1}_{topwords}'):
    """
    Generate topic labels derived from the top words of each topic. The top words are determined from the
    relevance score (Sievert and Shirley 2014) depending on `lambda_`. Specify the number of top words in the label
    with `n_words`. If `n_words` is None, a minimum number of words will be used to create unique labels for each
    topic. Topic labels are formed by joining the top words with `labels_glue` and formatting them with
    `labels_format`. Placeholders in `labels_format` are `{i0}` (zero-based topic index),
    `{i1}` (one-based topic index) and `{topwords}` (top words glued with `labels_glue`).
    """
    rel_mat = get_topic_word_relevance(topic_word_distrib, doc_topic_distrib, doc_lengths, lambda_=lambda_)

    if n_words is None:
        n_words = range(1, len(vocab)+1)
    else:
        if not 1 <= n_words <= len(vocab):
            raise ValueError('`n_words` must be in range [1, %d]' % len(vocab))

        n_words = range(n_words, n_words+1)

    most_rel_words = [tuple(get_most_relevant_words_for_topic(vocab, rel_mat, t))
                      for t in range(topic_word_distrib.shape[0])]

    n_most_rel = []
    for n in n_words:
        n_most_rel = [ws[:n] for ws in most_rel_words]
        if len(n_most_rel) == len(set(n_most_rel)):   # we have a list of unique word sequences
            break

    assert n_most_rel

    topic_labels = [labels_format.format(i0=i, i1=i+1, topwords=labels_glue.join(ws))
                    for i, ws in enumerate(n_most_rel)]

    if len(topic_labels) != len(set(topic_labels)):
        raise ValueError('generated labels are not unique')

    return topic_labels