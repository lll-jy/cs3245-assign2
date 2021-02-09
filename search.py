#!/usr/bin/python3
import math
import re
from heapq import *

import nltk
import os
import sys
import getopt

from shared import word_posting_len, normalize, index_width, empty_str

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
    # This is an empty method
    # Pls implement your code in below
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
        dict_index[entries[0]] = count * word_posting_len
        count = count + 1
    # Perform searching
    for query in qf.readlines():
        tokens = parse(nltk.word_tokenize(query))
        i = 0
        while i < len(tokens):
            # Things need to implement TODO:
            # and_nots
            # or words or list
            # handle and
            # handle or
            if tokens[i] == 'AND':
                # Get all things to be dealt with using parallel AND
                deal_list = tokens[(i-2):i]
                j = i + 1
                i = i - 2
                while tokens[j] == 'AND':
                    j = j + 1
                    i = i - 1
                    deal_list.append(tokens[i])
                # Open all
                # res = handle_and(deal_list)
            elif tokens[i] == 'OR':
                print(1)
                # Or list
            elif tokens[i] == 'NOT':
                print(1)
                # ??
            i = i + 1
    # print(handle_and_word(['a', 'again']))
    # print(handle_and_word2(['a', 'again']))
    # print(search_single_word('a'))
    # print(search_single_word('again'))
    print(handle_and_list([[3,4,5,6,7,10,11],[2,3,4,10],[2,3,4,6,7,10,12],[4,10,12]]))
    df.close()
    pf.close()
    qf.close()
    rf.close()
    # print(parse(['Hello', 'AND', 'NOT', '(', 'Worlds', 'OR', 'WorDS', 'OR', 'Windows', 'AND', 'MAC', ')']))


def handle_and_not_words(ls, words):
    return handle_and_not_shared(ls, words, lambda i: (ls[i], 'LIST'), get_doc_id, lambda i: words[i],
                                 lambda i: dictionary[words[i]])


def handle_and_not_shared(ls, words, get_ls_leading_pointer, get_leading_pointer, base, get_len):
    # If the list of words is empty, return itself
    if not words:
        return ls
    # Initialize pointers = 0, skip steps, and leading docs pointer points at
    ls_pointer = 0
    ls_skip_step = math.floor(math.sqrt(len(words)))
    ls_leading_doc = get_ls_leading_pointer(0)
    pointers = {}
    skip_steps = {}
    leading_docs = []
    for i in range(len(words)):
        pointers[base(i)] = 0
        skip_steps[base(i)] = math.floor(math.sqrt(get_len(i)))
        heappush(leading_docs, get_leading_pointer(base(i), 0))


def handle_and_word(words):
    """
    perform AND on a list of words
    :param words: the list of words to perform the operation
    :return: the list of docIDs in ascending order that (one single document) contains all words in the given list
    """
    return handle_and_shared(words, lambda i: words[i] not in dictionary, lambda i: dictionary[words[i]],
                             lambda i: words[i], get_doc_id, search_single_word)


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
    :param get_leading_pointer: a binary function that takes in the base form and a count, and returns the docID at the
    position of count, i.e. count-th docID, in the list associated to the given base form
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
                break
            processed_words.append(word[1])
            current_pointer = pointers[word[1]]
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
    doc_id = get_doc_id(word, pointer)
    while doc_id[0] < 0:
        res.append(-doc_id[0])
        pointer = pointer + 1
        doc_id = get_doc_id(word, pointer)
    return res


def get_doc_id(word, count):
    """
    get the docID
    :param word: the word that is searching for
    :param count: the number of documents already processed, i.e. the pointer position
    :return: the docID at this position
    """
    pf.seek(dict_index[word] + count * index_width)
    s = pf.read(index_width)
    if s == empty_str:
        return 1, word  # positive leading number means this is the end of the word
    return -int(s.strip()), word


def parse(tokens):
    """
    parse tokenized query to simplified executable list structure based on Shunting-yard algorithm
    :param tokens: tokens of a query, including words and strings of 'AND', 'OR', 'NOT', '(', and ')'
    :return: parsed tokens
    """
    # Parse
    special_tokens = ['AND', 'OR', 'NOT', '(', ')']
    ops = {
        'AND': 3,
        'OR': 2,
    }  # precedence
    output = []
    op_stack = []
    # Adapted from pseudo code provided in the Shunting-yard algorithm wikipedia page
    for i in range(len(tokens)):
        if not tokens[i] in special_tokens:
            word = normalize(tokens[i])
            output.append(word)
        elif tokens[i] == 'NOT':
            op_stack.append('NOT')
        elif tokens[i] in ops:
            while op_stack and op_stack[-1] != '(' and ops[op_stack[-1]] >= ops[tokens[i]] :
                output.append(op_stack.pop())
            op_stack.append(tokens[i])
        elif tokens[i] == '(':
            op_stack.append('(')
        elif tokens[i] == ')':
            while op_stack and op_stack[-1] != '(':
                output.append(op_stack.pop())
            if op_stack and op_stack[-1] == '(':
                op_stack.pop()
            if op_stack and op_stack[-1] == 'NOT':
                output.append(op_stack.pop())
    while op_stack:
        output.append(op_stack.pop())
    # Simplify
    i = 0
    while i < len(output):
        # Double negation is canceled
        if output[i] == 'NOT' and output[i - 1] == 'NOT':
            output[(i-1):] = output[(i+1):]
        # Use De Morgan's Law to take OR in NOT out
        elif output[i] == 'NOT' and output[i - 1] == 'OR':
            first_operand = get_operand(output, i - 1)
            second_operand = get_operand(output, i - 1 - len(first_operand))
            remaining = i + 1
            i = i - 2 - len(first_operand) - len(second_operand)
            output[(i+1):] = second_operand + ['NOT'] + first_operand + ['NOT', 'AND'] + output[remaining:]
        i = i + 1
    return output


def get_operand(parsed_tokens, index):
    """
    given index of operator token in the parsed tokens list, get the operand before it
    :param parsed_tokens: the list of tokens to evaluate after parsing
    :param index: the operand to get from index position
    :return: the full operand of the operator at index position in parsed tokens format
    """
    bi_ops = ['AND', 'OR']
    while index > 0:
        index = index - 1
        if parsed_tokens[index] in bi_ops:
            first_operand = get_operand(parsed_tokens, index)
            second_operand = get_operand(parsed_tokens, index - len(first_operand))
            return second_operand + first_operand + [parsed_tokens[index]]
        elif parsed_tokens[index] == 'NOT':
            return get_operand(parsed_tokens, index) + ['NOT']
        else:
            return parsed_tokens[index:(index+1)]


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
