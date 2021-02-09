#!/usr/bin/python3
# dictionary-of-documents: ~/nltk_data/corpora/reuters/training/
import nltk
import os
import ssl
import sys
import getopt

from shared import index_width, doc_count, max_doc_id, empty_str, normalize


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    # This is an empty method
    # Pls implement your code in below
    print('indexing...')
    # Initializations
    dictionary = {}
    doc_freq = {}
    # Iterate through each file
    # Not directly using files.sorted() because this sorts
    # alphabetically instead of by index number
    files = os.listdir(in_dir)
    file_index = 0
    while file_index < max_doc_id:
        # For each file, process
        file_index = file_index + 1
        if not str(file_index) in files:
            continue
        file_name = in_dir + "/" + str(file_index)
        with open(file_name, 'r') as reader:
            # Get the unprocessed words
            content = reader.read()
            words_in_doc = []
            words = nltk.word_tokenize(content)
            for w in words:
                ws = w.split('/')
                for word in ws:
                    word = normalize(word)
                    if not word == "" and not word in words_in_doc:
                        words_in_doc.append(word)
            for word in words_in_doc:
                if word not in dictionary:
                    dictionary[word] = []
                    doc_freq[word] = 0
                dictionary[word].append(file_index)
                doc_freq[word] = doc_freq[word] + 1
    with open(out_dict, 'w') as dict_writer:
        with open(out_postings, 'w') as post_writer:
            for word in sorted(doc_freq):
                dict_writer.write(word + " " + str(doc_freq[word]) + "\n")
                for doc in dictionary[word]:
                    post_writer.write(num_to_str(doc))
                # Add additional spaces so each word in postings takes the same number of characters
                count = doc_freq[word]
                while count < doc_count:
                    post_writer.write(empty_str)
                    count = count + 1
                post_writer.write("\n")


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


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    """
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    nltk.download('punkt')
    """
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
