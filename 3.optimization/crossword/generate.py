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
                    draw.rectangle(rect, fill="white") # type: ignore
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font) # type: ignore
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font # type: ignore
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
        for var in self.crossword.variables:
            for word in self.crossword.words:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]
        words_remove = set()
        # if there is an overlapping cell then check (x ?= y)
        if overlap:
            i, j = overlap
            # checking x arc consistent with y
            for word_x in self.domains[x].copy():
                # only domain[y] has word, but domain[x] does not need to has this
                # check letter
                if not any(word_x[i] == word_y[j] for word_y in self.domains[y]):
                    words_remove.add(word_x)
            if words_remove:
                self.domains[x] -= words_remove
                revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # if arcs is None, begin with initial list of all arcs in the problem
        if arcs is None:
            arcs = ((x, y) for x in self.crossword.variables for y in self.crossword.neighbors(x))
        csp_queue = list(arcs)

        while csp_queue:
            x, y = csp_queue.pop(0)
            if self.revise(x, y):
                # if x.domain is empty, return False
                if not self.domains[x]:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    csp_queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment or not assignment[var]:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var_x, word_x in assignment.items():
            if var_x.length != len(word_x):
                return False
            for var_y in self.crossword.neighbors(var_x):
                if var_y in assignment:
                    word_y = assignment[var_y]
                    i, j = self.crossword.overlaps[var_x, var_y]
                    if word_x[i] != word_y[j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        value_heuristic = dict()
        for word in self.domains[var]:
            value_heuristic[word] = 0
            # neighbors of var
            for n in self.crossword.neighbors(var) - set(assignment):
                (i, j) = self.crossword.overlaps[var, n]
                if (i, j):
                    for word_n in self.domains[n]:
                        if word[i] != word_n[j]:
                            value_heuristic[word] += 1

        value_heuristic = sorted(value_heuristic.items(), key=lambda x: x[1])
        return [word for word, _ in value_heuristic]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_var = None
        # 使用无穷大初始化
        min_num_var = float('inf')
        max_degree = -1

        for var in self.crossword.variables - set(assignment):
            # calculate the number of remaining value in domain
            num_var = len(self.domains[var])
            degree = len(self.crossword.neighbors(var))
            #
            if (num_var < min_num_var) or (num_var == min_num_var and degree > max_degree):
                unassigned_var = var
                min_num_var = num_var
                max_degree = degree
        return unassigned_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # 如果assignment已经完成，返回assignment
        if self.assignment_complete(assignment):
            return assignment
        # 以 minimum remaining value 选择一个未分配的变量
        var = self.select_unassigned_variable(assignment)
        # 以 least-constraining-value 选择一个值的列表
        for value in self.order_domain_values(var, assignment):
            # 从最小的值开始，检查是否满足约束
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                # 如果满足约束，继续递归,并更新 assignment 使其弧一致
                arcs = [(var, n) for n in self.crossword.neighbors(var)]
                inference = self.ac3(arcs)
                # 如果
                if inference:
                    result = self.backtrack(new_assignment)
                    if result is not False:
                        return result
            # 如果不满足约束，删除这个值
            del new_assignment[var]
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
