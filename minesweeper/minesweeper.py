import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        else:
            None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # marking the cell as a move made cell
        self.moves_made.add(cell)

        # marking the cell as safe
        if cell not in self.safes:
            self.mark_safe(cell)

        # extracting row, column value from cell
        i, j = cell

        cells = set()

        # helper function to add a cell to the cells set
        def add_cell(new_cell):
            if new_cell not in self.safes and new_cell not in self.moves_made:
                cells.add(new_cell)

        # neighbors from same column
        if i+1 < self.height:
            new_cell = (i+1, j)
            add_cell(new_cell)
        if i-1 >= 0:
            new_cell = (i-1, j)
            add_cell(new_cell)

        # neighbors from same row
        if j+1 < self.width:
            new_cell = (i, j+1)
            add_cell(new_cell)
        if j-1 >= 0:
            new_cell = (i, j-1)
            add_cell(new_cell)

        # neighbors from diagonal
        if i-1 >= 0 and j-1 >= 0:
            new_cell = (i-1, j-1)
            add_cell(new_cell)
        if i+1 < self.height and j+1 < self.height:
            new_cell = (i+1, j+1)
            add_cell(new_cell)

        # neighbors from anti-diagonal
        if i-1 >= 0 and j+1 < self.width:
            new_cell = (i-1, j+1)
            add_cell(new_cell)
        if i+1 < self.height and j-1 >= 0:
            new_cell = (i+1, j-1)
            add_cell(new_cell)

        # adding the newly created sentence to knowledge base
        new_sentence = Sentence(cells, count)
        self.knowledge.append(new_sentence)

        # helper function to evaluate knowledge base after appending a new sentece to it
        def evaluate_knowledges(new_sentence):

            # marking the cells as safe and mines using the knowledge from known_safes and known_mines function
            for sentence in self.knowledge:
                if len(sentence.cells) == 0:
                    self.knowledge.remove(sentence)
                    continue
                if not sentence.known_safes() is None:
                    known_safe_cells = list(sentence.known_safes())
                    for cell in known_safe_cells:
                        self.mark_safe(cell)
                if not sentence.known_mines() is None:
                    known_mine_cells = list(sentence.known_mines())
                    for cell in known_mine_cells:
                        self.mark_mine(cell)

            # making inference on knowledge base by finding subsets 
            sentences = []
            for sentence in self.knowledge:

                if sentence != new_sentence:
                    # the set must be a subset and it's length must be nonzero; we aren't considering empty sets
                    if len(sentence.cells) > 0 and sentence.cells.issubset(new_sentence.cells):
                        new_set = new_sentence.cells - sentence.cells
                        new_count = abs(new_sentence.count - sentence.count)
                        temp_sentence = Sentence(new_set, new_count)
                        sentences.append(temp_sentence)
                    elif len(new_sentence.cells) > 0 and new_sentence.cells.issubset(sentence.cells):
                        new_set = sentence.cells - new_sentence.cells
                        new_count = abs(sentence.count - new_sentence.count)
                        temp_sentence = Sentence(new_set, new_count)
                        sentences.append(temp_sentence)
            if len(sentences) > 0:
                self.knowledge += sentences

            return
        evaluate_knowledges(new_sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        print(self.safes - self.moves_made)
        for cell in self.safes:
            if cell not in self.mines and cell not in self.moves_made:
                return cell

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        i = random.randint(0, self.height-1)
        j = random.randint(0, self.height-1)
        movable_cells = []
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                if cell not in self.moves_made and cell not in self.mines:
                    movable_cells.append(cell)
        if len(movable_cells) > 0:
            random_cell = movable_cells[random.randint(0, len(movable_cells)-1)]
            return random_cell
        else:
            return None
