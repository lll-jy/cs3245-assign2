import re

from nltk.stem.porter import *

doc_count = 10000
# doc_count = 10
max_doc_id = 15000
# max_doc_id = 12
index_width = 6
word_posting_len = doc_count * index_width + 1
# placeholder of empty string
empty_str = "      "
# the size of block in BSBI
block_size = 5000000


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
