This is the README file for A0194567M and A0194484R's submission

== Python Version ==

I'm (We're) using Python Version 3.7.9 for
this assignment.

== General Notes about this assignment ==

** Change of command line processing (reason see 1.3):
Indexing: python index.py -i directory-of-documents -d dictionary-file -p postings-file -s sizes-file
Searching: python search.py -d dictionary-file -p postings-file -s sizes-file -q file-of-queries -o output-file-of-results

1. Indexing

1.1 Normalized word format (Remains the same as HW2)

Words stored in the dictionary are alphabetical lower-case stemmed words.
Hence, the program is not supportive for searches containing numbers. In
fact, all non-alphabetical content of a word is ignored.

Note that the nltk tokenizer cannot break the words connected by '/'
properly, so there is an additional process to tokenize the word further so
that words connected by '/' are regarded as separate words correctly.

Stop words are not removed.

1.2 Indexing method
For simplicity, scalable index construction techniques(BSBI, SPIMI) are not used.

1.3 Output file format (Minor updates compared to HW2)

After indexing, the resulting dictionary.txt file is a document such that
each line contains one word in the normalized form, after which is a white
space followed by the document frequency in the training data, after which
is another white space followed by the position of starting character index
of the line of the corresponding word in the postings file, namely, the
pointer to the postings file. The words are sorted alphabetically.

The resulting postings.txt file is a document such that each line is a list
of number pairs of document ID that contains the word in the corresponding
line of dictionary.txt, and term frequency within the document, and the
pairs are sorted in ascending order based on document ID. For easy access
using pointer in a file using the in-built Python seek function, we purposely
put some white spaces such that each tuple takes 8 characters long since the
maximum of document ID in the training data has 5 digits, and the maximum
term frequency has 2 digits.


By the fixed width of each document ID in the postings file and the size of
each postings list in memory while indexing, the pointer to the postings file
stored in the dictionary file is hence easily calculated cumulatively from
the product of document frequency of the word and the fixed document ID width
plus one (the '\n' mark).

An additional file named length.txt is generated during indexing, which keeps
track of the vector length of each document. The format of this file is such
that each line contains two number representing the document ID and length of
vector of the document respectively, separated by a white space, and each line
is separated using a '\n'.


1.4 Other notes (Remains the same as HW2)

For indexing, sent_tokenize function is not used because all that is needed is
words, and we do not need to get the intermediate state of breaking the whole
paragraph into sentences.


2. Searching

2.1 Cosine similarities calculation

As required, lnc.ltc is used to calculate the cosine similarities. Note the
special case when tf = 0, (1 + log(tf)) is replaced with the number 0.

The algorithm to calculate cosign scores is derived from the one given in
the lecture notes. Vectors for queries are actually not normalized to a unit
vector because this is a shared coefficient for all cosine scores, and thus
it makes no difference in the ranking of score.

Terms in the query that does not appear in the dictionary will not have effect
on the scores of documents. Omitting such terms in the calculation of score
makes sense because, firstly, the result of log-frequency of the term in any
document would be 0 makes the weight of term in any document 0; and, secondly,
actual document frequency is 0, and thus makes idf, and hence weight of term
in the query, undefined as the denominator is 0.


2.2 Get the 10 most relevant

A min-heap is used to help to keep track of the 10 most relevant documents. The
general implementation is a min-heap of tuple (score, -docID) sorted by score,
and -docID as tie breaker (as we want docID to be a tie breaker for the final
result with smaller docID ranked higher). If the size of heap is smaller than
10, the new tuples can be pushed directly. Otherwise, compare the current tuple
with the min element in the heap, and if the current tuple is greater, pop the
min element from the heap and push the current tuple into the heap.

If less than 10 documents has a non-zero score, only the documents with non-zero
score will be in the output, sorted in the same manner.


2.3 Query and output file format

The query file contains the free text search queries, each line in the file
contains one query. And the file contains no empty lines.

Each line of the output file will contain the 10 (or less) most relevant docIDs
corresponding to the query at the corresponding line of the query file in the
format as required.


== Files included with this submission ==

index.py: required source code of indexing
search.py: required source code of searching
shared.py: shared code for index.py and search.py
dictionary.txt: generated dictionary using index.py with data in Reuters
postings.txt: generated postings list using index.py with data in Reuters
lengths.txt: generated length of vector of each document using index.py with data Reuters
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