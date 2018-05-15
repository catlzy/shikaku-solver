from __future__ import print_function  # no more Python2 vs Python3 print issue!
import sys
import glob
import time
from rect import rectGet, rectSet, rectTest, rectValid, rectTest2
from math import sqrt

# These variables should be set during readPuzzle and then never modified.
global rows    # number of rows in the current puzzle
global cols    # number of columns in the current puzzle
global puzzle  # puzzle[row][col] is initial value in (row, col) with -1 for '-'
global anchors # anchors[i] gives the ith anchor as a triple (row, col, value)
global finishTime # the backtracking program must end at this time

# Use this variable to store the current state of the puzzle.
#  - state[row][col] = i means position (row, col) is covered by anchor i's rectangle.
#  - state[row][col] = -1 means position (row, col) is not covered by a rectangle.
global state
global anchors_factor # a list of all factors of each anchor (a list of lists)
global count # keeps track of which factor to start making rectangles with
global lastCells # has len(anchors), each element is a list of cells that must be
                 # covered by the end of this recursion

# Read a puzzle stored in a given file name.
# When this function is completed the puzzle variable will store the puzzle
# as a list of lists, and anchors will be stored as a list of triples.
def readPuzzle(inputFilename):
    global rows, cols, puzzle, anchors
    anchors = []
    with open(inputFilename, "r") as inputFile:
        rows = int(inputFile.readline())
        cols = int(inputFile.readline())
        puzzle = [cols * [""] for i in range(rows)]
        for row, line in enumerate(inputFile):
            for col, symbol in enumerate(line.split()):
                if symbol == "-":
                    puzzle[row][col] = -1
                else:
                    puzzle[row][col] = int(symbol)
                    anchors.append((row, col, int(symbol)))

# Verify that the current state is a solution to the current puzzle.
def verifySolution():
    global rows, cols, puzzle, anchors, state

    # Verify the following things about each anchor i which is in position (row,col) and has value val.
    #  (1) solution[row][col] should equal i due to the chosen solution format.
    #  (2) the number of i's in solution should equal val.
    #  (3) the i's in solution should form a rectangle.
    for i, (row, col, val) in enumerate(anchors):

        # Verify (1).
        if state[row][col] != i:
            print("error: state[%d][%d] != %d" % (row,col,i), file=sys.stderr)
            return False

        # Get all positions where solution is equal to i.
        wherei = [(r,c) for r in range(rows) for c in range(cols) if state[r][c] == i]
        numi = len(wherei)

        # Verify (2).
        if numi != val:
            print("error: state should contain %d copies of %d" % (val,i), file=sys.stderr)
            return False

        # Verify (3).
        left   = min(wherei, key=lambda x: x[0])[0]
        right  = max(wherei, key=lambda x: x[0])[0]
        top    = min(wherei, key=lambda x: x[1])[1]
        bottom = max(wherei, key=lambda x: x[1])[1]
        area = (right-left+1) * (bottom-top+1)
        if area != numi:
            print("error: the %d's in state form a rectangle" % i, file=sys.stderr)
            return False

    return True

def printGrid(grid):
    for row in grid:
        for symbol in row:
            print(str(symbol).rjust(4), end='')
        print("")

# find all factors of each anchor, update the anchors_factor list
def factors():
    global anchors, anchors_factor
    for anchor in anchors:
        value = anchor[2]
        current = []
        bound = round(sqrt(value))+1
        for i in range(1,int(bound)):
            if value%i == 0:
                if i == value//i:
                    current.append(i)
                else:
                    current.append(i)
                    current.append(value//i)
        anchors_factor.append(current)
    return


def backtrack(nexti):
    global rows, cols, puzzle, anchors, state, count, anchors_factor, lastCells
    global finishTime

    # Check if we have run out of time.
    if time.time() > finishTime: return

    # stop backtracking when it has looped through all the anchors,
    # which means a solution is found
    if nexti > len(anchors)-1: return True

    # set row, column, and value of the current anchor
    irow = anchors[nexti][0]
    icol = anchors[nexti][1]
    ivalue = anchors[nexti][2]

    # while the counter for the current nexti hasn't reached the end of the factor
    # list for the current nexti
    while count[nexti] < len(anchors_factor[nexti]):
        # a list of all the factors of the value of current nexti
        faclist = anchors_factor[nexti]
        # the current factor being processed
        fac = faclist[count[nexti]]
        # loop through all the valid rectangles of size fac by ivalue/fac
        for i in range(ivalue/fac):
            for j in range(fac):
                # if the rectangle in the current position is vaild and it only has values -1 and
                # the index of the current anchor, set values in that rectangle to the index of the
                # current anchor, and then call recursion to the next anchor
                if rectValid(state, irow-j, irow+fac-1-j, icol+i-ivalue/fac+1, icol+i):
                    if rectTest2(state, irow-j, irow+fac-1-j, icol+i-ivalue/fac+1, icol+i, -1, nexti):
                        rectSet(state, irow-j, irow+fac-1-j, icol+i-ivalue/fac+1, icol+i, nexti)
                        # if the any cells that will be last covered by this anchor is not covered,
                        # do not backtrack and move on to the next valid rectangle.
                        notCover = False
                        for z in range(len(lastCells[nexti])):
                            r = lastCells[nexti][z][0]
                            c = lastCells[nexti][z][1]
                            if state[r][c] == -1:
                                notCover = True
                                break
                        if notCover == False:
                            # if the recursion returns True, which means a solution is found,
                            # keep returning true until the very first level of recursion
                            if backtrack(nexti+1) == True:
                                return True
                        # if recursion doesn't return True or some last cells are not covered,
                        # set the values in that rectangle back to -1
                        rectSet(state, irow-j, irow+fac-1-j, icol+i-ivalue/fac+1, icol+i, -1)
                        # assign anchor value to its position
                        state[anchors[nexti][0]][anchors[nexti][1]] = nexti
        # increase counter by 1, so go to the next factor in the list
        count[nexti] += 1

    # if no valid rectangles are found, set counter for the current anchor back to 0
    if nexti > 0:
        count[nexti] = 0


def initialization():
    global state, anchors_factor, count, rows, cols, lastCells
    #create the factor list for all the anchors
    anchors_factor = []
    factors()

    #create the global counter for the factors
    count = [0]*len(anchors)

    #create initial state with all -1 and add the index of the anchors to their positions
    state = [[-1 for c in range(cols)] for r in range(rows)]
    for i in range(len(anchors)):
        state[anchors[i][0]][anchors[i][1]] = i

    # for each anchor, go through its possible rectangles and constantly reassign values
    # in the rectangles so that the values in each cell is the last anchor it can be covered
    for z in range(len(anchors)):
        irow = anchors[z][0]
        icol = anchors[z][1]
        ivalue = anchors[z][2]
        faclist = anchors_factor[z]
        for fac in faclist:
            for i in range(ivalue/fac):
                for j in range(fac):
                    if rectValid(state, irow-j, irow+fac-1-j, icol+i-ivalue/fac+1, icol+i):
                        rectSet(state, irow-j, irow+fac-1-j, icol+i-ivalue/fac+1, icol+i, z)

    # create the lastCells list
    lastCells = [[]for i in range(len(anchors))]
    for row in range(rows):
        for col in range(cols):
            value = state[row][col]
            lastCells[value].append([row, col])

    # reassign the state to original values
    state = [[-1 for c in range(cols)] for r in range(rows)]
    for i in range(len(anchors)):
        state[anchors[i][0]][anchors[i][1]] = i


if __name__ == "__main__":
    global finishTime
    totalSolved = 0
    totalUnsolved = 0
    fileNames = sorted(glob.glob("puzzles/*.txt"))
    for fileName in fileNames:
        readPuzzle(fileName)
        print(fileName)
        startTime = time.time()
        finishTime = startTime + 100
        initialization()
        backtrack(0)
        printGrid(state)
        endTime = time.time()
        if verifySolution():
            print("solved")
            totalSolved += 1
        else:
            print("not solved")
            totalUnsolved += 1
        print(endTime - startTime)
        print("")
    print("total solved: %d" % totalSolved)
    print("total unsolved: %d" % totalUnsolved)
