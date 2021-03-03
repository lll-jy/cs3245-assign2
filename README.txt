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

2.1 Parsing queries

To parse a query, the Shunting-yard algorithm is used as recommended. Operator
'AND' is assigned a precedence 3 and 'OR' is assigned a precedence 2. Although
'NOT' is also a Boolean operator, it is unary, and hence treated as a function
token instead of operator in the algorithm.

Some further simplification steps are done before going to the postings list
given the query. Firstly, remove double negations that does not affect the
result of evaluation. Secondly, since AND operation usually do not load very
long lists in memory, so it might be more efficient to transform some OR
operations to AND if possible. Hence, 23 applied De Morgans Laws to transform
expressions in the form of "NOT (A OR B)" to "NOT A AND NOT B" before
evaluation.


2.2 Evaluation

2.2.1 General idea

After getting the parsed sequence of tokens of a query, the general idea of
evaluation is to evaluate tokens recursively (with each token guaranteed to be
either a (not) word, a (not) list, or an operator, which will be elaborated
later) as follows:

    1. If the sequence length is 1
      a. and the only token is a word,
        ==> then find the documents containing this word.
      b. and the only token is a list,
        ==> then return this list.
    2. If the sequence length is greater than 1,
      ==> then search through the tokens sequentially until the first operator
          is found, and then handle this operator, remove this operator and its
          corresponding operands, and insert back the result in the same
          position of the token sequence.


2.2.2 Handle NOT

If the operator is NOT, since double negation is removed during parsing, we can
simply take this NOT operator and evaluate. The NOT operator is unary, so that
its operand is simply a word token or an intermediate resulting list of previous
rounds of evaluation that appears immediately in front of the operator.

However, since NOT will output all docIDs that do not contain the required word
(or the docIDs in the intermediate resulting list), operating NOT directly is
not favored. Therefore, if a NOT operator is found, we decide not to evaluate
directly, but instead, wrap it with the operand in the form  ('NOT', operand).
This tuple will be opened only if needed.

An exception is when this NOT is the only remaining operator in the token
sequence, then we simply find the result of AND NOT (discussed in the next
section) between the full list of all natural numbers smaller than the estimated
maximum document ID and the list to operate NOT because a result is expected.
Note that the full list may contain some document IDs that are not actually in
the training data because, as mentioned before, the IDs are not consecutive.
But we just leave this problem there as it is because such search queries are
in fact not expected because in reality, searching for merely NOT something does
not have any pragmatic utility.


2.2.3 Handle AND

If the operator is AND, search for tokens following AND sequentially until
a token that is not 'AND' is found. This is because intersections can be
dealt with together, not necessarily as a binary operation, which would
potentially save a lot of time if the AND list is quite long.

There are 4 possible forms of operands of a list of things to operate AND
together, which are a single word, an intermediate resulting list, a single
word wrapped with NOT, and an intermediate resulting list wrapped with NOT.
Let's call them word, list, nword, and nlist for short. The strategy to
handle the 4 forms is as follows:

    1. Find intersection of words, let it be iw.
    2. Find intersection of lists and iw, let it be iwl.
    3. Remove documents in iwl that contain some nword, let it be iwlnw.
    4. Remove documents in iwlnw that contain some nlist element, and this
       is the result.

To find the intersections, n-way merging with skip pointer is used. During
evaluation of intersection, a heap of all items to intersect ordered by
the least document ID in the item is kept throughout the whole process. A
document ID will be added to the result if and only if at some point during
evaluation, the document ID appears at the front of all items to intersect.
And the merging will end immediately if any of the items become empty. The
skip pointer implementation follows what is specified in the assignment
requirement.


2.2.4 Handle OR

If the operator is OR, it is handled similarly to AND, but disjunction
is implemented instead of conjunction. Hence, skip pointer is not (and
should not be) used here. All elements appear in any of the items to
operate should appear in the result.

In addition, nwords and nlists should be opened using AND NOT using
the strategy as mentioned before (full list AND NOT nword/nlist) before
performing the OR operation. This would, again, be possible to introduce
some documents that do not exist. Nevertheless, they are kept there because
either the resulting list will eventually be used to intersect with the
result of some other parts of evaluation, which will guarantee to filter
out all invalid document IDs, or such queries are not expected as searching
for something OR NOT something also does not have pragmatic utility.


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