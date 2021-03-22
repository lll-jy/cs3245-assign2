import math

from nltk.stem.porter import *
import nltk

doc_id_width = 6
max_doc_id = 15000
frequency_width = 2

index_width = doc_id_width + frequency_width
postings_info_file = 'lengths.txt'


def normalize(src):
    """
    :param src: The original word
    :return: Normalized word with only lower-case alphabetical characters after stemming
    """
    # To lower case
    word = src.lower()
    # Remove non-alphabetical
    regex = re.compile('[^a-zA_Z]')
    word = regex.sub('', word)
    # Stem words
    stemmer = PorterStemmer()
    word = stemmer.stem(word)
    return word


def process_doc(content):
    """
    Process the content of a document
    :param content: content string of a document (or query)
    :return: dictionary with term frequency in this document, and the length of vector of the document
    """
    doc_dict = {}
    words = nltk.word_tokenize(content)
    for w in words:
        ws = w.split('/')
        for word in ws:
            word = normalize(word)
            if not word == "":
                if word not in doc_dict:
                    doc_dict[word] = 0
                doc_dict[word] += 1
    acc = 0
    for word in doc_dict:
        tf = 1 + math.log(doc_dict[word])
        acc += tf * tf
    return doc_dict, math.sqrt(acc)
