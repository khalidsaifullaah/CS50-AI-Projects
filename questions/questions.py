import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    corpus = {}

    # getting the absolute address of the corpus directory
    root = os.path.join(os.getcwd(), directory)

    # It'll hold the list of all files that reside in the data directory
    files_list = os.listdir(root)

    # will go through all the files
    for file_name in files_list:

        # getting the absolute address of the document
        file_dir = os.path.join(root, file_name)

        # lastly, open the doc and save the texts in a dict
        with open(file_dir, mode='r', encoding="utf-8") as fd:
            document = fd.read().rstrip("\n")
            corpus[file_name] = document
    
    return corpus


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    # splitting the doc into words and making lowercase
    tokenized = nltk.word_tokenize(document.lower())

    # removing each word that doesn't contain any english letters
    punctuation = string.punctuation
    stopwords = nltk.corpus.stopwords.words('english')

    # it'll hold the cleaned (free from stopwords/punctuations) words only
    cleaned = []

    # will go through each word and filter it out
    for word in tokenized:

        # only consider non-stopwords
        if not word in stopwords:

            # if punctuation is present in the word we need to remove them
            # but strings are immutable, so we need to convert the string into a 'list' of chars
            word_char_list = list(word)

            # go throgh each char of word and check for punctuation
            for i, char in enumerate(word):
                if char in punctuation:
                    word_char_list[i] = ''

            # initializing the word with the new modified list cleaned from punctuations
            modified_word = "".join(word_char_list)

            if len(modified_word) > 0:
                cleaned.append(modified_word)
                

    return cleaned


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # Get all words in corpus
    words = set()
    for doc_name in documents:
        words.update(documents[doc_name])

    # Calculate IDF's for each word in the corpus
    idfs = dict()
    for word in words:
        word_appears = sum(word in documents[doc_name] for doc_name in documents)
        idf = math.log(len(documents) / word_appears)
        idfs[word] = idf

    return idfs

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # Helper function to calculate TF of a word given a doc
    def term_frequency(query_word, doc):
        frequency = 0
        for word in doc:
            if word == query_word:
                frequency += 1
        
        return frequency

    # Calculate TF-IDF first
    tfidfs = dict()
    for file_name in files:
        tfidfs[file_name] = {}
        for word in files[file_name]:
            tf = term_frequency(word, files[file_name])
            tfidfs[file_name][word] = tf * idfs[word]
    
    # giving each file a score by summing TF-IDF values
    files_score = {}
    for file_name in files:
        files_score[file_name] = 0
        for word in query:
            if word in tfidfs[file_name]: 
                files_score[file_name] += tfidfs[file_name][word]
    
    # ranking the files based on their scores
    ranked_files = sorted(files_score, key = lambda k: files_score[k], reverse = True)
    
    # will take only the top N files
    top_n = ranked_files[:n]

    return top_n

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # To hold scores of each sentences
    sentences_score = dict()
    
    # Give each score a 'matching word measure' score and 'query term density' score
    for sentence in sentences:

        # every sentence gonna have 2 kinda score
        score = {'matching word measure': 0, 'query term density': 0}

        # count how many word matches to calculate query term density
        matched_words = 0

        for word in query:
            if word in sentences[sentence]:
                score['matching word measure'] += idfs[word]
                matched_words += 1

        # calculate query term density    
        score['query term density'] = matched_words / len(sentences[sentence])

        # set the calculated score for the sentence to its dictionary
        sentences_score[sentence] = score

    # ranking the sentences based on their matching word measure scores first then query term density scores
    ranked_sentences = sorted(sentences_score, key = lambda k: (sentences_score[k]['matching word measure'], sentences_score[k]['query term density']), reverse = True)

    # will take only the top N sentences
    top_n = ranked_sentences[:n]
    
    
    return top_n

if __name__ == "__main__":
    main()
