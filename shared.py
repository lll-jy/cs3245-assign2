from nltk.stem.porter import *
import nltk

doc_id_width = 6
max_doc_id = 15000
frequency_width = 6
index_width = doc_id_width + frequency_width
postings_info_file = 'postings_summary.txt'


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
    doc_dict = {}
    count_in_doc = 0
    words = nltk.word_tokenize(content)
    for w in words:
        ws = w.split('/')
        for word in ws:
            word = normalize(word)
            if not word == "":
                if word not in doc_dict:
                    doc_dict[word] = 0
                doc_dict[word] += 1
                count_in_doc += 1
    return doc_dict, count_in_doc
