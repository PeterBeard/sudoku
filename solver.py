# Sudoku solver
# 
# This solver uses a simple brute-force algorithm to solve sudoku puzzles

from random import choice
from copy import deepcopy
from time import sleep

# Return a list of all possible values for a given square
def possible_values(board, row, col):
	row_values = []
	col_values = []
	square_values = []
	# Find the values in the current row
	for i in range(0,9):
		if len(board[row][i]) == 1:
			row_values.append(board[row][i][0])
	# Find the values in the current column
	for i in range(0,9):
		if len(board[i][col]) == 1:
			col_values.append(board[i][col][0])
	# Find the values already in the current square
	sq_start_row = int(row/3)*3
	sq_start_col = int(col/3)*3
	for i in range(sq_start_row, sq_start_row+3):
		for j in range(sq_start_col, sq_start_col+3):
			if len(board[i][j]) == 1:
				square_values.append(board[i][j][0])
	
	values = []
	# Try every number and see if it's valid in the given square
	for val in range(1,10):
		if val not in row_values and val not in col_values and val not in square_values:
			values.append(val)
	# Return an array of possible values for this square
	return values

# Check whether the value in a square is valid
def check_value(board, row, col):
	# Every square has only one valid value
	if len(board[row][col]) > 1:
		return False

	value = board[row][col][0]
	sq_start_row = int(row/3)*3
	sq_start_col = int(col/3)*3
	# Make sure the value is unique in its row
	for i in range(0,9):
		if i != col and board[row][i][0] == value and len(board[row][i]) == 1:
			return False
	# Make sure the value is unique in its column
	for i in range(0,9):
		if i != row and board[i][col][0] == value and len(board[i][col]) == 1:
			return False
	# Make sure the value is unique in its square
	for i in range(0,3):
		for j in range(0,3):
			sq_i = sq_start_row + i
			sq_j = sq_start_col + j
			if sq_i != row and sq_j != col and board[sq_i][sq_j][0] == value and len(board[sq_i][sq_j]) == 1:
				return False
	# If all of the tests passed, the value is valid
	return True

# Load a puzzle from a text file
# This function assumes that the file has nine lines, each with nine digits where '0' represents an empty square
# Returns a 3D (9x9x[0/1]) array containing the initial values for each square. Empty squares are initialized to an empty list.
def load_puzzle(filename):
	board = []
	fh = open(filename,'r')
	i = 0
	for line in fh:
		board.append([])
		for char in line:
			if char in ['1','2','3','4','5','6','7','8','9']:
				board[i].append([int(char)])
			elif char == '0':
				board[i].append([])
		i += 1
	fh.close()
	return board

# Display the board in a terminal
def show_board(board, show_options=False):
	print
	# Print each row of the board (assumes board is 9x9)
	for i in range(0,9):
		print ' ',
		for j in range(0,9):
			if len(board[i][j]) == 1:
				print board[i][j][0],
			else:
				if show_options:
					print board[i][j],
				else:
					print '?',
			# Print lines between the squares
			if (j+1) % 3 == 0 and j < 8:
				print '|',
		print
		if (i+1) % 3 == 0 and i < 8:
			print '  ' + '- '*10 + '-'
	print

# Determine whether the given board contains a solved puzzle
# If all squares have only one possible value and that value is valid, then the puzzle is solved
def is_solved(board):
	# Make sure each square only has one value
	for i in range(0,9):
		for j in range(0,9):
			if len(board[i][j]) != 1:
				return False
	# Make sure each square has a valid value
	for i in range(0,9):
		for j in range(0,9):
			if not check_value(board, i, j):
				return False
	return True

# Solve the puzzle using a naive iterative method
# This method assumes that at least one square will have only one possible solution at the beginning of the puzzle
# It works well with simple puzzles, but complex puzzles requiring logic to solve are not soluble with this approach
def naive_solver(board):
	iterations = 0
	unsolvable = False
	# Iterate over the board until the puzzle is either solved or no more progress can be made
	while not is_solved(board) and not unsolvable:
		unsolvable = True
		for i in range(0,9):
			for j in range(0,9):
				# If this square has either multiple possible values or no values, list the valid values for this square and put them in the data structure
				if len(board[i][j]) != 1:
					new_values = possible_values(board, i, j)
					board[i][j] = new_values
					# If this square now only has one possibility, progress has been made and the puzzle is not necessarily in an unsolvable state
					if len(new_values) == 1:
						unsolvable = False
		iterations += 1
	return (board, iterations)

# Solve the puzzle using a stochastic method
# This approach tries a random selection of possible values in the unsolved squares and marks where the errors occur
# The marked squares are then shuffled and the process is repeated until a solution is reached
# TODO: Finish this algorithm
def stochastic_solver(board):
	iterations = 0
	ITER_MAX = 10000
	while not is_solved(board) and iterations < ITER_MAX:
		test_board = deepcopy(board)
		for i in range(0,9):
			for j in range(0,9):
				# If this square has multiple possible values, pick one to try at random
				if len(test_board[i][j]) > 1:
					test_board[i][j] = [choice(test_board[i][j])]
		# See if the puzzle is solved; if not, try again
		if is_solved(test_board):
			return (test_board, iterations)
		else:
			iterations += 1
	# Give up
	show_board(test_board)
	return (board, iterations)

# This solver uses a backtracking method to solve puzzles
# The method chooses a random possible value for the first square with multiple options and proceeds to do this for all subsequent squares
# If it reaches a square with no valid values, it will go back and try another value for the previous square
# This process repeats until the puzzle is solved
def backtracking_solver(board):
	iterations = 0
	current_index = 0
	attempts = {}
	unsolved_squares = []
	temporary_board = deepcopy(board)
	# Make a list of all unsolved squares
	for i in range(0,9):
		for j in range(0,9):
			if len(board[i][j]) > 1:
				unsolved_squares.append((i,j))
				attempts[(i,j)] = 0
	current_square = unsolved_squares[0]
	# Iterate over the unsolved squares until we get to an impossible square
	while current_square != unsolved_squares[-1] or not is_solved(temporary_board):
		current_square = unsolved_squares[current_index]
		row = current_square[0]
		col = current_square[1]
		print current_square, attempts[current_square]+1, '/', len(board[row][col])
		show_board(temporary_board)
		# If we've gone beyond the number of possibilities for this square, backtrack
		if attempts[current_square] >= len(board[row][col]):
			temporary_board[row][col] = board[row][col]
			attempts[current_square] = 0
			current_index -= 1
		else:
			# Try the next possible value for that square
			temporary_board[row][col] = [board[row][col][attempts[current_square]]]
			# If this value is valid, advance to the next square
			if check_value(temporary_board, row, col):
				attempts[current_square] += 1
				current_index += 1
			# If not, try the next possible value
			else:
				attempts[current_square] += 1
				# If there are no more possibilities, bo back to the previous square
				if attempts[current_square] >= len(board[row][col]):
					temporary_board[row][col] = board[row][col]
					attempts[current_square] = 0
					current_index -= 1
					attempts[unsolved_squares[current_index]] += 1
		iterations += 1
		#sleep(1)
	return (temporary_board,iterations)

# Load the puzzle from the given text file
board = load_puzzle('puzzles/hard.txt')
# Show the starting board
print 'Initial board state:'
show_board(board,True)
# Try to solve the puzzle using the naive method
print 'Solving puzzle...',
result = naive_solver(board)
board = result[0]
iterations = result[1]
# If the puzzle wasn't solved, try the backtracking method next
if not is_solved(board):
	print 'naive solver failed after', iterations, 'iterations.'
	print 'Trying backtracking solver...',
	result = backtracking_solver(board)
	board = result[0]
	iterations += result[1]
print 'done.'
# Show the final board state, whether we were able to solve the puzzle, and how long it took
print 'Final board state:'
show_board(board, True)
if is_solved(board):
	print 'Puzzle solved in', iterations, 'iterations.'
else:
	print 'Gave up solving after', iterations, 'iterations.'

