This is the README file for A0000000X's submission

== Python Version ==

I'm (We're) using Python Version 3.7.9 for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

Words stored in the dictionary are alphabetical lower-case stemmed words. Hence,
the program is not supportive for searches containing numbers. In fact, all
non-alphabetical content of a word is ignored.

Note that the nltk tokenizer cannot break the words connected by '/' properly,
so there is an additional process to tokenize the word further so that words
connected by '/' are regarded as separate words correctly.

After indexing, the resulting dictionary.txt file is a document such that each line
contains one word in the normalized form, after which is a white space followed by
the document frequency in the training data. The words are sorted alphabetically.

The resulting postings.txt file is a document such that each line is a list of document
IDs that contains the word in the corresponding line of dictionary.txt, and sorted
in ascending order. For easy access using pointer in a file using the in-built Python
seek function, I purposely put some white spaces such that each document ID takes 10
characters long and each word takes the space of 10000 documents. The docIDs are the
name of the files. The files in the Reuters training set are not in consecutive indices,
but I just assumed that there are some missing files and still uses the file name as the
docID.

For indexing, I did not use sent_tokenize function because all I need is words, and
I do not need to get the intermediate state of breaking the whole paragraph into
sentences.

To parse a query, the Shunting-yard algorithm is used as recommended. Operator 'AND' is
assigned a precedence 3 and 'OR' is assigned a precedence 2. Although 'NOT' is also a
Boolean operator, it is unary, and hence treated as a function token instead of operator
in the algorithm.

Some further simplification steps are done before going to the postings list given the query.
Firstly, remove double negations that does not affect the result of evaluation. Secondly,
since AND operation usually do not load very long lists in memory, so it might be more efficient
to transform some OR operations to AND if possible. Hence, I applied De Morgans laws to transform
expressions in the form of "NOT (A OR B)" to "NOT A AND NOT B".

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py: required source code of indexing
search.py: required source code of searching
shared.py: shared functions and values of the previous code files
dictionary.txt: generated dictionary using index.py with data in Reuters
postings.txt: generated postings list using index.py with data in Reuters
README.txt: this file
ESSAY.txt: answers to essay questions

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0194567M, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0194567M, did not follow the class rules regarding homework
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