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
        tokens = parse(nltk.word_tokenize(query))
        i = 0
        while i < len(tokens):
            if len(tokens) == 1:
                if isinstance(tokens[0], str):
                    tokens[0] = search_single_word(tokens[0])
                break
            if tokens[i] == 'AND':
                # Get all things to be dealt with using parallel AND
                deal_list = tokens[(i-2):i]
                j = i + 1  # pointer to find AND
                i = i - 2  # pointer to find operands
                while j < len(tokens) and tokens[j] == 'AND':
                    j = j + 1
                    i = i - 1
                    deal_list.append(tokens[i])
                # Open all
                tokens[i] = handle_and(deal_list)
                tokens[(i + 1):] = tokens[j:]
            elif tokens[i] == 'OR':
                # Get all things to be dealt with using parallel OR
                deal_list = tokens[(i-2):i]
                j = i + 1  # pointer to find OR
                i = i - 2  # pointer to find operands
                while j < len(tokens) and tokens[j] == 'OR':
                    j = j + 1
                    i = i - 1
                    deal_list.append(tokens[i])
                # Open all
                tokens[i] = handle_or(deal_list)
                tokens[(i + 1):] = tokens[j:]
            elif tokens[i] == 'NOT':
                # Force open NOT if this is the last operation
                if len(tokens) == i + 1:
                    tokens = handle_not(tokens[i - 1])
                # Tag otherwise
                else:
                    tokens[i - 1] = ('NOT', tokens[i - 1])
                    tokens[i:] = tokens[(i + 1):]
                    i = i - 1
            i = i + 1
        for doc_id in tokens[0]:
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


def classify_operands(operands):
    """
    classify the list of operands into the 4 categories: word, list, not word, and not list
    :param operands: the list of operands to classify
    :return: dictionary with category as key and list of operands of the category as value
    """
    res = {
        'words': [],
        'lists': [],
        'nwords': [],  # not words
        'nlists': []  # not lists
    }
    for operand in operands:
        if isinstance(operand, str):
            res['words'].append(operand)
        elif isinstance(operand, list):
            res['lists'].append(operand)
        elif isinstance(operand[1], str):
            res['nwords'].append(operand)
        else:
            res['nlists'].append(operand)
    return res


def handle_or(operands):
    """
    perform OR over a list of operands
    :param operands: the given operands
    :return: the resulting list after performing OR
    """
    classified_operands = classify_operands(operands)
    res = handle_or_word(classified_operands['words'])
    lists = classified_operands['lists']
    lists.append(res)
    res = handle_or_list(lists)
    return res


def handle_or_word(words):
    """
    perform OR on a list of words
    :param words: the list of words to perform the operation
    :return: the list of docIDs in ascending order that (one single document) contains any words in the given list
    """
    return handle_or_shared(words, lambda i: words[i] not in dictionary, lambda i: dictionary[words[i]],
                            lambda i: words[i], get_inv_doc_id, search_single_word)


def handle_or_list(lists):
    """
    perform OR on a list of lists
    :param lists: the list of lists to perform the operation
    :return: the list of docIDs in ascending order that is the Union of given lists
    """
    def get_leading_pointer(base, count):
        if count >= len(lists[base]):
            return 1, base
        return -lists[base][count], base
    return handle_or_shared(lists, lambda i: not lists[i], lambda i: len(lists[i]), lambda i: i,
                            get_leading_pointer, lambda l: l)


def handle_or_shared(words, empty_test, get_len, base, get_leading_pointer, handle_single):
    """
    perform OR operation on a set of words or lists
    :param words: the set of items to be connected by OR
    :param empty_test: a unary Boolean function returns true if the given index in the set would return empty, hence
    making the result of OR empty
    :param get_len: a unary integer function that returns the length of the given index in the set
    :param base: a mapping of the given index to the base form to store as the keys of pointers
    :param get_leading_pointer: a binary function that takes in the base form and a count, and returns the inverted
    docID at the position of count, i.e. count-th docID, in the list associated to the given base form
    :param handle_single: a function that handles the situation when the list is of length 1
    :return: the resulting list of docIDs in ascending order after performing OR
    """
    # If the list is empty, return empty
    if not words:
        return []
    # If the length of the list is one, return itself
    if len(words) == 1:
        return handle_single(words[0])

    pointers = {}
    for i in range(len(words)):
        if empty_test(i):
            del words[i]
            return handle_or_shared(words, empty_test, get_len, base, get_leading_pointer, handle_single)
        pointers[(base(i))] = 0

    # Merge lists
    res = []
    for i in range(len(words)):
        posting = handle_single(words[i])
        for index in posting:
            if index not in res:
                res.append(index)
    return sorted(res)


def handle_not(token):
    """
    perform NOT operation
    :param token: the operand of NOT
    :return: the resulting list of NOT operation
    """
    if type(token) == str:
        return handle_and_not_words(list(range(1, max_doc_id)), [token])
    else:
        return handle_and_not_lists(list(range(1, max_doc_id)), [token])


def handle_and(operands):
    """
    perform AND over a list of mixed categories of operands
    :param operands: the given operands of mixed categories
    :return: the resulting list after performing AND
    """
    def rid_not(ns):
        res = []
        for n in ns:
            res.append(n[1])
        return res

    classified_operands = classify_operands(operands)
    res = handle_and_word(classified_operands['words'])
    lists = classified_operands['lists']
    lists.append(res)
    res = handle_and_list(lists)
    res = handle_and_not_words(res, rid_not(classified_operands['nwords']))
    res = handle_and_not_lists(res, rid_not(classified_operands['nlists']))
    return res


def handle_and_not_lists(ls, lists):
    def get_leading_pointer(i, count):
        if len(lists[i]) <= count:
            return -1, i
        return lists[i][count], i
    return handle_and_not_shared(ls, lists, get_leading_pointer, lambda i: i, lambda i: len(lists[i]))


def handle_and_not_words(ls, words):
    return handle_and_not_shared(ls, words, get_doc_id, lambda i: words[i],
                                 lambda i: dictionary[words[i]])


def handle_and_not_shared(ls, words, get_leading_pointer, base, get_len):
    """
    perform AND NOT operation: ls AND NOT words
    :param ls: the given base list that terms are to be removed by NOT
    :param words: the list of words to exclude
    :param get_leading_pointer: a binary function that takes in the base form and a count, and returns the docID at the
    position of count, i.e. count-th docID, in the list associated to the given base form
    :param base: a mapping of the given index to the base form to store as the keys of pointers
    :param get_len: a unary integer function that returns the length of the given index in the set
    :return: the resulting list after performing AND NOT
    """
    def get_ls_leading_pointer(index):
        if len(ls) <= index:
            return -1, 'LIST'
        return ls[index], 'LIST'

    def update_next_word(doc_id):
        next_doc = get_leading_pointer(doc_id[1], pointers[doc_id[1]] + skip_steps[doc_id[1]])
        while 0 < next_doc[0] < ls_leading_doc[0]:
            pointers[doc_id[1]] = pointers[doc_id[1]] + skip_steps[doc_id[1]]
            next_doc = get_leading_pointer(doc_id[1], pointers[doc_id[1]])
        if next_doc[0] > ls_leading_doc[0]:
            pointers[doc_id[1]] = pointers[doc_id[1]] + 1
            next_doc = get_leading_pointer(doc_id[1], pointers[doc_id[1]])
            while 0 < next_doc[0] < ls_leading_doc[0]:
                pointers[doc_id[1]] = pointers[doc_id[1]] + 1
                next_doc = get_leading_pointer(doc_id[1], pointers[doc_id[1]])
        heappush(leading_docs, next_doc)

    def update_ls():
        nonlocal ls_leading_doc
        ls[ls_pointer:] = ls[(ls_pointer + 1):]
        ls_leading_doc = get_ls_leading_pointer(ls_pointer)
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
    # Process lists
    while ls_leading_doc[0] > 0 and leading_docs:
        current_smallest = heappop(leading_docs)
        while leading_docs and leading_docs[0][0] == current_smallest:
            heappop(leading_docs)
        # If get to the end of list, remove and do nothing
        if current_smallest[0] < 0:
            continue
        # Skip through the giving list to locate the current smallest
        ls_next = get_ls_leading_pointer(ls_pointer + ls_skip_step)
        while 0 < ls_next[0] < current_smallest[0]:
            ls_pointer = ls_pointer + ls_skip_step
            ls_next = get_ls_leading_pointer(ls_pointer + ls_skip_step)
        # Remove if found
        if ls_next[0] == current_smallest[0]:
            ls_pointer = ls_pointer + ls_skip_step
            update_ls()
            update_next_word(current_smallest)
            continue
        # Search the interval not skipped
        ls_leading_doc = get_ls_leading_pointer(ls_pointer)
        while 0 < ls_leading_doc[0] < current_smallest[0]:
            ls_pointer = ls_pointer + 1
            ls_leading_doc = get_ls_leading_pointer(ls_pointer)
        # Remove if found
        if ls_leading_doc[0] == current_smallest[0]:
            update_ls()
        # Push next of the word
        update_next_word(current_smallest)
    return ls


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