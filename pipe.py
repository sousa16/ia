# pipe.py: Template para implementação do projeto de Inteligência Artificial 2023/2024.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 21:
# 99991 João Sousa

import sys
from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)


class PipeManiaState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = PipeManiaState.state_id
        PipeManiaState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id


class Board:
    """Representação interna de um tabuleiro de PipeMania."""

    def __init__(self, cells: tuple):
        """Construtor da classe."""
        self.cells = cells
        self.remaining_cells = []
        self.placed_cells = []
        self.size = len(cells)
        self.invalid = False

    def calculate_state(self):
        """ Calcula o estado interno do tabuleiro para ser usado no tabuleiro
        inicial """

        temp_cells = []
        # Initialize as list of empty tuples
        self.possible_values = []

        # Calculate possible_values, which will use actions_for_cell
        for row in range(self.size):
            row_possibilities = ()
            for col in range(self.size):
                actions = self.actions_for_cell(row, col)

                if len(actions) == 0:
                    self.invalid = True
                    return self
                else:
                    # Append a tuple (row, col, actions) to temp_cells
                    temp_cells.append((row, col, actions))

                row_possibilities += (actions,)

            self.possible_values += (row_possibilities,)

        # Sort temp_cells by the length of actions
        temp_cells.sort(key=lambda x: len(x[2]))

        # Create remaining_cells from the sorted temp_cells
        self.remaining_cells = [(row, col) for row, col, actions in temp_cells]

        return self

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.cells[row][col]

    def get_row(self, row: int) -> tuple:
        """Devolve a linha especificada."""
        return self.cells[row]

    def get_col(self, col: int) -> tuple:
        """Devolve a coluna especificada."""
        return tuple(self.cells[row][col] for row in range(self.size))

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        return self.get_value(row - 1, col), self.get_value(row + 1, col)

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        return self.get_value(row, col - 1), self.get_value(row, col + 1)

    def place_piece(self, row: int, col: int, piece: str):
        """Coloca a peça na posição especificada e devolve um novo tabuleiro."""

        new_row = self.cells[row][:col] + (piece,) + self.cells[row][col + 1:]
        new_cells = self.cells[:row] + (new_row,) + self.cells[row + 1:]
        new_board = Board(new_cells)

        new_board.remaining_cells = self.remaining_cells[1:]
        new_board.placed_cells = self.placed_cells + [(row, col)]
        new_board.possible_values = self.possible_values
        new_board.calculate_next_possible_pieces(row, col)

        # Sort remaining_cells by the length of possible actions for each cell
        new_board.remaining_cells.sort(key=lambda cell: len(
            new_board.possible_values[cell[0]][cell[1]]))

        """
        print("Placed piece", piece, "at", row, col)
        # print("Remaining cells:", new_board.remaining_cells)
        # print("Placed cells:", new_board.placed_cells)
        print("Possible values for cell:", new_board.possible_values[row][col])
        print("-------------------------------------------------")"""

        return new_board

    def calculate_next_possible_pieces(self, row: int, col: int):
        """Calcula as possibilidades para a posição que foi alterada.
        Atualiza a linha e coluna afetadas."""

        # Recalculate for affected row and column
        new_possible_values = ()
        for r in range(self.size):
            row_possibilities = ()
            for c in range(self.size):
                old_possibilities = self.get_possibilities_for_cell(r, c)
                if (r != row and c != col) or len(old_possibilities) == 0:
                    row_possibilities += (old_possibilities,)
                    continue

                possibilities = tuple(self.actions_for_cell(r, c))

                if (r != row or c != col) and len(possibilities) == 0:
                    self.invalid = True
                    return

                row_possibilities += (possibilities,)

            new_possible_values += (row_possibilities,)

        self.possible_values = new_possible_values

    def get_remaining_cells_count(self):
        """Devolve o número de células que ainda não foram preenchidas."""
        return len(self.remaining_cells)

    def get_next_cell(self):
        """Devolve a próxima célula a preencher."""
        return self.remaining_cells[0]

    def get_possibilities_for_cell(self, row, col):
        """Devolve as possibilidades para a célula especificada."""
        if not self.possible_values[row]:  # Check if the tuple is empty
            return ()
        return self.possible_values[row][col]

    def get_surrounding_placed_cells(self, row, col):
        """Devolve as peças colocadas nas posições adjacentes."""
        """top, bottom, left, right"""
        surrounding_placed_pieces = [None, None, None, None]

        if row != 0 and (row - 1, col) in self.placed_cells:
            surrounding_placed_pieces[0] = self.get_value(row - 1, col)

        if row != self.size - 1 and (row + 1, col) in self.placed_cells:
            surrounding_placed_pieces[1] = self.get_value(row + 1, col)

        if col != 0 and (row, col - 1) in self.placed_cells:
            surrounding_placed_pieces[2] = self.get_value(row, col - 1)

        if col != self.size - 1 and (row, col + 1) in self.placed_cells:
            surrounding_placed_pieces[3] = self.get_value(row, col + 1)

        return surrounding_placed_pieces

    def __repr__(self):
        return "\n".join(map(lambda x: "\t".join(map(str, x)), self.cells))

    @ staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 pipe.py < test-01.txt

            > from sys import stdin
            > line = stdin.readline().split()
        """
        cells = [tuple(line.strip("\n").split('\t')) for line in sys.stdin]
        return Board(tuple(cells)).calculate_state()

    def actions_for_closing_piece(self, row, col, surrounding_placed_pieces):
        """Devolve as ações possíveis para uma peça de fecho."""
        actions = ["FC", "FB", "FE", "FD"]

        invalid_pieces_0 = {"BB", "BE", "BD", "VB", "VE", "LV"}
        invalid_pieces_1 = {"BC", "BE", "BD", "VC", "VD", "LV"}
        invalid_pieces_2 = {"BC", "BB", "BD", "VB", "VD", "LH"}
        invalid_pieces_3 = {"BC", "BB", "BE", "VC", "VE", "LH"}

        if surrounding_placed_pieces[0] in invalid_pieces_0:
            return ("FC",)
        if surrounding_placed_pieces[1] in invalid_pieces_1:
            return ("FB",)
        if surrounding_placed_pieces[2] in invalid_pieces_2:
            return ("FE",)
        if surrounding_placed_pieces[3] in invalid_pieces_3:
            return ("FD",)

        invalid_pieces_0 = {"FB", "FE", "FD", "BC", "VC", "VD", "LH"}
        invalid_pieces_1 = {"FC", "FE", "FD", "BB", "VB", "VE", "LH"}
        invalid_pieces_2 = {"FC", "FB", "FD", "BE", "VC", "VE", "LV"}
        invalid_pieces_3 = {"FC", "FB", "FE", "BD", "VB", "VD", "LV"}

        if row == 0 or surrounding_placed_pieces[0] in invalid_pieces_0:
            actions.remove("FC")
        if row == self.size - 1 or surrounding_placed_pieces[1] in invalid_pieces_1:
            actions.remove("FB")
        if col == 0 or surrounding_placed_pieces[2] in invalid_pieces_2:
            actions.remove("FE")
        if col == self.size - 1 or surrounding_placed_pieces[3] in invalid_pieces_3:
            actions.remove("FD")

        return tuple(actions)

    def actions_for_bifurcation_piece(self, row, col, surrounding_placed_pieces):
        """Devolve as ações possíveis para uma peça de bifurcação."""

        if row == 0 or surrounding_placed_pieces[0] in {"FC", "FE", "FD", "BC", "VC", "VD", "LH"}:
            return ("BB",)
        if row == self.size - 1 or surrounding_placed_pieces[1] in {"FB", "FE", "FD", "BB", "VB", "VE", "LH"}:
            return ("BC",)
        if col == 0 or surrounding_placed_pieces[2] in {"FC", "FB", "FE", "BE", "VC", "VE", "LV"}:
            return ("BD",)
        if col == self.size - 1 or surrounding_placed_pieces[3] in {"FC", "FB", "FD", "BD", "VB", "VD", "LV"}:
            return ("BE",)

        actions = ["BC", "BB", "BE", "BD"]

        # Check for surrounding pieces that have a connection
        if surrounding_placed_pieces[0] in {"FB", "BB", "BE", "BD", "VB", "VE", "LV"}:
            actions.remove("BB")
        if surrounding_placed_pieces[1] in {"FC", "BC", "BE", "BD", "VC", "VD", "LV"}:
            actions.remove("BC")
        if surrounding_placed_pieces[2] in {"FD", "BC", "BB", "BD", "VB", "VD", "LH"}:
            actions.remove("BD")
        if surrounding_placed_pieces[3] in {"FE", "BC", "BB", "BE", "VC", "VE", "LH"}:
            actions.remove("BE")

        return tuple(actions)

    def actions_for_corner_piece(self, row, col, surrounding_placed_pieces):
        """Devolve as ações possíveis para uma peça de canto."""
        actions = ["VC", "VB", "VE", "VD"]

        invalid_pieces_0 = {"FC", "FE", "FD", "BC", "VC", "VD", "LH"}
        invalid_pieces_1 = {"FB", "FE", "FD", "BB", "VB", "VE", "LH"}
        invalid_pieces_2 = {"FC", "FB", "FE", "BE", "VC", "VE", "LV"}
        invalid_pieces_3 = {"FC", "FB", "FD", "BD", "VB", "VD", "LV"}

        invalid_pieces_4 = {"FB", "BB", "BE", "BD", "VB", "VE", "LV"}
        invalid_pieces_5 = {"FC", "BC", "BE", "BD", "VC", "VD", "LV"}
        invalid_pieces_6 = {"FD", "BC", "BB", "BD", "VB", "VD", "LH"}
        invalid_pieces_7 = {"FE", "BC", "BB", "BE", "VC", "VE", "LH"}

        if row == 0 or surrounding_placed_pieces[0] in invalid_pieces_0 or surrounding_placed_pieces[1] in invalid_pieces_5:
            actions.remove("VC") if "VC" in actions else None
            actions.remove("VD") if "VD" in actions else None
        elif row == self.size - 1 or surrounding_placed_pieces[1] in invalid_pieces_1 or surrounding_placed_pieces[0] in invalid_pieces_4:
            actions.remove("VB") if "VB" in actions else None
            actions.remove("VE") if "VE" in actions else None

        if col == 0 or surrounding_placed_pieces[2] in invalid_pieces_2 or surrounding_placed_pieces[3] in invalid_pieces_7:
            actions.remove("VE") if "VE" in actions else None
            actions.remove("VC") if "VC" in actions else None
        elif col == self.size - 1 or surrounding_placed_pieces[3] in invalid_pieces_3 or surrounding_placed_pieces[2] in invalid_pieces_6:
            actions.remove("VB") if "VB" in actions else None
            actions.remove("VD") if "VD" in actions else None

        return tuple(actions)

    def actions_for_straight_piece(self, row, col, surrounding_placed_pieces):
        """Devolve as ações possíveis para uma peça reta."""
        actions = ["LV", "LH"]

        if row == 0 or row == self.size - 1 or surrounding_placed_pieces[2] in {
                "FD", "BC", "BB", "BD", "VB", "VD", "LH"} or surrounding_placed_pieces[3] in {"FE", "BC", "BB", "BE", "VC", "VE", "LH"} or surrounding_placed_pieces[0] in {"FC", "FE", "FD", "BC", "VC", "VD", "LH"} or surrounding_placed_pieces[1] in {"FB", "FE", "FD", "BB", "VB", "VE", "LH"}:
            actions.remove("LV")

        if col == 0 or col == self.size - 1 or surrounding_placed_pieces[0] in {
                "FB", "BB", "BE", "BD", "VB", "VE", "LV"} or surrounding_placed_pieces[1] in {"FC", "BC", "BE", "BD", "VC", "VD", "LV"} or surrounding_placed_pieces[2] in {"FC", "FB", "FE", "BE", "VC", "VE", "LV"} or surrounding_placed_pieces[3] in {"FC", "FB", "FD", "BD", "VB", "VD", "LV"}:
            actions.remove("LH")

        return tuple(actions)

    def actions_for_cell(self, row, col):
        """Devolve as ações possíveis para a célula especificada."""
        piece = self.get_value(row, col)
        surrounding_placed_pieces = self.get_surrounding_placed_cells(row, col)

        if piece[0] == "F":
            return self.actions_for_closing_piece(row, col, surrounding_placed_pieces)
        elif piece[0] == "B":
            return self.actions_for_bifurcation_piece(row, col, surrounding_placed_pieces)
        elif piece[0] == "V":
            return self.actions_for_corner_piece(row, col, surrounding_placed_pieces)
        else:
            return self.actions_for_straight_piece(row, col, surrounding_placed_pieces)


class PipeMania(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        state = PipeManiaState(board)
        super().__init__(state)
        pass

    def actions(self, state: PipeManiaState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        if state.board.invalid:
            return []

        row, col = state.board.get_next_cell()

        possibilities = state.board.get_possibilities_for_cell(row, col)
        return map(lambda piece: (row, col, piece), possibilities)

    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        (row, col, piece) = action
        return PipeManiaState(state.board.place_piece(row, col, piece))

    def goal_test(self, state: PipeManiaState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        return state.board.get_remaining_cells_count() == 0

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    board = Board.parse_instance()
    pipemania = PipeMania(board)
    goal_node = depth_first_tree_search(pipemania)
    print(goal_node.state.board)
