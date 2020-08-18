import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP | NP VP | NP Adv VP | S Conj S | S Conj VP
AdvP -> Adv | Adv AdvP | Adv PP

AP -> Adv Adj | Adj | Adj Conj Adj | Adj PP | Adv Adj PP | Adj AP
CP -> DP Conj DP
DP -> Det NP
NP -> N | AP AP N | P Det N | Det N | AP N | Det N PP | Det AP N
PP -> P NP
VP -> V | V NP | Adv V NP | V PP | V NP PP | VP AdvP

"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    # splitting into words and making lowercase
    tokenized = nltk.word_tokenize(sentence.lower())

    # removing each word that doesn't contain any english letters
    cleaned = [word for word in tokenized if any(c.isalpha() for c in word)]

    return cleaned


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    
    # Helper function to traverse the whole tree
    def traverse_tree(tree):
        for subtree in tree:
            
            # If the current node is a subtree then we need to go deeper recursively
            if type(subtree) == nltk.tree.Tree:
                
                # checking if the node is a "Noun Phrase" and doesn't contain any other "Noun Phrase" as its child 
                if subtree.label() == "NP" and not "NP" in str(subtree[0:]):
                    chunks.append(subtree)
                    continue

                traverse_tree(subtree)
    
    # A list to hold all the NP chunks
    chunks = []

    # starting the tree traversal
    traverse_tree(tree)         

    return chunks


if __name__ == "__main__":
    main()
