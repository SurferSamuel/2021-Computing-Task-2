from tkinter import *
from PIL import ImageTk, Image
import copy

# Create Window
root = Tk()
root.title("Chess")
root.geometry("720x720")
root.configure(bg="#303030")

# Define board colours
board_colour = {'w': "", 'b': ""}

# Create board for the pieces
board = [['0' for file in range(8)] for rank in range(8)]

# Create grid for the squares
squares = [[] for rank in range(8)]

class Piece:
    
    def __init__(self, value, colour, rank, file, square_colour):

        # On the creation of the piece, assign variables
        self.value = value
        self.colour = colour
        self.rank = rank
        self.file = file
        self.selected = False
        self.square_colour = square_colour

        # Create lists for moves and move offsets
        self.moves = []
        self.move_offset = []
        
    def info(self):

        # Return info of the piece (eg. 'bK' for a Black King)
        return self.colour + self.value
    
    def select(self, bg_colour):

        # Select only if the board is not locked
        if locked != True:

            # Get is selected variable
            global is_selected
            
            # Unselect the piece
            if self.selected:

                # Delete image from frame
                self.piece_lbl.destroy()
                
                # Replace the image not highlighted
                self.place(None)

                # Update variables
                self.selected = False
                is_selected = False

                # Remove valid moves of the piece that is selected
                self.hide_moves()

            # Check if this is a capture target
            elif not self.selected and is_selected:

                # Get the already selected piece
                for rank in board:
                    for piece in rank:
                        if piece != '0' and piece.selected:
                            selected_piece = piece

                # If this piece is in the valid moves of the already selected piece, then capture
                if (self.rank, self.file) in selected_piece.moves:
                    selected_piece.capture(self)

            # Select the piece 
            elif not self.selected and not is_selected and self.colour == current_turn:

                # Delete image from frame
                self.piece_lbl.destroy()

                # Replace the image highlighted
                highlighted_image = Image.open("materials/highlight.png")
                self.place(highlighted_image)

                # Update variables
                self.selected = True
                is_selected = True

                # Show valid moves of the piece that is selected
                self.generate_legal_moves()
                self.highlight_moves()

    def place(self, bg_image):
        
        # Get required info
        pieceinfo = self.info()
        piece_frame = squares[self.rank][self.file]

        # Get piece image from resource folder
        pieceimage = Image.open("materials/{}.png".format(pieceinfo))
    
        # Keep frame a set size (don't let the image determine the size of the frame)
        piece_frame.pack_propagate(0)

        # If background is pre-defined
        if bg_image is not None:

            # Overlay the piece image onto the background
            bg_image.paste(pieceimage, None, pieceimage)
            tkpieceimage = ImageTk.PhotoImage(bg_image)

        # If background is not pre-defined
        else:
            # Convert image into TkPhoto object
            tkpieceimage = ImageTk.PhotoImage(pieceimage)

        # Create image with same background colour as the frame it's in
        self.piece_lbl = Label(piece_frame, image=tkpieceimage, bg=piece_frame["background"])
        self.piece_lbl.image = tkpieceimage
            
        # Bind mouse click to select the piece 
        self.piece_lbl.bind('<Button-1>', self.select)

        # Place image in frame
        self.piece_lbl.pack()

    def delete(self, image, piece):

        # Delete image from frame
        if image:
            self.piece_lbl.destroy()

        # Delete itself from the board ('0' defaults as an empty square)
        if piece:
            board[self.rank][self.file] = '0'

    def highlight_moves(self):

        # Highlight moves
        for target_rank, target_file in self.moves:

            # Get target piece and square
            target_piece = board[target_rank][target_file]
            target_frame = squares[target_rank][target_file]

            # If there is not a piece on the target square
            if target_piece == '0':

                # Get circle image from resource folder
                circleimage = ImageTk.PhotoImage(file="materials/circle_1.png")
        
                # Keep frame a set size (don't let the image determine the size of the frame)
                target_frame.pack_propagate(0)

                # Create image with same background colour as the frame it's in
                circle = Label(target_frame, image=circleimage, bg=target_frame["background"])
                circle.image = circleimage

                # Bind click to move the piece, and pass on the target variables
                circle.bind('<Button-1>', lambda event, r=target_rank, f=target_file: self.move_piece(r, f)) 

                # Place the image
                circle.pack()

            # If there is a piece in the target square
            elif target_piece != '0':

                # Get circle image from resource folder
                circleimage = Image.open("materials/circle_2.png")

                # Replace the target piece with a circle around it
                target_piece.delete(True, False)
                target_piece.place(circleimage)

        # If the piece is a pawn, highlight any en passant moves
        if self.value == 'P':

            # If there is a en passant move
            if self.en_passant_move != None:

                # Get target square of the en passant move
                target_rank, target_file = self.en_passant_move
                target_frame = squares[target_rank][target_file]

                # Get circle image from resource folder
                circleimage = ImageTk.PhotoImage(file="materials/circle_1.png")
            
                # Keep frame a set size (don't let the image determine the size of the frame)
                target_frame.pack_propagate(0)

                # Create image with same background colour as the frame it's in
                circle = Label(target_frame, image=circleimage, bg=target_frame["background"])
                circle.image = circleimage

                # Bind click to move the piece, and pass on the target variables
                circle.bind('<Button-1>', lambda event, r=target_rank, f=target_file: self.pawn_en_passant_move(r, f)) 

                # Place the image
                circle.pack()

        # If the piece is a king, highlight any castling moves
        if self.value == 'K':

            for target_rank, target_file in self.castling_moves:

                # Get target square
                target_frame = squares[target_rank][target_file]

                # Get circle image from resource folder
                circleimage = ImageTk.PhotoImage(file="materials/circle_1.png")
        
                # Keep frame a set size (don't let the image determine the size of the frame)
                target_frame.pack_propagate(0)

                # Create image with same background colour as the frame it's in
                circle = Label(target_frame, image=circleimage, bg=target_frame["background"])
                circle.image = circleimage

                # Bind click to move the piece, and pass on the target variables
                circle.bind('<Button-1>', lambda event, r=target_rank, f=target_file: self.king_castling_move(r, f)) 

                # Place the image
                circle.pack()

    def generate_moves(self, board, check_castling):

        # Reset any existing moves
        self.moves = []
        self.move_offset = []
        
        # Pawn Moves
        if self.value == 'P':
            self.pawn_moves(board)
            self.get_en_passant_moves(board)

        # Rook Moves
        if self.value == 'R':
            self.sliding_moves(board, 0, 3)    # 0-3 is for straight directions

        # Bishop Moves
        if self.value == 'B':
            self.sliding_moves(board, 4, 7)    # 4-7 is for diagonal directions

        # Queen Moves
        if self.value == 'Q':
            self.sliding_moves(board, 0, 7)    # 0-7 is for diagonal and straight directions

        # Knight Moves
        if self.value == 'N':
            self.knight_moves(board)

        # King Moves
        if self.value == 'K':
            self.king_moves(board)

            # If check castling is true
            if check_castling:
                self.get_castling_moves(board)

    def generate_legal_moves(self):

        # Generate pseudo legal moves (moves that aren't necessarily legal) & check for castling
        self.generate_moves(board, True)

        # Create variable of removed moves
        self.removed_moves = []

        # Check if each pseudo legal move is legal
        for pseudo_move in self.moves:

            # Create a temporary copy of the current board
            temp_board = []
            for piece in board:

                # Use copy() to create new class instances of the pieces
                temp_board.append(copy.copy(piece))

            # Get target piece of the move
            target_rank = pseudo_move[0]
            target_file = pseudo_move[1]
            target_piece = temp_board[target_rank][target_file]

            # Play the move on the temp board
            temp_board[target_rank][target_file] = Piece(self.value, self.colour, target_rank, target_file, colour_of_square(squares[target_rank][target_file]))
            temp_board[self.rank][self.file] = '0'

            # Check if any opponents responses include taking the king
            if self.check_for_attacked_king(temp_board, change_turn(self.colour)):

                # If so, then the last move was not legal
                self.removed_moves.append(pseudo_move)

        # Remove the non-legal moves
        for move in set(self.removed_moves):
                
            self.moves.remove(move)

    def check_for_attacked_king(self, board, colour):

        # Check if the king can be captured by the inputed colour's pieces
        for rank in board:

                for piece in rank:
                    
                    # Get the pieces of the inputed colour
                    if piece != '0' and piece.colour == colour:

                        # Generate moves for the piece (don't check for castling)
                        piece.generate_moves(board, False)

                        # Check if a move consists of taking the king
                        for move_rank, move_file in piece.moves:

                            # Get the target piece of the move
                            move_target = board[move_rank][move_file]

                            # Return true if the piece target is a king
                            if move_target != '0' and move_target.value == 'K':
                                return True

        # If passed all moves, then reutrn False
        return False

    def pawn_moves(self, board):

        # White Pawn
        if self.colour == 'w':

            # Starting rank and move offset 
            self.start_rank = 6
            self.move_offset.append((-1, 0))

        # Black Pawn
        elif self.colour == 'b':

            # Starting rank and move offset 
            self.start_rank = 1
            self.move_offset.append((1, 0))

        # Capture move offsets
        self.move_offset.append((self.move_offset[0][0], 1))
        self.move_offset.append((self.move_offset[0][0], -1))
                                    
        # Get target rank and file
        target_rank, target_file = self.rank + self.move_offset[0][0], self.file

        # Check if the move is on the board
        if not target_rank > 7 or target_rank < 0:

            # If the square in front of the pawn is not currently occupied by another piece
            if board[target_rank][target_file] == '0':

                # Add the move
                self.moves.append((target_rank, target_file))

                # Check if the pawn hasn't moved
                if self.start_rank == self.rank:

                    # Get 2 square forward move position
                    target_rank, target_file = self.rank + (self.move_offset[0][0] * 2), self.file

                    # If the square two squares in front of the pawn is not occupied by another piece
                    if board[target_rank][target_file] == '0':

                        # Add the move
                        self.moves.append((target_rank, target_file))

            # Check if the pawn can capture diagonally
            for rank_offset, file_offset in self.move_offset[1:]:

                # Get target rank and file
                target_rank = self.rank + rank_offset
                target_file = self.file + file_offset
                    
                # Check if target square exists on the board
                try:
                    target_square = board[target_rank][target_file]
                    if target_rank < 0 or target_file < 0:
                        continue
                except IndexError:
                    continue

                # Check if there is an enemy piece at the target square
                if target_square != '0' and target_square.colour != self.colour:
                    self.moves.append((target_rank, target_file))

    def get_en_passant_moves(self, board):

        # Remove any existing en passant moves
        self.en_passant_move = None

        # Check if there is an en passant target square
        if en_passant_target != None:

            # Check if the pawn can capture diagonally the en passant target
            for rank_offset, file_offset in self.move_offset[1:]:

                # Get target rank and file
                target_rank = self.rank + rank_offset
                target_file = self.file + file_offset
                        
                # Check if target square exists on the board
                try:
                    target_square = board[target_rank][target_file]
                    if target_rank < 0 or target_file < 0:
                        continue
                except IndexError:
                    continue

                # Check if the target square is the en passant target
                if (target_rank, target_file) == en_passant_target:

                    # If there target sqaure is the en passant capture, check if move is legal
                    # Create a temporary copy of the current board
                    temp_board = []
                    for piece in board:

                        # Use copy() to create new class instances of the pieces
                        temp_board.append(copy.copy(piece))

                    # Move the pawn to the en passant capture sqaure
                    temp_board[target_rank][target_file] = Piece(self.value, self.colour, target_rank, target_file, colour_of_square(squares[target_rank][target_file]))
                    temp_board[self.rank][self.file] = '0'

                    # Check if any opponents responses does not include taking the king
                    if not self.check_for_attacked_king(temp_board, change_turn(self.colour)):

                        # If so, then the en passant is legal
                        self.en_passant_move = (target_rank, target_file)

    def sliding_moves(self, board, start_dir, end_dir):

        # Straight move offsets
        self.move_offset.append((-1, 0))    # Up   
        self.move_offset.append((1, 0))     # Down
        self.move_offset.append((0, -1))    # Left
        self.move_offset.append((0, 1))     # Right

        # Diagonal move offsets
        self.move_offset.append((-1, -1))   # Up Left
        self.move_offset.append((-1, 1))    # Up Right
        self.move_offset.append((1, -1))    # Down Left
        self.move_offset.append((1, 1))     # Down Right

        # Get moves in each direction
        for direction in range(start_dir, end_dir + 1):

            # Reset move multiple
            move_multiple = 0

            # Loop until all moves in direction has been found
            while True:

                # Increment move multiplier
                move_multiple += 1

                # Get target rank and file
                target_rank = self.rank + (self.move_offset[direction][0] * move_multiple)
                target_file = self.file + (self.move_offset[direction][1] * move_multiple)

                # Check if target square exists on the board
                try:
                    target_square = board[target_rank][target_file]
                    if target_rank < 0 or target_file < 0:
                        break
                except IndexError:
                    break

                # Check if there is not a frienly piece at the target square 
                if (target_square != '0' and target_square.colour == self.colour):
                    break
                    
                # Add the move
                self.moves.append((target_rank, target_file))

                # If there is any enemy piece at the target square, then this is the last move for the direction
                if target_square != '0':
                    break

    def knight_moves(self, board):

        # Knight move offsets
        self.move_offset.append((-2, -1))   # Up 2 Left 1
        self.move_offset.append((-2, 1))    # Up 2 Right 1
        self.move_offset.append((-1, -2))   # Up 1 Left 2
        self.move_offset.append((-1, 2))    # Up 1 Right 2
        self.move_offset.append((1, -2))    # Down 1 Left 2
        self.move_offset.append((1, 2))     # Down 1 Right 2
        self.move_offset.append((2, -1))    # Down 2 Left 1
        self.move_offset.append((2, 1))     # Down 2 Right 1

        # Get move (or not) in each direction
        for move in self.move_offset:

            # Get target rank and file
            target_rank = self.rank + move[0]
            target_file = self.file + move[1]

            # Check if target square exists on the board
            try:
                target_square = board[target_rank][target_file]
                if target_rank < 0 or target_file < 0:
                    continue
            except IndexError:
                continue

            # Check if there is not a frienly piece at the target square 
            if (target_square != '0' and target_square.colour == self.colour):
                continue
                    
            # Add the move
            self.moves.append((target_rank, target_file))

    def king_moves(self, board):

        # King move offsets
        self.move_offset.append((-1, 0))    # Up   
        self.move_offset.append((1, 0))     # Down
        self.move_offset.append((0, -1))    # Left
        self.move_offset.append((0, 1))     # Right
        self.move_offset.append((-1, -1))   # Up Left
        self.move_offset.append((-1, 1))    # Up Right
        self.move_offset.append((1, -1))    # Down Left
        self.move_offset.append((1, 1))     # Down Right

        # Get move (or not) in each direction
        for move in self.move_offset:

            # Get target rank and file
            target_rank = self.rank + move[0]
            target_file = self.file + move[1]

            # Check if target square exists on the board
            try:
                target_square = board[target_rank][target_file]
                if target_rank < 0 or target_file < 0:
                    continue
            except IndexError:
                continue

            # Check if there is not a frienly piece at the target square 
            if (target_square != '0' and target_square.colour == self.colour):
                continue
                    
            # Add the move
            self.moves.append((target_rank, target_file))

    def get_castling_moves(self, board):

        # Reset any existing castling moves
        self.castling_moves = []

        # If player is still legible to castle short
        if castling_short[self.colour] != False:

            # Check if there are not any pieces blocking the castling move
            if board[self.rank][self.file + 1] == '0' and board[self.rank][self.file + 2] == '0':

                # Check if the king doesn't excape check
                if self.check_for_attacked_king(board, change_turn(self.colour)) != True:

                    # Check if the king doesn't pass through check or go into check
                    if self.check_castling(board, [1, 2]):

                        # If all checks are passed, then king can legally castle short
                        self.castling_moves.append((self.rank, self.file + 2))

        # If player is still legible to castle long
        if castling_long[self.colour] != False:

            # Check if there are not any pieces blocking the castling move
            if board[self.rank][self.file - 1] == '0' and board[self.rank][self.file - 2] == '0' and board[self.rank][self.file - 3] == '0':

                # Check if the king doesn't excape check
                if self.check_for_attacked_king(board, change_turn(self.colour)) != True:

                    # Check if the king doesn't pass through check or go into check
                    if self.check_castling(board, [-1, -2, -3]):

                        # If all checks are passed, then king can legally castle long
                        self.castling_moves.append((self.rank, self.file - 2))

    def check_castling(self, board, offsets):

        # Check if the king doesn't pass through check or go into check
        for offset in offsets:

            # Create a temporary copy of the current board
            temp_board = []
            for piece in board:

                # Use copy() to create new class instances of the pieces
                temp_board.append(copy.copy(piece))

            # Move the king over in it's rank by the offset
            temp_board[self.rank][self.file + offset] = Piece(self.value, self.colour, self.rank, self.rank + offset, colour_of_square(squares[self.rank][self.file + offset]))
            temp_board[self.rank][self.file] = '0'

            # Check if the king is not in check
            if self.check_for_attacked_king(temp_board, change_turn(self.colour)):

                # If the king is in check, then castling is not a legal move
                return False

        # If passes all moves, then castling is a legal move
        return True
            

    def evaluate(self):

        global locked

        # Check if opponent has any legal moves
        opponent_legal_moves = []
            
        for rank in board:
                
            for piece in rank:

                # Get the enemy pieces
                if piece != '0' and piece.colour != self.colour:

                    # Generate legal moves for that piece
                    piece.generate_legal_moves()

                    # If the piece has legal moves, add them to the list
                    if piece.moves:
                        opponent_legal_moves.append(piece.moves)

        # Check if move puts opponent's king in check / checkmate
        if self.check_for_attacked_king(board, self.colour):

            # If the opponent has no legal moves and is in check, then checkmate
            if not opponent_legal_moves:

                # Lock the board
                locked = True
                
                # Find the winner
                if self.colour == 'w':
                    winner_text = "WHITE WINS!"
                elif self.colour == 'b':
                    winner_text = "BLACK WINS!"

                # Create checkmate label
                checkmate_lbl = Label(boardframe, text=winner_text, bg="#303030", fg="White", font="comicsans 96", width=720)
                checkmate_lbl.place(x=360, y=360, anchor=CENTER)

                # Update the board and after 5 seconds (5000 milliseconds) delete the label
                root.update()
                root.after(5000, checkmate_lbl.destroy())

            # If the opponent does have legal moves and is in check, then check
            else:
                # Create check label
                check_lbl = Label(boardframe, text="CHECK", bg="#303030", fg="White", font="comicsans 96", width=720)
                check_lbl.place(x=360, y=360, anchor=CENTER)

                # Update the board and after 2 seconds (2000 milliseconds) delete the label
                root.update()
                root.after(2000, check_lbl.destroy())

        # Check for draw by stalemate
        else:

            # If the opponent has no legal moves and is not in check, then stalemate
            if not opponent_legal_moves:

                # Lock the board
                locked = True

                # Create stalemate label
                stalemate_lbl = Label(boardframe, text="STALEMATE", bg="#303030", fg="White", font="comicsans 96", width=720)
                stalemate_lbl.place(x=360, y=360, anchor=CENTER)

                # Update the board and after 5 seconds (5000 milliseconds) delete the label
                root.update()
                root.after(5000, stalemate_lbl.destroy())

    def pawn_promotion(self, rank, file):

        # Get the piece on the target square
        piece = board[rank][file]

        # Check if the piece is a pawn
        if piece != '0' and piece.value == 'P':

            # White pawn promotion rank
            if piece.colour == 'w':
                piece.promote_rank = 0
                
            # Black pawn promotion rank
            elif piece.colour == 'b':
                piece.promote_rank = 7

            # Check if the pawn is on the promotion rank
            if piece.rank == piece.promote_rank:

                # If so, prompt the user with a window to choose promotion piece
                promotion_window(piece)

    def hide_moves(self):

        # Add any castling moves 
        if self.value == 'K':
            moves = self.moves + self.castling_moves
        else:
            moves = self.moves

        # Add any en passant moves
        if self.value == 'P' and self.en_passant_move != None:
            self.moves.append(self.en_passant_move)
            moves = self.moves

        # Unhighlight moves back to original square colour
        for target_rank, target_file in moves:

            # Get target piece and square
            target_piece = board[target_rank][target_file]
            target_frame = squares[target_rank][target_file]

            # If the square is empty, remove the circle
            if target_piece == '0':

                # Destory the image inside the frame    
                for image in target_frame.winfo_children():
                    image.destroy()

            # If the square is not empty, remove the circle from the piece 
            else:

                # Replace the image without the circle around it
                target_piece.delete(True, False)
                target_piece.place(None)    

    def move_piece(self, target_rank, target_file):

        # Unhighlight existing moves
        self.hide_moves()

        # Update castling availability
        self.castling_availability()

        # If pawn just did a double move, update the en passant target square
        global en_passant_target
        if self.value == 'P' and self.rank + 2 * self.move_offset[0][0] == target_rank:

            # Set the en passant target square one square behind the double move
            en_passant_target = (self.rank + self.move_offset[0][0], self.file)

        else:
            # Else reset the en passant target
            en_passant_target = None

        # Move the piece to the target square
        board[target_rank][target_file] = Piece(self.value, self.colour, target_rank, target_file, colour_of_square(squares[target_rank][target_file]))
        board[target_rank][target_file].place(None)
            
        # Once the piece is placed, delete the old piece
        self.delete(True, True)

        # Check for pawn promotion
        self.pawn_promotion(target_rank, target_file)

        # Update the move to the board
        self.update_move()

    def pawn_en_passant_move(self, target_rank, target_file):

        # Reset the en passant target square
        global en_passant_target
        en_passant_target = None

        # Unhighlight existing moves
        self.hide_moves()

        # Get the pawn target of the en passant capture
        target_pawn = board[target_rank - self.move_offset[0][0]][target_file]

        # Delete the captured pawn
        target_pawn.delete(True, True)

        # Move the pawn to the en passant capture location
        board[target_rank][target_file] = Piece(self.value, self.colour, target_rank, target_file, colour_of_square(squares[target_rank][target_file]))
        board[target_rank][target_file].place(None)

        # Once the piece is placed, delete the old piece
        self.delete(True, True)

        # Update the move to the board
        self.update_move()
        

    def king_castling_move(self, target_rank, target_file):

        # Unhighlight existing moves
        self.hide_moves()

        # Update castling availability
        self.castling_availability()

        # Find and move the required rook
        if target_file > self.file:
            # Rook on king side
            rook = board[self.rank][7]
            board[target_rank][target_file - 1] = Piece(rook.value, self.colour, target_rank, target_file - 1, colour_of_square(squares[target_rank][target_file - 1]))
            board[target_rank][target_file - 1].place(None)
        else:
            # Rook on queen side
            rook = board[self.rank][0]
            board[target_rank][target_file + 1] = Piece(rook.value, self.colour, target_rank, target_file + 1, colour_of_square(squares[target_rank][target_file + 1]))
            board[target_rank][target_file + 1].place(None)

        # Move the king to the new square
        board[target_rank][target_file] = Piece(self.value, self.colour, target_rank, target_file, colour_of_square(squares[target_rank][target_file]))
        board[target_rank][target_file].place(None)

        # Delete old pieces
        rook.delete(True, True)
        self.delete(True, True)
        
        # Update the move to the board
        self.update_move()

    def capture(self, target_piece):

        # Unhighlight existing moves
        self.hide_moves()

        # Update castling availability
        self.castling_availability()

        # Get the capture location
        capture_rank, capture_file = target_piece.rank, target_piece.file

        # Delete the captured pieces from the board
        target_piece.delete(True, True)

        # Move the capturing piece to where the capture piece is
        board[capture_rank][capture_file] = Piece(self.value, self.colour, capture_rank, capture_file, colour_of_square(squares[capture_rank][capture_file]))
        board[capture_rank][capture_file].place(None)

        # Once the piece is placed, delete the old piece
        self.delete(True, True)

        # Check for pawn promotion
        self.pawn_promotion(capture_rank, capture_file)

        # Update the move to the board
        self.update_move()

    def update_move(self):

        # Update selected variable
        global is_selected
        is_selected = False

        # Check for check/checkmate
        self.evaluate()

        # Switch player's turn
        global current_turn
        current_turn = change_turn(self.colour)

    def castling_availability(self):

        global castling_short, castling_long

        # If the moved piece was a king, revoke castling privileges for that colour 
        if self.value == 'K':

            castling_short[self.colour] = False
            castling_long[self.colour] = False

        # If the moved piece was a rook, revoke castling privileges only for that side (ie. short / long)
        if self.value == 'R':

            # Queen side (long)
            if self.file == 0:
                castling_long[self.colour] = False

            # King side (short)
            if self.file == 7:
                castling_short[self.colour] = False

def start():

    ''' Title Header '''
    # Title frame
    global title_frame
    title_frame = Frame(root, bg="#303030")
    title_frame.pack()

    # Title content
    title_1_lbl = Label(title_frame, text="CHESS", font="comicsans 92", bg="#303030", fg="White")
    title_1_lbl.pack(pady=(80, 0))
    title_2_lbl = Label(title_frame, text="Created By: Samuel Johnston", font="comicsans 14", bg="#303030", fg="White")
    title_2_lbl.pack(pady=(0, 60))

    ''' Custom Board Selection '''
    # Fen for board editor
    global fen
    fen = StringVar()
    fen.set("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    
    # Create custom board position frame
    global board_position_editor
    board_position_editor = Frame(root, bg="#303030")
    board_position_editor.pack()

    # Show editor title
    custom_board_lbl = Label(board_position_editor, text="CUSTOMISE BOARD POSITION", font="comicsans 14", bg="#303030", fg="White")
    custom_board_lbl.pack(pady=(0, 10))

    # Show the fen editor
    fen_frame = Frame(board_position_editor, bg="#303030")
    fen_lbl = Label(fen_frame, text="Board Fen:", font="comicsans 12", bg="#303030", fg="White")
    fen_entry = Entry(fen_frame, textvariable=fen, width="50", highlightbackground="#303030")
    fen_lbl.pack(side=LEFT, padx=(0, 10))
    fen_entry.pack(side=RIGHT)
    fen_frame.pack(pady=(0, 20))

    ''' Custom Colour Selection '''
    # Colours for board
    global colour_b, colour_w
    colour_b, colour_w = StringVar(), StringVar()
    colour_b.set("#f8dcb4")
    colour_b.trace("w", lambda name, index, mode: update_colours())
    colour_w.set("#b88c64")
    colour_w.trace("w", lambda name, index, mode: update_colours())
    
    # Create colour editor frame
    global colour_editor
    colour_editor = Frame(root, bg="#303030")
    colour_editor.pack()

    # Show editor title
    custom_colour_lbl = Label(colour_editor, text="CUSTOMISE BOARD COLOUR", font="comicsans 14", bg="#303030", fg="White")
    custom_colour_lbl.pack(pady=(0, 10))

    # Show the colour editor
    colour_frame = Frame(colour_editor, bg="#303030")

    # Split colour frame into 3 sections horizontally
    colour_lbl = Frame(colour_frame, bg="#303030")
    colour_lbl.pack(side=LEFT)
    colour_entry = Frame(colour_frame, bg="#303030")
    colour_entry.pack(side=LEFT)
    colour_display = Frame(colour_frame, bg="#303030")
    colour_display.pack(side=RIGHT)

    # Section 1: Labels
    colour_1_lbl = Label(colour_lbl, text="White Colour:", font="comicsans 12", bg="#303030", fg="White")
    colour_1_lbl.pack(padx=(0, 10), pady=(0, 2))
    colour_2_lbl = Label(colour_lbl, text="Black Colour:", font="comicsans 12", bg="#303030", fg="White")
    colour_2_lbl.pack(padx=(0, 10), pady=(2, 0))

    # Section 2: Entry Boxes
    colour_1_entry = Entry(colour_entry, textvariable=colour_b, width="15", highlightbackground="#303030")
    colour_1_entry.pack()
    colour_2_entry = Entry(colour_entry, textvariable=colour_w, width="15", highlightbackground="#303030")
    colour_2_entry.pack()

    # Section 3: Updating colour frames
    global colour_1_display, colour_2_display
    colour_1_display = Frame(colour_display, bg=colour_b.get(), height="22", width="50")
    colour_1_display.pack(padx="3", pady="3")
    colour_2_display = Frame(colour_display, bg=colour_w.get(), height="22", width="50")
    colour_2_display.pack(padx="3", pady="3")

    colour_frame.pack(pady=(0, 20))

    ''' Start Button '''
    global start_button
    start_button = Label(root, text="START", font="comicsans 32", bg="#303030", fg="White")
    start_button.pack(pady=(50, 0))
    start_button.bind("<Button-1>", start_game)

def update_colours():

    # When entry box is edited, update the colour of the frames
    # If the colour doesn't exist, update the colour to white
    
    try:
        colour_1_display.config(bg=colour_b.get())
    except:
        colour_1_display.config(bg="white")

    try:
        colour_2_display.config(bg=colour_w.get())
    except:
        colour_2_display.config(bg="white")

def start_game(event):

    # Get the start fen from the entry box
    start_fen = fen.get()

    # Update the colours of the board
    global board_colour
    board_colour['w'] = colour_1_display['bg']
    board_colour['b'] = colour_2_display['bg']

    # Delete the opening screen widgets
    for element in [title_frame, board_position_editor, colour_editor, start_button]:
        element.destroy()

    # Create the board and place pieces
    create_board()
    fen_to_board(start_fen)

    # After board creation, no pieces are selected
    global is_selected
    is_selected = False

def create_board():

    # Create the board's frame
    global boardframe
    boardframe = Frame(root)
    boardframe.pack()

    # Create each tile as a sperate frame
    for rank in range(8):
        
        for file in range(8):

            # Create the frame with a black background, and add it into the squares list
            squares[rank].append(Frame(boardframe, highlightthickness=0, bg=board_colour['b'], height=90, width=90))

            # If rank + file is an even number, the colour is white
            if ((rank + file) % 2) == 0:

                # Change the colour of the square to white
                squares[rank][file].config(bg=board_colour['w'])

            # Place the frame on the board
            squares[rank][file].grid(column=file, row=rank)

    # Board is made unlocked by default
    global locked
    locked = False

def fen_to_board(fen):

    # Get board 
    global board

    # Split the fen into 6 sections
    sections = fen.split(' ')

    ''' 1st Section: Position section '''
    # Set file and rank as 0 (starting at the top left square)
    file, rank = 0, 0
    
    for symbol in sections[0]:

        # If symbol is "/", start at the next rank
        if symbol == "/":
            file = 0
            rank += 1

        # If symbol is anything else (not "/")
        else:

            # Test if symbol is an int
            try:
                file += int(symbol)

            # If symbol is not an int, then it is a piece
            except ValueError:

                # Uppercase = White
                if symbol.isupper():
                    piece_colour = "w"
                    
                # Lowercase = Black
                else:
                    piece_colour = "b"

                # Get colour of the square the piece is on
                square_colour = colour_of_square(squares[rank][file])

                # Create and place the piece
                board[rank][file] = Piece(symbol.upper(), piece_colour, rank, file, square_colour)
                board[rank][file].place(None)

                # Increment the file
                file += 1

    ''' 2nd Section: Current player's turn '''
    global current_turn

    # Update current player's turn
    current_turn = sections[1]

    ''' 3rd Section: Castling availability '''
    global castling_long, castling_short

    # Create variables with no castling availability 
    castling_long = {'w': False, 'b': False}
    castling_short = {'w': False, 'b': False}

    # Assign castling availability (if there is any)
    for symbol in sections[2]:

        # If there is castling availability
        if symbol != '-':

            # Find colour target
            if symbol.isupper():
                colour = 'w'
            else:
                colour = 'b'

            # Determine weither long or short
            if symbol.lower() == 'k':
                castling_short[colour] = True
            else:
                castling_long[colour] = True

    ''' 4th Section: En Passant Target Square '''
    global en_passant_target

    # If there is an en passant target square
    if sections[3] != '-':

        # Get position of the en passant taregt square
        file_letter, rank_num = sections[3]

        # Convert position (ie e4) into indexs (e4 to (4, 4))
        rank = 8 - int(rank_num)
        file = ord(file_letter) - 97

        # Update en passant target square
        en_passant_target = (rank, file)

    # If there is not an en passant target square
    else:

        # Update en passant target square
        en_passant_target = None
            
def promotion_window(target_pawn):

    # Create a new window
    global promote_window
    promote_window = Toplevel(root)
    promote_window.title("Promotion")
    promote_window.configure(bg="#b88c64")

    # Get colour of pawn
    colour = target_pawn.colour

    # Create counter
    col_counter = 0

    # Generate image for each promotion
    for piece, bg_colour in [('Q', 'b'), ('R', 'w'), ('B', 'b'), ('N', 'w')]:

        col_counter += 1
        image = ImageTk.PhotoImage(file="materials/{}{}.png".format(colour, piece))
        lbl = Label(promote_window, image=image, bg=board_colour[bg_colour])
        lbl.image = image
        lbl.bind('<Button-1>', lambda event, t=target_pawn, v=piece: promote(t, v)) 
        lbl.grid(column=col_counter, row=0)

    # Lock board until promotion is made
    global locked
    locked = True

def promote(target_pawn, value):

    # Destroy the promotion window
    promote_window.destroy()
    
    # Handle promotion variables
    target_pawn.delete(True, False)
    target_pawn.value = value
    target_pawn.place(None)

    # Unlock board 
    global locked
    locked = False

def colour_of_square(target):
    
    # Get hex colour of the target square 
    hex_colour = target['bg']

    # Convert hex into colour
    if hex_colour == board_colour['w']:
        return 'w'
    else:
        return 'b'

def change_turn(colour):

    # Return the colour of the other player
    if colour == 'w':
        return 'b'
    else:
        return 'w'

start()

mainloop()
