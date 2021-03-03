#!/usr/bin/python3
# dictionary-of-documents: ~/nltk_data/corpora/reuters/training/
import nltk
import os
import ssl
import sys
import getopt

from nltk.stem.porter import *
from shared import normalize, index_width, max_doc_id

# Global variables
block_size = 1000


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print("indexing...")
    # Initializations
    dictionary = {}
    doc_freq = {}

    # Iterate through each file
    # Not directly using files.sorted() because this sorts
    # alphabetically instead of by index number
    files = os.listdir(in_dir)
    file_index = 0
    block_count = 0
    file_count = 0
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

        file_count += 1
        words_in_doc = []
        words = nltk.word_tokenize(content)
        for w in words:
            ws = w.split('/')
            for word in ws:
                word = normalize(word)
                if not word == "" and word not in words_in_doc:
                    words_in_doc.append(word)

        for word in words_in_doc:
            if word not in dictionary:
                dictionary[word] = []
                doc_freq[word] = 0
            dictionary[word].append(file_index)
            doc_freq[word] += 1

        # Divide the files into blocks, each block with block_size files
        # index every block by applying BSBI
        if file_count >= block_size:
            block_count += 1
            temp_dict_path = "./temp_dict" + str(block_count) + ".txt"
            temp_posting_path = "./temp_post" + str(block_count) + ".txt"
            bsbi_invert(dictionary, doc_freq, temp_dict_path, temp_posting_path)
            dictionary = {}
            doc_freq = {}
            file_count = 0

    if len(dictionary) >= 1:  # Construct last block using BSBI
        block_count += 1
        temp_dict_path = "./temp_dict" + str(block_count) + ".txt"
        temp_posting_path = "./temp_post" + str(block_count) + ".txt"
        bsbi_invert(dictionary, doc_freq, temp_dict_path, temp_posting_path)

    merge_block(block_count, out_dict, out_postings)


def merge_block(block_count, out_dict, out_postings):
    """
    merge block_count number of blocks into one, and store them in specified files
    :param block_count: the number of blocks to be merged
    :param out_dict: the path to the final dictionary file
    :param out_postings: the path to the final postings file
    """
    if block_count == 1:
        # If there is only one block, copy the block into output files
        dict_reader = open("./temp_dict1.txt", 'r')
        post_reader = open("./temp_post1.txt", 'r')
        dict_writer = open(out_dict, 'w')
        post_writer = open(out_postings, 'w')
        dict_writer.write(dict_reader.read())
        for post in post_reader:
            post_writer.write(post)
        dict_reader.close()
        post_reader.close()
        dict_writer.close()
        post_writer.close()
        os.remove("./temp_dict1.txt")
        os.remove("./temp_post1.txt")
    else:
        # If there are more than one block, merge the blocks recursively
        intermediate_dict_path = "./inter_dict_till" + str(block_count - 1) + ".txt"
        intermediate_post_path = "./inter_post_till" + str(block_count - 1) + ".txt"
        # merge the result of the merging of the previous blocks with the current block
        merge_block(block_count - 1, intermediate_dict_path, intermediate_post_path)
        dict1_reader = open(intermediate_dict_path, 'r')
        post1_reader = open(intermediate_post_path, 'r')
        current_dict_path = "./temp_dict" + str(block_count) + ".txt"
        current_post_path = "./temp_post" + str(block_count) + ".txt"
        dict2_reader = open(current_dict_path, 'r')
        post2_reader = open(current_post_path, 'r')
        dictionary1 = []
        dictionary2 = []
        idx1 = 0
        idx2 = 0
        for line in dict1_reader:
            dictionary1.append(line[:-1])
        for line in dict2_reader:
            dictionary2.append(line[:-1])
        dict1_reader.close()
        dict2_reader.close()
        dict_writer = open(out_dict, 'w')
        post_writer = open(out_postings, 'w')
        acc_pointer = 0
        while True:
            # Merging two blocks
            # Use two pointers to traverse through the two dictionaries
            # The merging result is then written into the specified result files
            if idx1 >= len(dictionary1) and idx2 >= len(dictionary2):
                break
            if idx1 >= len(dictionary1):
                for line in dictionary2[idx2:]:
                    tokens2 = line.split(' ')
                    freq = int(tokens2[1])
                    dict_writer.write(f"{tokens2[0]} {str(freq)} {acc_pointer}\n")
                    acc_pointer += freq * index_width + 1
                for line in post2_reader.readlines():
                    post_writer.write(line)
                break
            if idx2 >= len(dictionary2):
                for line in dictionary1[idx1:]:
                    tokens1 = line.split(' ')
                    freq = int(tokens1[1])
                    dict_writer.write(f"{tokens1[0]} {str(freq)} {acc_pointer}\n")
                    acc_pointer += freq * index_width + 1
                for line in post1_reader.readlines():
                    post_writer.write(line)
                break
            tokens1 = dictionary1[idx1].split(' ')
            tokens2 = dictionary2[idx2].split(' ')
            if tokens1[0] == tokens2[0]:
                word = tokens1[0]
                freq = int(tokens1[1]) + int(tokens2[1])
                posting = post1_reader.readline()[:-1] + post2_reader.readline()[:-1]
                dict_writer.write(f"{word} {str(freq)} {acc_pointer}\n")
                acc_pointer += freq * index_width + 1
                post_writer.write(posting + "\n")
                idx1 += 1
                idx2 += 1
            elif tokens1[0] < tokens2[0]:
                word = tokens1[0]
                freq = int(tokens1[1])
                dict_writer.write(f"{word} {str(freq)} {acc_pointer}\n")
                acc_pointer += freq * index_width + 1
                post_writer.write(post1_reader.readline())
                idx1 += 1
            else:
                word = tokens2[0]
                freq = int(tokens2[1])
                dict_writer.write(f"{word} {str(freq)} {acc_pointer}\n")
                acc_pointer += freq * index_width + 1
                post_writer.write(post2_reader.readline())
                idx2 += 1
        post1_reader.close()
        post2_reader.close()
        dict_writer.close()
        post_writer.close()
        os.remove(intermediate_dict_path)
        os.remove(intermediate_post_path)
        os.remove(current_dict_path)
        os.remove(current_post_path)


def bsbi_invert(dictionary, doc_freq, dict_file, post_file):
    """
    Construct inverted index for every block.
    :param dictionary: the dictionary of the words in the specific block
    :param doc_freq: the document frequency of each word in the block
    :param dict_file: the temporary file for storing the dictionary of the words in the block
    :param post_file: the temporary file for storing the postings of the words in the block
    """
    acc_pointer = 0
    dict_writer = open(dict_file, 'w')
    post_writer = open(post_file, 'w')
    for word in sorted(doc_freq):
        dict_writer.write(f"{word} {str(doc_freq[word])} {acc_pointer}\n")
        acc_pointer += len(dictionary[word]) * index_width + 1
        for doc in dictionary[word]:
            post_writer.write(num_to_str(doc))
        post_writer.write("\n")
    dict_writer.close()
    post_writer.close()


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
