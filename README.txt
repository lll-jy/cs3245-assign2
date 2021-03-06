This is the README file for A0194567M and A0194484R's submission

== Python Version ==

I'm (We're) using Python Version 3.7.9 for
this assignment.

== General Notes about this assignment ==

1. Indexing

1.1 Normalized word format

Words stored in the dictionary are alphabetical lower-case stemmed words.
Hence, the program is not supportive for searches containing numbers. In
fact, all non-alphabetical content of a word is ignored.

Note that the nltk tokenizer cannot break the words connected by '/'
properly, so there is an additional process to tokenize the word further so
that words connected by '/' are regarded as separate words correctly.

Stop words are not removed.

1.2 BSBI

Blocked Sort_Based Indexing(BSBI) is used to make the indexing process scalable.
The corpus is divided into blocks of files, each block contains 1000 files except
for the last one.

The inverted index is firstly constructed inside each block, kept as intermediate
files. The intermediate files are then be merged together into one dictionary file
and one postings file. The merging process is done recursively, postings are to be
merged with the result of the previous merges. And when merging two posting files,
two pointers are used to traverse through the two posting lists, which is similar as the
AND operation's algorithm.


1.3 Output file format

After indexing, the resulting dictionary.txt file is a document such that
each line contains one word in the normalized form, after which is a white
space followed by the document frequency in the training data, after which
is another white space followed by the position of starting character index
of the line of the corresponding word in the postings file, namely, the
pointer to the postings file. The words are sorted alphabetically.

The resulting postings.txt file is a document such that each line is a list
of document IDs that contains the word in the corresponding line of
dictionary.txt, and sorted in ascending order. For easy access using pointer
in a file using the in-built Python seek function, we purposely put some
white spaces such that each document ID takes 6 characters long since the
maximum of document ID in the training data has 5 digits. The docIDs are the
name of the files. The files in the Reuters training set are not in
consecutive indices, but we just assumed that there are some missing files
and still uses the file name as the docID.

By the fixed with of each document ID in the postings file and the size of
each postings list in memory while indexing, the pointer to the postings file
stored in the dictionary file is hence easily calculated cumulatively from
the product of document frequency of the word and the fixed document ID width
plus one (the '\n' mark).


1.4 Other notes

For indexing, sent_tokenize function is not used because all that is needed is
words, and we do not need to get the intermediate state of breaking the whole
paragraph into sentences.


2. Searching


2.3 Query and output file format

The Query file contains the search queries, each line in the file
contains one query. And the file contains no empty lines at the end.

Since the results are also posting lists, the same format as posting file
is used in the search output file. Each line in the output file is a list
of document IDs that contains the search result of the queries,
and sorted in ascending order.


== Files included with this submission ==

index.py: required source code of indexing
search.py: required source code of searching
shared.py: shared code for index.py and search.py
dictionary.txt: generated dictionary using index.py with data in Reuters
postings.txt: generated postings list using index.py with data in Reuters
README.txt: this file
ESSAY.txt: answers to essay questions

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0194567M, A0194484R, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

[ ] I/We, A0194567M, A0194484R, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

NLTK Installation help:
https://stackoverflow.com/questions/38916452/nltk-download-ssl-certificate-verify-failed

NLTK Porter stemmer help:
https://www.nltk.org/howto/stem.html

Regex to remove non-alphabetical terms help:
https://stackoverflow.com/questions/22520932/python-remove-all-non-alphabet-chars-from-string

Parsing queries algorithm help:
https://en.wikipedia.org/wiki/Shunting-yard_algorithm

NLTK API:
https://www.nltk.org/api/nltk.html

Python API:
https://docs.python.org/3/library/