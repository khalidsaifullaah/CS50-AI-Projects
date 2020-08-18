import os
import random
import numpy as np
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    transition_probs = dict.fromkeys(corpus.keys(), 0)
    
    # giving a probability to the pages that can be visited from 
    # given page in parameter using damping factor
    if len(corpus[page]) > 0:
        N = len(corpus[page])
        probability = damping_factor / N
        for page in corpus[page]:
            transition_probs[page] = probability
    else:
        # if the page doesn't contain outgoing links
        # we'll assume it has links to all pages thus the probability
        N = len(corpus)
        probability = damping_factor / N
        for page in corpus:
            transition_probs[page] = probability

    # giving probality to all the pages of the corpus using value of 1 - damping_factor 
    N = len(corpus)
    probability = (1 - damping_factor) / N
    transition_probs = {k:v+probability for (k, v) in transition_probs.items()}
    return transition_probs


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # variable for tracking each page that has been visited
    sample_counter = dict.fromkeys(corpus.keys(), 0)

    # choosing the 1st sample randomly from the corpus
    sample = random.choices(list(corpus.keys()), k = 1)[0]
    sample_counter[sample] += 1

    # let's get the transition probabilities of the page
    transition_probs = transition_model(corpus, sample, damping_factor)

    # generating all the next samples based on prev samples transition values
    prev_sample_probs = transition_probs
    for i in range(n-1):
        # generating next sample based on prev sample's transition probs
        next_sample = random.choices(list(prev_sample_probs.keys()), k = 1, weights = list(prev_sample_probs.values()))[0]
        sample_counter[next_sample] += 1
        prev_sample_probs = transition_model(corpus, next_sample, damping_factor)

    # lets calculate the page rank for each page of the corpus using counter's value
    page_rank = {k: v/n for (k, v) in sample_counter.items()}

    return page_rank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # helper function to calculate the sum of all the incoming links page rank for a query page
    def incoming_links_sum(query_page):
        sum = 0
        for page in corpus:
            if query_page in corpus[page]:
                sum += prev_page_rank[page]/len(corpus[page])
        return sum
    
    # for any page that doesn't contain any outgoing link, we're it has links to every page
    # thus making those adjustments to the corpus
    for page in corpus:
            if len(corpus[page]) == 0:
                corpus[page] = set(corpus.keys())

    # begining by assigning each page a rank of 1/N in the corpus
    N = len(corpus)
    d = damping_factor
    page_rank = dict.fromkeys(corpus.keys(), 1/N)

    # set the current page_rank as the previous, so we can calculate new ranks based on those values
    prev_vals = np.array(list(page_rank.values()))
    prev_page_rank = copy.deepcopy(page_rank)

    while True:
        # calculating new page ranks for each page based on formula PR(p) = 1-d/N + d*sum(PR(i)/NumLinks(i))
        for page in page_rank:
            page_rank[page] = ((1 - d)/N) + (d * incoming_links_sum(page))
        
        # storing the current page ranks in numpy array to make calculations easier
        current_vals = np.array(list(page_rank.values()))

        # calculating the change between previous and current rank values
        difference = abs(prev_vals - current_vals)

        # checking if it crosses the threshold
        if np.all(np.round(difference, 3) <= 0.001):
            break
        

        # set the current values as previous values
        prev_vals = current_vals
        prev_page_rank = page_rank.copy()

    return page_rank

if __name__ == "__main__":
    main()
