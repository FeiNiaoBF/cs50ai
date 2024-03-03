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
        # The numbers cells is equal to the count,
        # we know that all of that sentence’s cells must be mines.
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        else:
            return set()


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # if cell is mine and in cells, cells update and count sub 1
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1




    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.discard(cell)


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

        '''
        - initial state : starting knowledge base
        - actions: inference rules
        - transition model: new knowledge base after inference
        - goal test: check statement we're trying to prove
        - path cost function: number of steps in proof
        '''

        #    1) mark the cell as a move that has been made
        #    2) mark the cell as safe
        self.state(cell)
        # print('1.----------------------')
        # print(self.moves_made, end='\n')
        # print(self.mines, end='\n')
        # print(self.safes, end='\n')

        #    3) add a new sentence to the AI's knowledge base
        #      based on the value of `cell` and `count`
        subSentence = self.actions(cell, count)
        # print('2.----------------------')
        # print(self.moves_made, end='\n')
        # print(self.mines, end='\n')
        # print(self.safes, end='\n')
        # for s in self.knowledge:
        #     print(s)
        #     print(s.known_safes(), end='\n')
        #     print(s.known_mines(), end='\n')

        #    4) mark any additional cells as safe or as mines
        #      if it can be concluded based on the AI's knowledge base
        #    5) add any new sentences to the AI's knowledge base
        #      if they can be inferred from existing knowledge
        self.update_knowledge_model(subSentence)
        # print('3.----------------------')
        # print(self.moves_made, end='\n')
        # print(self.mines, end='\n')
        # print(self.safes, end='\n')
        # for s in self.knowledge:
        #     print(s)
        #     print(s.known_safes(), end='\n')
        #     print(s.known_mines(), end='\n')



    def state(self, cell):
        try:
            # clicked a cell / move cell
            self.moves_made.add(cell)
            # mark the cell as safe.
            self.mark_safe(cell)
        except EOFError as e:
            print(f"Error: {e}")

    def actions(self, cell, count):
        # inference rules.
        mine_cell, count_mines = self.cell_neighbors(cell)
        subSentence = Sentence(mine_cell, count - count_mines)
        # updating any sentences that contain the cell as well.
        self.knowledge.append(subSentence)
        '''
            KB = [
                {D, G} = 1,
                {D, G, H} = 2,
                ...
            ]
        '''
        return subSentence

    def update_knowledge_model(self, subset):
        # mark new cells as mine or safe
        self.mark_safe_or_mine()
        self.new_inference(subset)


    def mark_safe_or_mine(self):
        # update knowledge base
        # update all cell of sentences
        for sentence in self.knowledge:
            if sentence.known_mines():
                # RuntimeError: Set changed size during iteration so set copy
                for cell in sentence.known_mines().copy():
                    self.mark_mine(cell)
            if sentence.known_safes():
                for cell in sentence.known_safes().copy():
                    self.mark_safe(cell)


    def new_inference(self, subset):
        for sentence in self.knowledge:
            if subset.cells.issubset(sentence.cells) \
                and subset.count > 0 \
                and sentence.count > 0 \
                and subset != sentence:
                # set2-set1 = count2 - count1
                newSubset = sentence.cells.difference(subset.cells)
                newSentence = Sentence(set(newSubset), sentence.count - subset.count)
                self.knowledge.append(newSentence)



    def cell_neighbors(self, cell):
        tmp = set()
        count_mines = 0
        for r in range(cell[0] - 1, cell[0] + 2):
            for c in range(cell[1] - 1, cell[1] + 2):
                if (0 <= r < self.height and 0 <= c < self.width) \
                    and ((r, c) not in self.safes) \
                    and ((r, c) not in self.moves_made):
                    tmp.add((r, c))
                if (r, c) in self.mines:
                    count_mines += 1
        return tmp, count_mines


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move_cell in self.safes:
            if move_cell not in self.mines and move_cell not in self.moves_made:
                return move_cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        random_move = []
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.mines and (i, j) not in self.moves_made:
                    random_move.append((i, j))
        if len(random_move) != 0:
            return random.choice(random_move)
        else:
            return None
