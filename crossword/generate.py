import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            self.domains[var] = {
                word for word in self.domains[var] if len(word) == var.length}

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        if self.crossword.overlaps[x, y] is None:
            return revised

        for x_word in list(self.domains[x]):
            i, j = self.crossword.overlaps[x, y]

            # looking in y's domain that if all of it's value generates conflict
            # in other words, if no y in Y.domains satisfies constraint(X,Y)
            if all(x_word[i] != y_word[j] for y_word in self.domains[y]):
                self.domains[x].remove(x_word)
                revised = True

        return revised

    # custom function to initialize a queue with all the binary constraints
    def initialize(self):
        queue = []
        for x in self.crossword.variables:
            for y in self.crossword.neighbors(x):
                # if no arcs provided then populate queue with all the arcs in the problem
                queue.append((x, y))

        return queue

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = arcs

        if arcs is None:
            # initializing queue with all the constraints of the problem
            queue = self.initialize()

        while len(queue) > 0:
            # Dequeue
            x, y = queue.pop(0)

            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    # Enqueue
                    queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check if all values are distinct
        if len(list(assignment.values())) == len(set(list(assignment.values()))):

            constraints = self.initialize()

            for (x, y) in constraints:

                # only consider arcs where both are assigned
                if x not in assignment or y not in assignment:
                    continue

                i, j = self.crossword.overlaps[x, y]

                # If overlapping square contains different value then not consistent
                if assignment[x][i] != assignment[y][j]:
                    return False

            return True

        return False

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # unassigned variables set
        unassigned_vars = self.crossword.variables - set(assignment.keys())

        # Neighbors who are still unassigned
        unassigned_neighbors = set(unassigned_vars).intersection(
            self.crossword.neighbors(var))

        # dictionary to map each word with the nember of values they rule out from neighbors domain
        ordered_domain_values = {key: 0 for key in self.domains[var]}

        for value in self.domains[var]:
            for neighbor in unassigned_neighbors:
                # shared square between 2 vars
                i, j = self.crossword.overlaps[var, neighbor]

                for neighbor_value in self.domains[neighbor]:
                    # checking if the 2 words aren't distinct or if the shared square contains different letter
                    if value == neighbor_value or value[i] != neighbor_value[j]:
                        ordered_domain_values[value] += 1

        # sorting the domain values based on the values they ruled out
        ordered_domain_values = [key for key, val in sorted(
            ordered_domain_values.items(), key=lambda item: item[1])]

        return ordered_domain_values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # unassigned variables set
        unassigned = list(self.crossword.variables - set(assignment.keys()))

        # unassigned variables mapped with their domain
        unassigned_vars = {var: self.domains[var] for var in unassigned}

        # sort the variables based on their domain length for "Minimum Remaining Value Heuristic"
        unassigned_vars = [key for key, val in sorted(
            unassigned_vars.items(), key=lambda item: len(item[1]))]

        if len(unassigned_vars) >= 2:
            # checking for degree heuristic
            degree_var1 = len(self.crossword.neighbors(unassigned_vars[0]))
            degree_var2 = len(self.crossword.neighbors(unassigned_vars[1]))

            # will choode the one that has mostest neighbors
            if degree_var1 >= degree_var2:

                return unassigned_vars[0]
            else:
                return unassigned_vars[1]

        return unassigned_vars[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
