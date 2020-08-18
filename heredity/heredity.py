import csv
import numpy as np
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probabilities = []
    childs = set()

    # helper function that gives the likelyhod of a parent passing their gene to the child
    def pass_on_probability(parent):
        if parent in one_gene:
            return 0.5
        elif parent in two_genes:
            return 1 - PROBS["mutation"]
        else:
            return PROBS["mutation"]
            
    # people with no parents
    for person in people:
        if people[person]["father"] is None and people[person]["mother"] is None:
            if person in one_gene:
                prob_one_gene = PROBS["gene"][1]
                prob_trait = PROBS["trait"][1][True] if person in have_trait else PROBS["trait"][1][False]
                probabilities.append(prob_one_gene * prob_trait)
            elif person in two_genes:
                prob_two_gene = PROBS["gene"][2]
                prob_trait = PROBS["trait"][2][True] if person in have_trait else PROBS["trait"][2][False]
                probabilities.append(prob_two_gene * prob_trait)
            else:
                prob_zero_gene = PROBS["gene"][0]
                prob_trait = PROBS["trait"][0][True] if person in have_trait else PROBS["trait"][0][False]
                probabilities.append(prob_zero_gene * prob_trait)
        else:
            childs.add(person)
    
    # people with parents
    for child in childs:
        if child in one_gene:
            # one case is got the gene from mother and not from father
            from_mother = pass_on_probability(people[child]["mother"])
            not_from_father = 1 - pass_on_probability(people[child]["father"])

            # another case is got the gene from father and not from mother
            from_father = pass_on_probability(people[child]["father"])
            not_from_mother = 1 - pass_on_probability(people[child]["mother"])

            prob_trait = PROBS["trait"][1][True] if child in have_trait else PROBS["trait"][1][False]
            p = (from_mother * not_from_father + from_father * not_from_mother) * prob_trait
            probabilities.append(p)
        elif child in two_genes:
            # parents should pass one gene individually
            from_father = pass_on_probability(people[child]["father"])
            from_mother = pass_on_probability(people[child]["mother"])

            prob_trait = PROBS["trait"][2][True] if child in have_trait else PROBS["trait"][2][False]
            p = (from_father * from_mother) * prob_trait
            probabilities.append(p)
        else:
            # parents should not pass any gene to the child
            not_from_father = 1 - pass_on_probability(people[child]["father"])
            not_from_mother = 1 - pass_on_probability(people[child]["mother"])

            prob_trait = PROBS["trait"][0][True] if child in have_trait else PROBS["trait"][0][False]
            p = (not_from_father * not_from_mother) * prob_trait
            probabilities.append(p)
    
    return np.prod(probabilities)    


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p
        
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # normalizing the "genes" distribution
        N = sum(list(probabilities[person]["gene"].values()))
        for key, value in probabilities[person]["gene"].items():
            probabilities[person]["gene"][key] = value/N if N != 0 else value
        
        # normalizing the "trait" distribution
        N = sum(list(probabilities[person]["trait"].values()))
        for key, value in probabilities[person]["trait"].items():
            probabilities[person]["trait"][key] = value/N if N != 0 else value


if __name__ == "__main__":
    main()
