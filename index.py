#!/usr/bin/python3
# dictionary-of-documents: ~/nltk_data/corpora/reuters/training/
import os
import ssl
import sys
import getopt

from shared import index_width, max_doc_id, process_doc

def usage():
    print("usage: " + sys.argv[0] +
          " -i directory-of-documents -d dictionary-file -p postings-file -l document-lengths-file")


def build_index(in_dir, out_dict, out_postings, out_lengths):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print("indexing...")
    # Initializations
    dictionary = {}
    doc_freq = {}
    doc_len = {}

    # Iterate through each file
    # Not directly using files.sorted() because this sorts
    # alphabetically instead of by index number
    files = os.listdir(in_dir)
    file_index = 0

    while file_index < max_doc_id:
        # For each file, tokenize and normalize the words
        file_index = file_index + 1
        if not str(file_index) in files:
            continue
        file_name = in_dir + "/" + str(file_index)

        reader = open(file_name, 'r')
        # Get the unprocessed words
        content = reader.read()
        reader.close()

        process_res = process_doc(content)
        doc_dict = process_res[0]
        doc_len[file_index] = process_res[1]
        for word in doc_dict:
            if word not in dictionary:
                dictionary[word] = []
                doc_freq[word] = 0
            dictionary[word].append((file_index, doc_dict[word]))
            doc_freq[word] += 1

    invert(dictionary, doc_freq, out_dict, out_postings)

    psf = open(postings_info_file, 'w')
    for file in doc_len:
        psf.write(f"{file} {doc_len[file]}\n")
    psf.close()

    
def invert(dictionary, doc_freq, dict_file, post_file):
    """
    Construct inverted index for all the documents.
    :param dictionary: a dictionary of lists of words' corresponding doc_id and term frequency
    :param doc_freq: the document frequency of each word
    :param dict_file: the output file for storing the dictionary of the words
    :param post_file: the output file for storing the postings of the words
    """
    acc_pointer = 0
    dict_writer = open(dict_file, 'w')
    post_writer = open(post_file, 'w')
    for word in sorted(doc_freq):
        dict_writer.write(f"{word} {str(doc_freq[word])} {acc_pointer}\n")
        acc_pointer += len(dictionary[word]) * index_width + 1
        for doc in dictionary[word]:
            post_writer.write(doc_tuple_str(doc))
        post_writer.write("\n")
    dict_writer.close()
    post_writer.close()


def doc_tuple_str(tuple):
    """
    :param tuple: A tuple of (docID, term frequency)
    :return: A string of fixed length containing the white spaces at the back containing
    information in the tuple.
    """
    s = str(f"{tuple[0]} {tuple[1]}")
    l = len(s)
    while l < index_width:
        s = s + " "
        l = l + 1
    return s


input_directory = output_file_dictionary = output_file_postings = output_file_lengths = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:l:')
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
    elif o == '-l': # lengths file
        output_file_lengths = a
    else:
        assert False, "unhandled option"


if input_directory == None or output_file_postings == None \
        or output_file_dictionary == None or output_file_lengths == None:
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

build_index(input_directory, output_file_dictionary, output_file_postings, output_file_lengths)
