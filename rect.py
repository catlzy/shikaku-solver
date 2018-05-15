'''
This file has functions for accessing rectangular regions of lists of lists.
[It would be more efficient (but less portable) to use numpy for this purpose.]

In each function the parameter L is the list of lists and the rectangular region
is defined by the following 0-based indices:
 - r1 is the index of the top row of the rectangular region;
 - r2 is the index of the bottom row of the rectangular region;
 - c1 is the index of the left column of the rectangular region;
 - c2 is the index of the right column of the rectangular region.

It is assumed that the list of lists is non-empty and that all lists in the
list of lists have the same length.  These assumptions are never checked.
'''

# Returns True if the r1, r2, c1, c2 values define a valid non-empty rectangle.
def rectValid(L, r1, r2, c1, c2):
    numRows = len(L)
    numCols = len(L[0])
    if (r1 > r2 or c1 > c2): return False
    if (r1 < 0 or c1 < 0): return False
    if (r2 >= numRows or c2 >= numCols): return False
    return True

# Return a list of lists defined by the rectangular region.
def rectGet(L, r1, r2, c1, c2):
    assert(r1 <= r2)
    assert(c1 <= c2)
    rect = [[L[r][c] for r in range(r1,r2+1)] for c in range(c1,c2+1)]
    return rect

# Set all of the values in the rectangular region to the same vaule.
def rectSet(L, r1, r2, c1, c2, value):
    assert(r1 <= r2)
    assert(c1 <= c2)
    for r in range(r1,r2+1):
        for c in range(c1,c2+1):
            L[r][c] = value

# Return True if all of the values in the rectangular region equal the value.
def rectTest(L, r1, r2, c1, c2, value):
    assert(r1 <= r2)
    assert(c1 <= c2)
    for r in range(r1,r2+1):
        for c in range(c1,c2+1):
            if L[r][c] != value:
                return False
    return True

# Return True if all of the values in the rectangular region equal either of the two values
def rectTest2(L, r1, r2, c1, c2, value, value2):
    assert(r1 <= r2)
    assert(c1 <= c2)
    for r in range(r1,r2+1):
        for c in range(c1,c2+1):
            if L[r][c] != value and L[r][c] != value2:
                return False
    return True
