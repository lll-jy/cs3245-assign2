#!/usr/bin/python3
import math
import re
from heapq import *

import nltk
import sys
import getopt
from shared import normalize, index_width, max_doc_id

# Global variables, dictionary and postings
dictionary = {}
dict_index = {}
pf = None


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def run_search(dict_file, postings_file, queries_file, results_file):
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

    # Load dictionary
    count = 0
    for word_str in df.readlines():
        word_str = word_str[:-1]
        entries = word_str.split(' ')
        dictionary[entries[0]] = int(entries[1])
        dict_index[entries[0]] = int(entries[2])
        count = count + 1
    # Perform searching
    for query in qf.readlines():
        res = []
        for doc_id in res:
            rf.write(num_to_str(doc_id))
        rf.write("\n")

    # Close files
    df.close()
    pf.close()
    qf.close()
    rf.close()


def num_to_str(n):
    """
    :param n: A number
    :return: A string of exactly length 10 containing the number with white spaces at the back.
    This makes sure that each docID takes exactly the same number of characters, making it easier
    to locate the file pointer
    """
    s = str(n)
    l = len(s)
    while l < index_width:
        s = s + " "
        l = l + 1
    return s


def handle_and_word(words):
    """
    perform AND on a list of words
    :param words: the list of words to perform the operation
    :return: the list of docIDs in ascending order that (one single document) contains all words in the given list
    """
    return handle_and_shared(words, lambda i: words[i] not in dictionary, lambda i: dictionary[words[i]],
                             lambda i: words[i], get_inv_doc_id, search_single_word)


def handle_and_list(lists):
    """
    perform AND on a list of lists
    :param lists: the list of lists to perform the operation
    :return: the list of docIDs in ascending order that is the intersection of given lists
    """
    def get_leading_pointer(base, count):
        if count >= len(lists[base]):
            return 1, base
        return -lists[base][count], base
    return handle_and_shared(lists, lambda i: not lists[i], lambda i: len(lists[i]), lambda i: i,
                             get_leading_pointer, lambda l: l)


def handle_and_shared(words, empty_test, get_len, base, get_leading_pointer, handle_single):
    """
    perform AND operation on a set of words or lists
    :param words: the set of items to be connected by AND
    :param empty_test: a unary Boolean function returns true if the given index in the set would return empty, hence
    making the result of AND empty
    :param get_len: a unary integer function that returns the length of the given index in the set
    :param base: a mapping of the given index to the base form to store as the keys of pointers
    :param get_leading_pointer: a binary function that takes in the base form and a count, and returns the inverted
    docID at the position of count, i.e. count-th docID, in the list associated to the given base form
    :param handle_single: a function that handles the situation when the list is of length 1
    :return: the resulting list of docIDs in ascending order after performing AND
    """
    # If the list is empty, return empty
    if not words:
        return []
    # If the length of list is zero, returns itself
    if len(words) == 1:
        return handle_single(words[0])
    # Initialize pointers to be 0, initialize skip steps for each word, and find leading docs
    pointers = {}
    skip_steps = {}
    leading_docs = []
    for i in range(len(words)):
        # If word not in dictionary, then done
        if empty_test(i):
            return []
        pointers[base(i)] = 0
        skip_steps[base(i)] = math.floor(math.sqrt(get_len(i)))
        heappush(leading_docs, get_leading_pointer(base(i), 0))
    # Merge lists
    res = []
    while True:
        current_biggest = heappop(leading_docs)
        # If gets to empty, return
        if current_biggest[0] == 1:
            return res
        processed_words = []
        is_common = True
        for word in leading_docs:
            # Break if processed, since leading_docs is changing
            if word[1] in processed_words:
                continue
            processed_words.append(word[1])
            current_pointer = pointers[word[1]]
            if word[0] == 1:
                return res
            # Continue if the leading doc is the same doc
            if word[0] == current_biggest[0]:
                leading_docs.remove(word)
                pointers[word[1]] = current_pointer + 1
                heappush(leading_docs, get_leading_pointer(word[1], pointers[word[1]]))
                continue
            doc_id = get_leading_pointer(word[1], current_pointer + skip_steps[word[1]])
            while doc_id[0] < 0 and -doc_id[0] < -current_biggest[0]:
                current_pointer = current_pointer + skip_steps[word[1]]
                doc_id = get_leading_pointer(word[1], current_pointer + skip_steps[word[1]])
            # If common docID found, continue
            if doc_id[0] == current_biggest[0]:
                pointers[word[1]] = current_pointer + skip_steps[word[1]] + 1
                leading_docs.remove(word)
                heappush(leading_docs, get_leading_pointer(word[1], pointers[word[1]]))
                continue
            # Traverse interval not skipped
            doc_id = get_leading_pointer(word[1], current_pointer)
            while doc_id[0] < 0 and -doc_id[0] < -current_biggest[0]:
                current_pointer = current_pointer + 1
                doc_id = get_leading_pointer(word[1], current_pointer)
            # If common docID found, continue
            if -doc_id[0] == -current_biggest[0]:
                pointers[word[1]] = current_pointer + 1
                leading_docs.remove(word)
                heappush(leading_docs, get_leading_pointer(word[1], pointers[word[1]]))
                continue
            # If comes to the end of list, end the loop since no more intersection is possible
            elif doc_id[0] == 1:
                return res
            # Else, restart the loop through heap
            else:
                is_common = False
                pointers[word[1]] = current_pointer
                leading_docs.remove(word)
                heappush(leading_docs, doc_id)
                break
        # Update result
        if is_common:
            res.append(-current_biggest[0])
        # Update leading docs heap
        pointers[current_biggest[1]] = pointers[current_biggest[1]] + 1
        heappush(leading_docs, get_leading_pointer(current_biggest[1], pointers[current_biggest[1]]))


def search_single_word(word):
    """
    get the entire list of docID of a particular word
    :param word: a normalized single word to search in dictionary
    :return: the list of docID containing the word
    """
    res = []
    pointer = 0
    doc_id = get_inv_doc_id(word, pointer)
    while doc_id[0] < 0:
        res.append(-doc_id[0])
        pointer = pointer + 1
        doc_id = get_inv_doc_id(word, pointer)
    return res


def get_doc_id(word, count):
    """
    get the docID
    :param word: the word that is searching for
    :param count: the number of documents already processed, i.e. the pointer position
    :return: a tuple (-docID at the position, word)
    """
    inverted = get_inv_doc_id(word, count)
    return -inverted[0], inverted[1]


def get_inv_doc_id(word, count):
    """
    get the docID
    :param word: the word that is searching for
    :param count: the number of documents already processed, i.e. the pointer position
    :return: a tuple (-docID at the position, word)
    """
    pf.seek(dict_index[word])
    pf.seek(dict_index[word] + count * index_width)
    s = pf.read(index_width)
    if s[0] == '\n' or count >= dictionary[word]:
        return 1, word  # positive leading number means this is the end of the word
    return -int(s.strip()), word


dictionary_file = postings_file = file_of_queries = output_file_of_results = None


try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"


if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
