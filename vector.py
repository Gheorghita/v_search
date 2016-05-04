"""
Vector search for documents.
Returns all documents based on an search query and cosine similarity
"""
from collections import defaultdict
import math
import sys


# no of documents
N = 0

# all words
WORDS_DICTIONARY = defaultdict(dict)

# reverse index
REV_INDEX = defaultdict(dict)

# { w : no_of_docs }
DOC_FREQ = defaultdict(int)

# { docs_ids : euclidean length }
LENGTH = defaultdict(float)

# { doc_name : doc_id }
DOCS = defaultdict(dict)


def init_no_docs(fname):
    """
    open fname and read no of lines

    :param fname: filename
    :return: no of lines
    """

    with open(fname) as opened_file:
        return len(opened_file.readlines())


def init_reverse_index(fname):
    """
    open fname, read previously generated reverse index
    and build an dictionary:
        { 'w1' :{'docid1' :'freq1', ..., 'docidn' :'freqn'}, ...,
          'w2' :{'docid1' :'freq1', ..., 'docidn' :'freqn'}
        }

    :example:
        dict['w1']['docid1'] -> freq1

    :param fname: reverse_index previously generated
    """

    word_id = None

    with open(fname) as opened_file:
        for line in opened_file:
            splitted_line = line.strip('\n\r').split(' ')
            if len(splitted_line) == 1:
                word_id = splitted_line[0]
            else:
                REV_INDEX[word_id][splitted_line[0]] = int(splitted_line[1])


def init_words_id_dict(fname):
    """
    open fname, read previously generated list (word - word_id) and
    build an dictionary: { word : word_id }

    :param fname: words_dict previously generated
    """

    with open(fname) as opened_file:
        for line in opened_file:
            (key, val) = line.split()
            WORDS_DICTIONARY[key] = val


def init_docs_dict(fname):
    """
    open fname, read previously generated list (doc - doc_id) and
    build an dictionary: { doc : doc_id }

    :param fname: docs_ids previously generated
    """

    with open(fname) as opened_file:
        for line in opened_file:
            (key, val) = line.split()
            DOCS[key] = val


def init_doc_freq():
    """
    { w : no_of_docs }
    """

    for word in WORDS_DICTIONARY.values():
        DOC_FREQ[word] = len(REV_INDEX[word])


def init_lengths():
    """
    length for each document.
    """
    for doc_id in DOCS.values():
        temp = 0
        for word in WORDS_DICTIONARY.values():
            temp += importance(word, doc_id)**2
        LENGTH[doc_id] = math.sqrt(temp)


def importance(word, doc_id):
    """
    Importance of word in document id.
    :param word: word from dictionary
    :param doc_id: doc_id
    :return: importance or 0 if the word isn't in the doc
    """
    if doc_id in REV_INDEX[word]:
        return REV_INDEX[word][doc_id] * idf(word)
    else:
        return 0.0


def idf(word):
    """
    idf of word.
    :param word: word
    :return: idf of word or 0 if the word isn't in the dictionary
    """
    if word in WORDS_DICTIONARY.values():
        return math.log(N / DOC_FREQ[word], 2)
    else:
        return 0.0


def intersection(sets):
    """
    intersection of all sets
    :param sets: list sets
    :return: intersection
    """
    return reduce(set.intersection, [s for s in sets])


def cos_similarity(query, doc_id):
    """
    cos similarity between query and document id search results.
    :param query: user query
    :param doc_id: doc id
    :return: cos similarity
    """
    similarity = 0.0
    for word in query:
        if word in WORDS_DICTIONARY.values():
            similarity += idf(word)*importance(word, doc_id)
    similarity = similarity / LENGTH[doc_id]
    return similarity


def search():
    """
    Returns a list of relevant documents based on introduced query,
    in decreasing order of cosine similarity.
    """
    input_query = tokenize(raw_input("Search query >> "))
    index = 0
    query = []
    while index < len(input_query):
        if input_query[index] not in WORDS_DICTIONARY.keys():
            print "Ignoring " + input_query[index] + " not an dictionary word"
            del input_query[index]
            continue
        query.append(WORDS_DICTIONARY[input_query[index]])
        index = index + 1
    if not query:
        print "No query terms."
        sys.exit()
    # find document ids containing all query terms.
    relevant_docs = intersection(
        [set(REV_INDEX[term].keys()) for term in query])
    if not relevant_docs:
        print "No doc matched all query terms."
    else:
        scores = sorted([(doc_id, cos_similarity(query, doc_id))
                         for doc_id in relevant_docs],
                        key=lambda doc: doc[1],
                        reverse=True)
        docs_reverse = dict(map(reversed, DOCS.items()))
        print "Score: filename"
        for (doc_id, score) in scores:
            print str(score)+": " + docs_reverse[doc_id]


def tokenize(inp):
    """
    list of words without punctuations
    :param inp: input string
    :return: list
    """
    characters = " .,!#$%^&*();:\n\t\\\"?!{}[]<>"
    terms = inp.lower().split()
    return [term.strip(characters) for term in terms]


def main():
    """
    Initializing docs_dict, words_id_dict, no_docs, reverse_index,
    doc_freq, lenghts and starting search function
    """
    global N
    init_docs_dict('sources/docs_ids.txt')
    init_words_id_dict('sources/words_id.txt')
    N = init_no_docs('sources/docs_ids.txt')
    init_reverse_index('sources/reverse_index.txt')
    init_doc_freq()
    init_lengths()
    search()


if __name__ == "__main__":
    main()
