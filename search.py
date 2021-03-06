#!/usr/bin/python3
import math
import re
from heapq import *

import sys
import getopt
from shared import index_width, process_doc

# Global variables, dictionary and postings
dictionary = {}
dict_index = {}
postings_size = {}
doc_vectors = {}
pf = None
search_limit = 10
# search_limit = 4


def usage():
    print("usage: " + sys.argv[0] +
          " -d dictionary-file -p postings-file -s sizes-file -q file-of-queries -o output-file-of-results")


def run_search(dict_file, postings_file, sizes_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    # Open files
    global pf
    df = open(dict_file, 'r')
    pf = open(postings_file, 'r')
    qf = open(queries_file, 'r')
    rf = open(results_file, 'w')
    sf = open(sizes_file, 'r')

    # Load dictionary
    count = 0
    dictionary_file_content = df.readlines()
    for word_str in dictionary_file_content:
        word_str = word_str[:-1]
        entries = word_str.split(' ')
        dictionary[entries[0]] = int(entries[1])
        dict_index[entries[0]] = int(entries[2])
        count = count + 1
    # Load postings size
    while True:
        line = sf.readline()
        if not line:
            break
        entries = line[:-1].strip().split(' ')
        postings_size[int(entries[0])] = int(entries[1])
    # Perform searching
    queries = qf.readlines()
    for query in queries:
        res = process_free_query(query)
        if not res:
            rf.write('\n')
            continue
        rf.write(str(res[0]))
        for doc_id in res[1:]:
            rf.write(' ')
            rf.write(str(doc_id))
        rf.write('\n')

    # Close files
    df.close()
    pf.close()
    qf.close()
    rf.close()
    sf.close()


def weight_query(doc_freq, term_freq):
    """
    Calculate the tf-idf weight given tf and df in ltc
    :param doc_freq: df = document frequency > 0
    :param term_freq: tf = term frequency
    :return: the weight calculated using the formula w = (1 + log(tf)) * log(N/df)
    """
    return weight_doc(term_freq) * math.log(len(postings_size) / doc_freq)


def weight_doc(term_freq):
    """
    Calculate the log-frequency weight given tf and df in lnc
    :param term_freq: tf = term frequency
    :return: the weight calculated using the formula w = 1 + log(tf)
    """
    if term_freq == 0:
        return 0
    return 1 + math.log(term_freq, 10)


def process_free_query(query):
    """
    Process a free query
    :param query: the free query given
    :return: most relevant 10 documents as a list in descending order of relevance
    """
    res = []
    query_info = process_doc(query)
    # Initialize scores of each document to 0
    scores = {}
    for doc in postings_size:
        scores[doc] = 0
    for word in query_info[0]:
        if word not in dictionary:
            # tf of documents if always 0, so the score is 0
            continue
        qw = weight_query(dictionary[word], query_info[0][word])
        if qw == 0:
            # w(t,q)=0, so additional score for this term is 0
            continue
        file_pointer = dict_index[word]
        file_count = 0
        while file_count < dictionary[word]:
            pf.seek(file_pointer)
            info_str = pf.read(index_width)
            if info_str[0] == '\n':
                break
            pair = tuple(map(lambda x: int(x), info_str.strip().split(' ')))
            scores[pair[0]] += weight_doc(pair[1])
            file_pointer += index_width
            file_count += 1
    for doc in scores:
        scores[doc] /= postings_size[doc]
        if len(res) < search_limit:
            heappush(res, (scores[doc], -doc))
        else:
            if res[0] < (scores[doc], -doc):
                heappop(res)
                heappush(res, (scores[doc], -doc))
    res_docs = []
    while res:
        doc = heappop(res)
        if doc[0] > 0:
            res_docs.append(-doc[1])
    res_docs.reverse()
    return res_docs


dictionary_file = postings_file = sizes_file = file_of_queries = file_of_output = None


try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:s:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-s':
        sizes_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"


if dictionary_file == None or postings_file == None or sizes_file == None \
        or file_of_queries == None or file_of_output == None:
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, sizes_file, file_of_queries, file_of_output)
