from copy import deepcopy
import re
import sys
import tkinter as tk
class Position:
    def __init__(self, row, col):
        self.row = row
        self.col = col
    def match(self,list_pos):
        for pos in list_pos:
            if self.row == pos.row and self.col == pos.col:
                return True 
        return False 
class PieceNames:
    @staticmethod
    def get_full_name(short_name):
        short_name = short_name.upper()
        if short_name == 'R':
            return 'Rook'
        elif short_name == 'N':
            return 'Knight'
        elif short_name == 'B':
            return 'Bishop'
        elif short_name == 'Q':
            return 'Queen'
        elif short_name == 'K':
            return 'King'
        elif short_name == 'P':
            return 'Pawn'
        else:
            return None

def create_piece(piece, color='white'):
    ''' Takes a piece name or shortname and returns the corresponding piece instance '''
    if piece in (None, ' '): return
    if len(piece) == 1:
        if piece.isupper():
            color = 'white'
        else:
            color = 'black'
        piece_name = PieceNames.get_full_name(piece)
        if piece_name:
            module = sys.modules[__name__]
            return module.__dict__[piece_name](color)
    return None

class Piece(object):
    def __init__(self, color):
        if color == 'black':
            self.shortname = self.shortname.lower()
        elif color == 'white':
            self.shortname = self.shortname.upper()
        self.color = color


    def place(self, board):
        ''' Keep a reference to the board '''
        self.board = board

    def moves_available(self, pos, orthogonal, diagonal, distance):
        board = self.board
        allowed_moves = []
        orth = ((-1, 0), (0, -1), (0, 1), (1, 0))
        diag = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        piece = self
        beginningpos = board.num_notation(pos.upper())
        if orthogonal and diagonal:
            directions = diag + orth
        elif diagonal:
            directions = diag
        elif orthogonal:
            directions = orth
        for x, y in directions:
            collision = False
            for step in range(1, distance + 1):
                if collision: break
                dest = beginningpos[0] + step * x, beginningpos[1] + step * y
                if self.board.alpha_notation(dest) not in board.occupied(
                        'white') + board.occupied('black'):
                    allowed_moves.append(dest)
                elif self.board.alpha_notation(dest) in board.occupied(
                        piece.color):
                    collision = True
                else:
                    allowed_moves.append(dest)
                    collision = True
        allowed_moves = filter(board.is_on_board, allowed_moves)
        return map(board.alpha_notation, allowed_moves)


class Queen(Piece):
    shortname = 'q'

    def moves_available(self, pos):
        return super(Queen, self).moves_available(pos.upper(), True, True, 8)


class Rook(Piece):
    shortname = 'r'
    def possible_moves(self):
        moves = []
        # Directions the queen can move: vertical, horizontal, and diagonal
        directions = [
            (1, 0), (-1, 0),  # vertical
            (0, 1), (0, -1),  # horizontal
            (1, 1), (-1, -1), # diagonal down
            (1, -1), (-1, 1)  # diagonal up
        ]

        # Check each direction
        for d in directions:
            for i in range(1, 8):  # The queen can move up to 7 squares in any direction
                new_row = self.position.row + d[0] * i
                new_col = self.position.col + d[1] * i
                new_pos = Position(new_row, new_col)
                # Check if the new position is inside the board
                if not self.board.is_inside_board(new_pos):
                    break  # Move is off the board, so break out of the loop for this direction
                if self.board.is_square_empty(new_pos):
                    moves.append(new_pos)  # Add the position if it's empty
                elif self.board.is_enemy_piece(new_pos, self.color):
                    moves.append(new_pos)  # Add the position if it's occupied by an enemy piece
                    break  # Can't move past capturing a piece, so break out of the loop
                else:
                    break  # Path is blocked by a friendly piece, so break out of the loop

        return moves 
    def possible_moves(self):
        moves = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
        for d in directions:
            for i in range(1, 8):
                new_row = self.position.row + d[0] * i
                new_col = self.position.col + d[1] * i
                new_pos = Position(new_row, new_col)
                if not self.board.is_inside_board(new_pos):
                    break  # move is off the board
                if self.board.is_square_empty(new_pos):
                    moves.append(new_pos)
                elif self.board.is_enemy_piece(new_pos, self.color):
                    moves.append(new_pos)
                    break  # can't move past a capture
                else:
                    break  # path is blocked by a friendly piece
        return moves

    def move(self, end_pos):
        if end_pos in self.possible_moves():
            return True
        return False

    def __str__(self):
        if self.color == "White":
            return "R"
        return "r" 
    def moves_available(self, pos):
        return super(Rook, self).moves_available(pos.upper(), True, False, 8)


class Bishop(Piece):
    shortname = 'b'
    def possible_moves(self):
        moves = []
        # Bishops can move diagonally in all four directions
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for d in directions:
            for i in range(1, 8):  # Maximum board size is 8x8
                row = self.position[0] + d[0] * i
                col = self.position[1] + d[1] * i
                # Check if the new position is within the board boundaries
                if 0 <= row < 8 and 0 <= col < 8:
                    # Check if the position is occupied by a piece of the same color
                    if self.board[row][col] is None or self.board[row][col].color != self.color:
                        moves.append((row, col))
                    # If the position is occupied by an opponent's piece, capture it
                    if self.board[row][col] is not None and self.board[row][col].color != self.color:
                        break
                else:
                    break
        return moves

    def __str__(self):
        if self.color == "White":
            return "B"
        return "b" 
    def moves_available(self, pos):
        return super(Bishop, self).moves_available(pos.upper(), False, True, 8)


class Knight(Piece):
    shortname = 'n'
    def possible_moves(self):
        moves = []
        # The knight can move in an L shape: 2 steps in one direction and 1 step in a perpendicular direction
        move_offsets = [
            (2, 1), (1, 2), (-1, 2), (-2, 1),
            (-2, -1), (-1, -2), (1, -2), (2, -1)
        ]

        for offset in move_offsets:
            new_row = self.position.row + offset[0]
            new_col = self.position.col + offset[1]
            new_pos = Position(new_row, new_col)
            # Check if the new position is inside the board and either empty or occupied by an enemy piece
            if self.board.is_inside_board(new_pos) and (self.board.is_square_empty(new_pos) or self.board.is_enemy_piece(new_pos, self.color)):
                moves.append(new_pos)

        return moves
    def moves_available(self, pos):
        board = self.board
        allowed_moves = []
        beginningpos = board.num_notation(pos.upper())
        piece = board.get(pos.upper())
        deltas = (
        (-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for x, y in deltas:
            dest = beginningpos[0] + x, beginningpos[1] + y
            if (board.alpha_notation(dest) not in board.occupied(piece.color)):
                allowed_moves.append(dest)
        allowed_moves = filter(board.is_on_board, allowed_moves)
        return map(board.alpha_notation, allowed_moves)
    def __str__(self):
        if self.color == "White":
            return "N"
        return "n" 

class Pawn(Piece):
    shortname = 'p'

    def __init__(self, color):
        super().__init__(color)
        self.en_passant_target = None

    def moves_available(self, pos):
        board = self.board
        piece = self
        if self.color == 'white':
            startpos, direction, enemy = 1, 1, 'black'
            en_passant_row = 4
        else:
            startpos, direction, enemy = 6, -1, 'white'
            en_passant_row = 3
        allowed_moves = []
        prohibited = board.occupied('white') + board.occupied('black')
        beginningpos = board.num_notation(pos.upper())
        forward = beginningpos[0] + direction, beginningpos[1]
        if board.alpha_notation(forward) not in prohibited:
            allowed_moves.append(forward)
            if beginningpos[0] == startpos:
                double_forward = (forward[0] + direction, forward[1])
                if board.alpha_notation(double_forward) not in prohibited:
                    allowed_moves.append(double_forward)
        # En passant
        if self.en_passant_target:
            en_passant_pos = self.en_passant_target
            if (beginningpos[0] == en_passant_row and abs(beginningpos[1] - board.num_notation(en_passant_pos.upper())[1]) == 1):
                allowed_moves.append(board.num_notation(en_passant_pos.upper()))
        # Attacking
        for a in range(-1, 2, 2):
            attack = beginningpos[0] + direction, beginningpos[1] + a
            if board.alpha_notation(attack) in board.occupied(enemy):
                allowed_moves.append(attack)
        allowed_moves = filter(board.is_on_board, allowed_moves)
        return map(board.alpha_notation, allowed_moves)
    def __str__(self):
        if self.color.lower() == "white":
            return "P"
        return "p"

class King(Piece):
    shortname = 'k'
    def __init__(self,color,board,position=None):
        super().__init__(color,board,position)
        self.piece_type = "king"
    def possible_moves(self):
        moves = []
        offsets = [(1, 0), (0, 1), (-1, 0), (0, -1),
                    (1, 1), (-1, 1), (1, -1), (-1, -1)]
        for dr, dc in offsets:
            new_pos = Position(self.position.row + dr, self.position.col + dc)
            if self.board.is_inside_board(new_pos) and (self.board.is_square_empty(new_pos) or self.board.is_enemy_piece(new_pos, self.color)):
                moves.append(new_pos)
        # Castling
        if not self.board.board[self.position.row][self.position.col].has_moved:
            # Check kingside castling
            if self.board.board[self.position.row][7] and not self.board.board[self.position.row][7].has_moved:
                if all(self.board.is_square_empty(Position(self.position.row, c)) for c in range(self.position.col + 1, 7)):
                    moves.append(Position(self.position.row, self.position.col + 2))
            # Check queenside castling
            if  self.board.board[self.position.row][0] and not self.board.board[self.position.row][0].has_moved:
                if all(self.board.is_square_empty(Position(self.position.row, c)) for c in range(1, self.position.col)):
                    moves.append(Position(self.position.row, self.position.col - 2))
    def moves_available(self, pos):
        return super(King, self).moves_available(pos.upper(), True, True, 1)

    def __init__(self, color):
        super().__init__(color)
        if color.lower() == 'black':
            self.shortname = self.shortname.lower()
        elif color.lower() == 'white':
            self.shortname = self.shortname.upper()

class Piece(object):
    def __init__(self, color):
        if color.lower() == 'black':
            self.shortname = self.shortname.lower()
        elif color.lower() == 'white':
            self.shortname = self.shortname.upper()
        self.color = color

START_PATTERN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w 0 1'
class Board(dict):
    y_axis = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
    x_axis = (1, 2, 3, 4, 5, 6, 7, 8)
    captured_pieces = {'white': [], 'black': []}
    player_turn = None
    halfmove_clock = 0
    fullmove_number = 1
    history = []

    def __init__(self, pat=None):
        self.show(START_PATTERN)

    def is_in_check_after_move(self, p1, p2):
        tmp = deepcopy(self)
        tmp.move(p1, p2)
        return tmp.king_in_check(self[p1].color)

    def shift(self, p1, p2):
        p1, p2 = p1.upper(), p2.upper()
        piece = self[p1]
        try:
            dest = self[p2]
        except KeyError:
            dest = None
        if isinstance(piece, Pawn) and abs(self.num_notation(p1)[0] - self.num_notation(p2)[0]) == 2:
            piece.en_passant_target = self.alpha_notation(((self.num_notation(p1)[0] + self.num_notation(p2)[0]) // 2, self.num_notation(p1)[1]))
        else:
            piece.en_passant_target = None

        del self[p1]
        self[p2] = piece
        if isinstance(piece, Pawn) and dest is None and p1[0] != p2[0]:
            del self[p2[0] + p1[1]]
        if piece.color == 'black':
            self.fullmove_number += 1
        self.halfmove_clock += 1
        self.player_turn = 'white' if piece.color == 'black' else 'black'
        abbr = piece.shortname
        if abbr == 'P':
            abbr = ''
            self.halfmove_clock = 0
        if dest is None:
            movetext = abbr + p2.lower()
        else:
            movetext = abbr + 'x' + p2.lower()
            self.halfmove_clock = 0
        piece.en_passant_target = None
        self.history.append(movetext)

    def move(self, p1, p2):
        piece = self[p1]
        try:
            dest = self[p2]
        except KeyError:
            dest = None
        if isinstance(piece, Pawn) and abs(self.num_notation(p1)[0] - self.num_notation(p2)[0]) == 2:
            piece.en_passant_target = self.alpha_notation(((self.num_notation(p1)[0] + self.num_notation(p2)[0]) // 2, self.num_notation(p1)[1]))
        else:
            piece.en_passant_target = None

        del self[p1]
        self[p2] = piece
        if isinstance(piece, Pawn) and dest is None and p1[0] != p2[0]:
            del self[p2[0] + p1[1]]
        if piece.color == 'black':
            self.fullmove_number += 1
        self.halfmove_clock += 1
        self.player_turn = 'white' if piece.color == 'black' else 'black'
        abbr = piece.shortname
        if abbr == 'P':
            abbr = ''
            self.halfmove_clock = 0
        if dest is None:
            movetext = abbr + p2.lower()
        else:
            movetext = abbr + 'x' + p2.lower()
            self.halfmove_clock = 0
        piece.en_passant_target = None
        self.history.append(movetext)
    def complete_move(self, piece, dest, p1, p2):
        enemy = ('white' if piece.color == 'black' else 'black')
        if piece.color == 'black':
            self.fullmove_number += 1
        self.halfmove_clock += 1
        self.player_turn = enemy
        abbr = piece.shortname
        if abbr == 'P':
            abbr = ''
            self.halfmove_clock = 0
        if dest is None:
            movetext = abbr + p2.lower()
        else:
            movetext = abbr + 'x' + p2.lower()
            self.halfmove_clock = 0
        self.history.append(movetext)

    def all_moves_available(self, color):

        result = []
        for coord in self.keys():
            if (self[coord] is not None) and self[coord].color == color:
                moves = self[coord].moves_available(coord)
                if moves: result += moves
        return result

    def occupied(self, color):
        result = []

        for coord in iter(self.keys()):
            if self[coord].color == color:
                result.append(coord)
        return result

    def position_of_king(self, color):
        for pos in self.keys():
            if isinstance(self[pos], King) and self[pos].color == color:
                return pos

    def king_in_check(self, color):
        kingpos = self.position_of_king(color)
        opponent = ('black' if color == 'white' else 'white')
        for pieces in self.items():
            if kingpos in self.all_moves_available(opponent):
                return True
            else:
                return False

    def alpha_notation(self, xycoord):
        if xycoord[0] < 0 or xycoord[0] > 7 or xycoord[1] < 0 or xycoord[
            1] > 7: return
        return self.y_axis[int(xycoord[1])] + str(self.x_axis[int(xycoord[0])])

    def num_notation(self, coord):
        return int(coord[1]) - 1, self.y_axis.index(coord[0])

    def is_on_board(self, coord):
        if coord[1] < 0 or coord[1] > 7 or coord[0] < 0 or coord[0] > 7:
            return False
        else:
            return True

    def show(self, pat):
        self.clear()
        pat = pat.split(' ')

        def expand(match):
            return ' ' * int(match.group(0))

        pat[0] = re.compile(r'\d').sub(expand, pat[0])
        for x, row in enumerate(pat[0].split('/')):
            for y, letter in enumerate(row):
                if letter == ' ': continue
                coord = self.alpha_notation((7 - x, y))
                self[coord] =create_piece(letter)
                self[coord].place(self)
        if pat[1] == 'w':
            self.player_turn = 'white'
        else:
            self.player_turn = 'black'
        self.halfmove_clock = int(pat[2])
        self.fullmove_number = int(pat[3])
class ChessError(Exception): pass
class Check(ChessError): pass
class InvalidMove(ChessError): pass
class CheckMate(ChessError): pass
class Draw(ChessError): pass
class NotYourTurn(ChessError): pass
class InvalidCoord(ChessError): pass
class GUI:
    pieces = {}
    selected_piece = None
    focused = None
    images={}
    color1 = "#FFFFFF"
    color2 = "#555555" 
    highlightcolor = "khaki"
    rows = 8
    columns = 8
    dim_square = 70

    def __init__(self, parent, chessboard):
        self.chessboard = chessboard
        self.parent = parent
        # Adding Top Menu
        self.menubar = tk.Menu(parent)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New Game", command=self.new_game)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.parent.config(menu=self.menubar)

        # Adding Frame
        self.btmfrm = tk.Frame(parent, height=64)
        self.info_label = tk.Label(self.btmfrm,
                                text="   White to Start the Game  ",
                                fg=self.color2)
        self.info_label.pack(side=tk.RIGHT, padx=8, pady=5)
        self.btmfrm.pack(fill="x", side=tk.BOTTOM)

        canvas_width = self.columns * self.dim_square
        canvas_height = self.rows * self.dim_square
        self.canvas = tk.Canvas(parent, width=canvas_width,
                               height=canvas_height)
        self.canvas.pack(padx=8, pady=8)
        self.draw_board()
        self.canvas.bind("<Button-1>", self.square_clicked)

    def new_game(self):
        self.chessboard.show(START_PATTERN)
        self.draw_board()
        self.draw_pieces()
        self.info_label.config(text="   White to Start the Game  ", fg='red')

    def square_clicked(self, event):
        col_size = row_size = self.dim_square
        selected_column = int(event.x / col_size)
        selected_row = 7 - int(event.y / row_size)
        pos = self.chessboard.alpha_notation((selected_row, selected_column))
        if self.selected_piece:
            self.shift(self.selected_piece[1], pos)
            self.selected_piece = None
            self.focused = None
            self.pieces = {}
            self.draw_board()
            self.draw_pieces()
        self.focus(pos)
        self.draw_board()

        # Highlight en passant squares if the selected piece is a pawn
        try:
            piece = self.chessboard[pos]
            if isinstance(piece, Pawn) and self.selected_piece:
                start_pos = self.selected_piece[1]
                end_pos = pos
                if start_pos and end_pos:
                    try:
                        self.chessboard.shift(start_pos, end_pos)
                    except InvalidMove:
                        pass
                    except Check:
                        pass
                    except CheckMate:
                        pass
                    except Draw:
                        pass
                    except NotYourTurn:
                        pass
                self.draw_board()
                self.draw_pieces()
        except KeyError:
            pass

    def shift(self, p1, p2):
        piece = self.chessboard[p1]
        try:
            dest_piece = self.chessboard[p2]
        except:
            dest_piece = None
        if dest_piece is None or dest_piece.color != piece.color:
            try:
                self.chessboard.shift(p1, p2)
            except ChessError as error:
                self.info_label["text"] = error.__class__.__name__
            else:
                turn = ('white' if piece.color == 'black' else 'black')
                self.info_label[
                    "text"] = '' + piece.color.capitalize() + "  :  " + p1 + p2 + '    ' + turn.capitalize() + '\'s turn'
                if isinstance(piece, Pawn) and ((piece.color == 'white' and p2[1] == '8') or (piece.color == 'black' and p2[1] == '1')):
                    self.prompt_promotion(p2, piece.color)
    def prompt_promotion(self, pawn_pos, color):
        promotion_window = tk.Toplevel(self.parent)
        promotion_window.title("Pawn Promotion")
        
        selected_promotion = tk.StringVar()
        selected_promotion.set("Queen") 
        promotion_options = [("Queen", "Q"), ("Rook", "R"), ("Bishop", "B"), ("Knight", "N")]
        for option, piece_type in promotion_options:
            tk.Radiobutton(promotion_window, text=option, variable=selected_promotion, value=piece_type).pack(anchor="w")

        confirm_button = tk.Button(promotion_window, text="Confirm", command=lambda: self.complete_promotion(pawn_pos, selected_promotion.get(), promotion_window, color))
        confirm_button.pack()


    def complete_promotion(self, pawn_pos, selected_piece, promotion_window, color):
        promoted_piece = None
        if selected_piece == 'Q':
            promoted_piece = Queen(color)
        elif selected_piece == 'R':
            promoted_piece = Rook(color)
        elif selected_piece == 'B':
            promoted_piece = Bishop(color)
        elif selected_piece == 'N':
            promoted_piece = Knight(color)

        promoted_piece.place(self.chessboard) 
        self.chessboard[pawn_pos] = promoted_piece
        self.draw_board()
        self.draw_pieces()
        promotion_window.destroy()




    def focus(self, pos):
        try:
            piece = self.chessboard[pos]
        except:
            piece = None
        if piece is not None and (piece.color == self.chessboard.player_turn):
            self.selected_piece = (self.chessboard[pos], pos)
            self.focused = list(map(self.chessboard.num_notation,
                               (self.chessboard[pos].moves_available(pos))))

    def draw_board(self):
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                x1 = (col * self.dim_square)
                y1 = ((7 - row) * self.dim_square)
                x2 = x1 + self.dim_square
                y2 = y1 + self.dim_square
                if (self.focused is not None and (row, col) in self.focused):
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                                                 fill=self.highlightcolor,
                                                 tags="area")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color,
                                                 tags="area")
                color = self.color1 if color == self.color2 else self.color2
        for name in self.pieces:
            self.pieces[name] = (self.pieces[name][0], self.pieces[name][1])
            x0 = (self.pieces[name][1] * self.dim_square) + int(
                self.dim_square / 2)
            y0 = ((7 - self.pieces[name][0]) * self.dim_square) + int(
                self.dim_square / 2)
            self.canvas.coords(name, x0, y0)
        self.canvas.tag_raise("occupied")
        self.canvas.tag_lower("area")

    def draw_pieces(self):
        self.canvas.delete("occupied")
        for coord, piece in self.chessboard.items():
            x, y = self.chessboard.num_notation(coord)
            if piece is not None:
                filename = "pieces_image/%s%s.png" % (
                piece.shortname.lower(), piece.color)
                piecename = "%s%s%s" % (piece.shortname, x, y)
                if filename not in self.images:
                    self.images[filename] = tk.PhotoImage(file=filename)
                self.canvas.create_image(0, 0, image=self.images[filename],
                                         tags=(piecename, "occupied"),
                                         anchor="c")
                x0 = (y * self.dim_square) + int(self.dim_square / 2)
                y0 = ((7 - x) * self.dim_square) + int(self.dim_square / 2)
                self.canvas.coords(piecename, x0, y0)


def main(chessboard):
    root = tk.Tk()
    root.title("Chess")
    gui = GUI(root, chessboard)
    gui.draw_board()
    gui.draw_pieces()
    root.mainloop()


if __name__ == "__main__":
    game = Board()
    main(game)
