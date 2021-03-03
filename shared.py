from nltk.stem.porter import *

index_width = 6
max_doc_id = 15000

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
