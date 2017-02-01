import numpy as np

#This is a Sudoku solver that works for most puzzles, but it can't yet break
#the toughest. It uses simple recursion to execute a two-step cycle which repeats
#again and again until the grid is full:

#Step 1) Enumerate all the possible numbers that could fit into each empty
#cell, based on the information known (i.e., the numbers in all the other
#cells) at that point.
#Step 2) Use these possibilities (called "Options") to scan each cell and deduce
#a solution for that cell, if possible.

#Each step in the cycle is applied to all the cells in the grid before the next
#step starts. It may seem like a waste of time to move on from one cell to the
#next (in step 1) without immediately checking it for a solution, but keep in
#mind that even more solutions will emerge once the entire grid has been checked
#for options, so that all these solutions can be implemented at once, ready for
#the next round of option-checking.

#In the Option-checking step (Grid.GetAllOptions), there's a thing called
#HandleGhostNumbers. It was the toughest part to write, and it's still messy,
#with awkward variables and an inefficient algorithm. I was hoping this part
#would make it much more powerful, and while I have seen it solve some cells
#correctly where the rest of the program fails, it still can't crack the
#hardest puzzles, or even significantly speed up the solution for moderate puzzles.
#But it shouldn't give any incorrect solutions. See that section to learn more
#about what it actually does.

#Some methods relating to an individual cell appear under the Grid class, rather
#than here, because they need to refer to other cells in the grid.
class Cell(object):
    def __init__(self, Row, Col, Number, Options, Eliminations):
        self.Row = Row
        self.Col = Col
        self.Number = Number
        self.Options = Options
        self.Eliminations = Eliminations

    #Returns the coordinates of all 9 cells in the local 3x3 block
    def BlockCoords(self):
        BRows = []
        BCols = []
        BlockCoords = []
        if 0 <= self.Row <= 2:
            BRows = [0,1,2]
        elif 3 <= self.Row <= 5:
            BRows = [3,4,5]
        else:
            BRows = [6,7,8]
        if 0 <= self.Col <= 2:
            BCols = [0,1,2]
        elif 3 <= self.Col <= 5:
            BCols = [3,4,5]
        else:
            BCols = [6,7,8]
        for r in BRows:
            for c in BCols:
                BlockCoords.append([r,c])
        return BlockCoords
    
    #Returns True if the cell has already been filled with a number
    def IsCellFull(self):
        if self.Number == " ":
            return False
        else:
            return True

#A Grid is a NumPy array of Cells (with dtype = Cell)
class Grid(object):
    def __init__(self, Cells):
        self.Cells = Cells
    
    #A method that refreshes the Options list for each Cell. Note that
    #HandleGhostNumbers appears here, and so would a lot of other methods
    #if I had the audacity to try and code for more solution techniques.
    #I don't, and I have a lot of audacity.
    def GetAllOptions(self):
        self.HandleGhostNumbers()
        for r in range(9):
            for c in range(9):
                self.Cells[r,c].Options = self.GetCellOptions(self.Cells[r,c])
    
    #A method that fills each Cell with a number, if possible.
    #(See FillCellNumber, which processes the individual Cell.)
    def FillAllNumbers(self):
        for r in range(9):
            for c in range(9):
                self.Cells[r,c].Number = self.FillCellNumber(self.Cells[r,c])
    
    #This function takes a single cell and shortens its Options string based
    #on the Numbers in the grid (whether they were there from the beginning or
    #were logically deduced and implemented in FillAllNumbers).
    def GetCellOptions(self, TheCell):
        self.TheCell = TheCell
        TheCell.Eliminations = ""
        if not TheCell.IsCellFull():
            #Enumerate invalid options by checking columns, rows, and blocks
            for r in range(9):
                TheCell.Eliminations += self.Cells[r,TheCell.Col].Number
            for c in range(9):
                TheCell.Eliminations += self.Cells[TheCell.Row,c].Number
            BC = TheCell.BlockCoords()
            for b in range(9):
                TheCell.Eliminations += self.Cells[BC[b][0],BC[b][1]].Number
            #Trim out the spaces (the Number value for an empty cell is " ")
            TheCell.Eliminations = TheCell.Eliminations.replace(" ","")

            #Makes sure that none of the eliminations appear in the options.
            for x in range(len(TheCell.Options)):
                if TheCell.Options[x] in TheCell.Eliminations:
                    TheCell.Options = TheCell.Options.replace(TheCell.Options[x]," ")
            #Trim out the spaces
            TheCell.Options = TheCell.Options.replace(" ","")
        else:
            TheCell.Options = ""
        return TheCell.Options
    
    #This is really clunky. And even after writing it, I realized that there's
    #an even more general way to state the rule, not to mention design the
    #algorithm or write the code. But I'll write down exactly what this code
    #does, as it is now:
    
    #I made up the term "ghost numbers." Imagine you have a 3x3 block, and you're
    #looking at the options for number 7. Turns out that 7 appears twice in the
    #options for the top row in that block, but zero times in the rest of the
    #block. Since there are two possibilities for where to put it, you can't
    #necessarily commit to either one of them (spooooky!!). What you DO know is
    #that, either way, there WILL be a 7 in the top row of that block. Which
    #means that if you look at the rest of the row, outside that block, you can
    #eliminate 7 from all options lists in which it would have appeared.
    
    #This method takes each 3x3 block and runs it through 6 main processes. The
    #first three check the three intersections between a row and that block (so
    #three horizontal rows of three cells each). For each of these three "mini-
    #rows," it checks to see if any options in those cells (RowInBlockOpts) also
    #appear elsewhere in the block (OtherRowsInBlockOpts). If a certain number
    #does not, and if the number in question hasn't after all been assigned as
    #the solution anywhere in the block, then it goes ahead and eliminates that
    #option from the rest of its row OUTSIDE the block, like in my ghost story
    #above. The next 3 main processes (I said there were 6, remember?) do
    #exactly the same thing except vertically, with the columns.
    def HandleGhostNumbers(self):
        for rBlockCorner in [0,3,6]:
            for cBlockCorner in [0,3,6]:
                r = 0
                rOtherBlocks = [0,3,6]
                rOtherBlocks.remove(rBlockCorner)
                CellsInRowOutsideBlock = []
                
                c = 0
                cOtherBlocks = [0,3,6]
                cOtherBlocks.remove(cBlockCorner)
                CellsInColOutsideBlock = []
                for rLocal in range(3):
                    r = rLocal + rBlockCorner
                    CellsInRowOutsideBlock = []
                    RowInBlockOpts = ""
                    OtherRowsInBlockOpts = ""
                    NumsInBlock = ""
                    for cLocal in range(3):
                        c = cLocal + cBlockCorner
                        RowInBlockOpts += self.Cells[r,c].Options
                        OtherRowsInBlockOpts += self.Cells[rBlockCorner+((rLocal+1)%3),c].Options
                        OtherRowsInBlockOpts += self.Cells[rBlockCorner+((rLocal+2)%3),c].Options
                        NumsInBlock += self.Cells[rBlockCorner+(rLocal%3),c].Number
                        NumsInBlock += self.Cells[rBlockCorner+((rLocal+1))%3,c].Number
                        NumsInBlock += self.Cells[rBlockCorner+((rLocal+2))%3,c].Number
                        CellsInRowOutsideBlock.append(self.Cells[r,cOtherBlocks[0]+cLocal])
                        CellsInRowOutsideBlock.append(self.Cells[r,cOtherBlocks[1]+cLocal])
                    for o in RowInBlockOpts:
                        if (not o in OtherRowsInBlockOpts and not o in NumsInBlock):
                            for TheCell in CellsInRowOutsideBlock:
                                TheCell.Options = TheCell.Options.replace(o,"")
                                self.Cells[TheCell.Row,TheCell.Col] = TheCell
                                
                for cLocal in range(3):
                    c = cLocal + cBlockCorner
                    CellsInColOutsideBlock = []
                    ColInBlockOpts = ""
                    OtherColsInBlockOpts = ""
                    NumsInBlock = ""
                    for rLocal in range(3):
                        r = rLocal + rBlockCorner
                        ColInBlockOpts += self.Cells[r,c].Options
                        OtherColsInBlockOpts += self.Cells[r,cBlockCorner+((cLocal+1)%3)].Options
                        OtherColsInBlockOpts += self.Cells[r,cBlockCorner+((cLocal+2)%3)].Options
                        NumsInBlock += self.Cells[r,cBlockCorner+(cLocal%3)].Number
                        NumsInBlock += self.Cells[r,cBlockCorner+((cLocal+1)%3)].Number
                        NumsInBlock += self.Cells[r,cBlockCorner+((cLocal+2)%3)].Number
                        CellsInColOutsideBlock.append(self.Cells[rOtherBlocks[0]+rLocal,c])
                        CellsInColOutsideBlock.append(self.Cells[rOtherBlocks[1]+rLocal,c])
                    for o in ColInBlockOpts:
                        if (not o in OtherColsInBlockOpts and not o in NumsInBlock):
                            for TheCell in CellsInColOutsideBlock:
                                TheCell.Options = TheCell.Options.replace(o,"")
                                self.Cells[TheCell.Row,TheCell.Col] = TheCell
    
    #This is the function that takes the Options string for each Cell and
    #deduces what number (if any) can fill that Cell. The first part is
    #simple: if a Cell is left with only one Option, then that Option becomes
    #the Cell's Number. But the second part goes further. There could be a case
    #in which a cell has more than one Option listed (i.e., 3, 5, and 6), but
    #one of these (say, 3) doesn't appear anywhere else in that Cell's column,
    #or row, or block (considered separately). Then, we would fill the cell with 3.
    def FillCellNumber(self, TheCell):
        self.TheCell = TheCell
        #If there is only one option left in the cell, that MUST be the answer.
        if len(TheCell.Options) == 1:
            TheCell.Number = TheCell.Options
        else:
            #EVEN IF THE CELL HAS MULTIPLE OPTIONS, one of these options might
            #be unique in the row, or column, or block. That option is the answer.
            OtherCellsInCol = []
            OtherCellsInRow = []
            OtherCellsInBlock = []
            #These commands assemble a list of the other cells in the current
            #cell's column, row, and block, respectively, without including the
            #current cell.
            for r in range(9):
                OtherCellsInCol.append(self.Cells[r,TheCell.Col])
            OtherCellsInCol.remove(TheCell)
            for c in range(9):
                OtherCellsInRow.append(self.Cells[TheCell.Row,c])
            OtherCellsInRow.remove(TheCell)
            BC = TheCell.BlockCoords()
            for b in range(9):
                OtherCellsInBlock.append(self.Cells[BC[b][0],BC[b][1]])
            OtherCellsInBlock.remove(TheCell)
            #Now we check whether the Cell has an option which also features
            #in the options of the other groups (i.e., the column, row, or block),
            #one group at a time. First we have to concatenate all the options
            #for each group, separately, so we're comparing strings to strings.
            StringOtherOptionsInCol = ""
            StringOtherOptionsInRow = ""
            StringOtherOptionsInBlock = ""
            for r in range(8):
                StringOtherOptionsInCol += OtherCellsInCol[r].Options
            for c in range(8):
                StringOtherOptionsInRow += OtherCellsInRow[c].Options
            for b in range(8):
                StringOtherOptionsInBlock += OtherCellsInBlock[b].Options
            
            #If an option is unique to the cell (as compared separately with the
            #rest of its column, row, and block), then it must be the answer.
            for i in range(len(TheCell.Options)):
                if not TheCell.Options[i] in StringOtherOptionsInCol:
                    TheCell.Number = TheCell.Options[i]
                if not TheCell.Options[i] in StringOtherOptionsInRow:
                    TheCell.Number = TheCell.Options[i]
                if not TheCell.Options[i] in StringOtherOptionsInBlock:
                    TheCell.Number = TheCell.Options[i]
        return TheCell.Number
    
    #Checks to see if all the Cells are full; if so, returns True.
    def IsGridFull(self):
        FullCells = 0
        for r in range(9):
            for c in range(9):
                if self.Cells[r,c].IsCellFull():
                    FullCells += 1
        return FullCells == 81
            
#This is where you make a pretty user interface where you can input puzzles
#with just a few clicks. Obviously, I haven't done this...for now, make a 
#NumPy array like the examples listed and comment it out if you're not currently
#using it. DOUBLE-CHECK to make sure you entered the numbers right!!! If you
#entered the numbers row by row, check them column by column, and vice versa.
def FirstGridInput():
    #A puzzle marked "evil"
    """SampleSet = np.array([("7"," "," "," "," ","6","8"," ","2"),
                          (" ","2"," "," "," "," "," "," ","4"),
                          (" "," ","6"," ","9"," "," "," "," "),
                          (" "," "," ","9"," ","7","5"," "," "),
                          (" ","6"," "," "," "," "," ","8"," "),
                          (" "," ","4","3"," ","5"," "," "," "),
                          (" "," "," "," ","5"," ","4"," "," "),
                          ("8"," "," "," "," "," "," ","3"," "),
                          ("9"," ","2","7"," "," "," "," ","5")])"""
    
    #Another puzzle marked "evil"
    """SampleSet = np.array([("8","5","6","2"," "," "," "," "," "),
                          (" ","1"," "," "," ","3"," "," "," "),
                          (" ","7","2"," "," ","1"," "," "," "),
                          (" ","8"," "," ","9"," ","7"," "," "),
                          (" "," ","7"," "," "," ","4"," "," "),
                          (" "," ","5"," ","3"," "," ","9"," "),
                          (" "," "," ","6"," "," ","5","7"," "),
                          (" "," "," ","1"," "," "," ","8"," "),
                          (" "," "," "," "," ","9","1","6","2")])"""
                          
    #Evil again...
    """SampleSet = np.array([(" "," ","3"," "," ","5"," "," "," "),
                          ("1"," "," ","4"," ","7"," "," "," "),
                          (" "," "," "," ","1"," ","2","6"," "),
                          (" "," "," "," "," "," "," ","4","9"),
                          ("6","5"," "," ","7"," "," ","1","3"),
                          ("7","8"," "," "," "," "," "," "," "),
                          (" ","4","7"," ","3"," "," "," "," "),
                          (" "," "," ","6"," ","2"," "," ","4"),
                          (" "," "," ","7"," "," ","3"," "," ")])"""
                          
    #And again...
    """SampleSet = np.array([("1"," ","4"," "," "," "," "," "," "),
                          (" ","2","7"," "," ","4"," ","9","8"),
                          (" "," "," ","7"," "," "," "," ","5"),
                          (" "," "," ","9"," "," ","2"," "," "),
                          (" "," ","6","3"," ","2","8"," "," "),
                          (" "," ","3"," "," ","7"," "," "," "),
                          ("7"," "," "," "," ","3"," "," "," "),
                          ("9","8"," ","4"," "," ","5","3"," "),
                          (" "," "," "," "," "," ","4"," ","1")])"""
                          
    #One marked "expert" from a different website
    """SampleSet = np.array([(" "," "," "," ","3"," "," "," "," "),
                          (" "," ","1"," "," "," ","9"," ","8"),
                          (" "," "," "," "," "," "," "," "," "),
                          (" "," "," "," "," ","4"," ","7"," "),
                          ("6"," "," ","1","5","2"," "," ","3"),
                          (" ","1"," ","7"," "," "," "," "," "),
                          (" "," "," "," "," "," "," "," "," "),
                          ("2"," ","5"," "," "," ","4"," "," "),
                          (" "," "," "," ","9"," "," "," "," ")])"""
                          
    #A "hard" puzzle
    SampleSet = np.array([(" ","6"," ","9","3"," ","5"," "," "),
                          (" ","8"," "," "," "," ","2"," "," "),
                          (" "," ","9","8"," "," ","1"," ","6"),
                          ("8","7"," "," "," "," "," "," "," "),
                          (" "," ","2"," ","1"," ","7"," "," "),
                          (" "," "," "," "," "," "," ","6","2"),
                          ("3"," ","8"," "," ","6","9"," "," "),
                          (" "," ","1"," "," "," "," ","2"," "),
                          (" "," ","4"," ","2","5"," ","7"," ")])
    
    #A "medium" puzzle
    """SampleSet = np.array([(" ","7"," "," ","1"," ","3","5","6"),
                          (" "," ","6"," "," ","7"," ","8"," "),
                          (" ","8"," "," ","3"," "," ","9"," "),
                          (" "," ","1"," "," "," "," "," ","7"),
                          ("9"," "," "," ","6"," "," "," ","8"),
                          ("8"," "," "," "," "," ","5"," "," "),
                          (" ","6"," "," ","4"," "," ","1"," "),
                          (" ","4"," ","1"," "," ","8"," "," "),
                          ("7","1","8"," ","9"," "," ","2"," ")])"""
    
    #An "easy" puzzle   
    """SampleSet = np.array([("3","9","7"," ","4"," "," ","1"," "),
                          ("8","2"," "," "," "," ","5","3"," "),
                          (" ","4"," "," ","6","3","7"," ","9"),
                          (" "," ","2","1"," "," "," "," "," "),
                          (" "," ","9","3"," ","6","8"," "," "),
                          (" "," "," "," "," ","7","1"," "," "),
                          ("7"," ","5","6","3"," "," ","9"," "),
                          (" ","6","8"," "," "," "," ","7","1"),
                          (" ","3"," "," ","7"," ","2","5","6")])"""
    #Not much to see here; it takes the starting numbers and makes a Grid
    #out of them.
    NewCells = np.empty((9,9), dtype=Cell)
    for r in range(9):
        for c in range(9):
            NewCells[r,c] = Cell(r,c,SampleSet[r,c],"123456789","")
    NewGrid = Grid(NewCells)
    NewGrid.GetAllOptions()
    return NewGrid

#Basic recursion that 1) refreshes the options for all of the cells, then
#2) fills each cell (if possible) based on the currently known options. If
#the function hasn't reached its base case (Grid 100% solved), it keeps going,
#and going, and going, and going, and going....
def RecursiveSolve(GridNow):
    if GridNow.IsGridFull() == True:
        return GridNow
    else:
        GridNow.GetAllOptions()
        GridNow.FillAllNumbers()
        NewGrid = GridNow
        return RecursiveSolve(NewGrid)

#Puts the grid on display for the whole world to see. It's really presentable
#and easy to read right now...
def DisplayGrid(TheGrid):
    for r in range(9):
        ThisRow = ""
        for c in range(9):
            ThisRow += TheGrid.Cells[r,c].Number
        print(ThisRow)

#Where to start.
def main():
    MainGrid = FirstGridInput()
    DisplayGrid(MainGrid)
    print("---------")
    #If RecursiveSolve isn't doing it for you, go step-by-step with this "for"
    #loop and tell it how many steps you want it to do.
    """for x in range(20):
        MainGrid.GetAllOptions()
        MainGrid.FillAllNumbers()
        DisplayGrid(MainGrid)
        print("---------")"""
    MainGrid = RecursiveSolve(MainGrid)
    DisplayGrid(MainGrid)

if __name__ == "__main__":
    main()
