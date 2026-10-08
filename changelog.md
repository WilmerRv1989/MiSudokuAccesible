## 1.0.0

First stable version, tested on NVDA 2026.2:

* Sudokus of 9 by 9 in three levels measured by the techniques they need, and mini sudokus of 4 by 4 and 6 by 6 for beginners and children, all generated on the spot with a single solution.
* Hints that teach (P and Shift+P), clash warnings and Check; or a challenge without help.
* Learn to play: a guided course of 13 lessons, from the rules to intersections and pairs, with endless practice of each technique. The course is in Spanish.
* Sudoku of the day with days in a row, My statistics, a settings panel in NVDA's options and a list of keyboard shortcuts.
* Automatic saving of the sudoku, the sudoku of the day and the course.

## 0.9.3

* The Spanish manual was rewritten from start to finish, ordered from the basics to the advanced, with a section about how this add-on was made.
* Fuller description in the add-on store, and an updated readme in English.

## 0.9.2

* Fixed a key press that could be lost on the board: NVDA asked the cell something it could not answer, and wrote an error in its log.

## 0.9.1

* Keyboard shortcuts, in Tools, MiSudokuAccesible, did nothing. It works now. From the menu of the board and of the lessons it already worked.
* Fixed an error that NVDA wrote in its log for every cell of the board while playing. It was not noticed, but filled the log.

## 0.9.0

* Settings panel in NVDA's options: say the position of the cells in the short form (R3C5), remove notes automatically when writing, announce complete rows, columns and blocks, play sounds, and delete your progress and statistics.
* Keyboard shortcuts: a new item in the menu of the board and of the lessons, and in Tools, MiSudokuAccesible. The keys are read from NVDA, so the list includes your changes in Input gestures. A new command, without a key by default, shows it from the board.
* The whole sudokus of lessons 11 to 13 are kept, with the hints you asked for, when you close the lesson; next time you continue where you left it.
* Continue the sudoku now appears right after New sudoku in the submenu.

## 0.8.1

* New Help option in the New sudoku dialog, remembered like size and level: with help off there are no hints and no clash warnings, for a bigger challenge. Check, reading rows, columns and blocks, notes and F5 still work. The window title says "without help".
* The sudoku of the day asks every day whether you want to play it with or without help.
* My statistics count separately the sudokus solved without help.

## 0.8.0

* Sudoku of the day, in Tools, MiSudokuAccesible: a new 9 by 9 sudoku every day, the same for everyone. Easy on Monday, Tuesday, Saturday and Sunday; medium on Wednesday and Thursday; hard on Friday. It has its own saved game and counts the days in a row you solve it.
* My statistics: sudokus solved by size and level with your best time, the days in a row of the sudoku of the day, and your progress in the course. Solving a sudoku faster than ever is announced.

## 0.7.0

* Learn to play is complete. Block C, Let's play: 11. Your first 4 by 4. 12. Your first 6 by 6. 13. Your first 9 by 9. Whole sudokus, solved from start to finish with the help of the course.
* In these whole sudokus, stars depend on how many hints you ask for: 3 with none or one, 2 with up to four, 1 with more.
* At the end of the course, a final message invites you to play New sudoku and to keep practicing.

## 0.6.1

* Intersections and pairs were confusing: the hint named the group with the reason, but the number went somewhere else. Now the exercises of lessons 9 and 10, and their practice, go in two steps on a board with notes: first remove the notes that are ruled out, in a named cell; then write the number that becomes clear. The explanations of both lessons were rewritten.
* Game hints with an intersection or a pair name both places: "You can write a number in the row 3, but first you need an intersection in the block 2". The full hint says first where the number goes, and then why.

## 0.6.0

* Learn to play, block B, The techniques: 4. Last number. 5. Only place in a block. 6. Only place in rows and columns. 7. Only number. 8. Notes as a help. 9. Intersection. 10. Pair. In 6 by 6 and 9 by 9.
* Technique exercises say where to look, not the cell: finding it is the exercise. Writing in another cell says "Not here" and repeats where to look.
* Practice: the lessons of block B have a Practice button (also in the menu of the board). Each round has 5 new exercises of that technique, generated on the spot; the list of lessons shows your best round.
* Hints in the game and in the lessons are shorter: when an intersection or a pair is needed, the explanation only includes the ones that are really needed.

## 0.5.0

* Learn to play, in Tools, MiSudokuAccesible: a guided course with lessons and exercises on the board, also designed for children. The lessons are in Spanish.
* Block A, Getting to know sudoku: 1. The rules. 2. Rows, columns and blocks. 3. Writing, deleting and notes. All in 4 by 4.
* In the lessons, a number that does not fit is not written: the add-on says why. F2 repeats the instruction and Shift+F2 the explanation. Each exercise gives 3 stars without hints, 2 with the short hint and 1 with the full hint. Progress is saved automatically.

## 0.4.0

* Mini sudokus for beginners and children: 4 by 4 (blocks of 2 by 2) and 6 by 6 (blocks of 2 rows by 3 columns). The New sudoku dialog now has a Size choice, and remembers it.
* Mini sudokus have two levels, Easy and Medium: they hardly ever need the harder techniques, so Medium only has fewer numbers placed.
* Pressing a number higher than the board says which numbers go in that sudoku.
* The window title says the size and the level.

## 0.3.0

* Hints that teach: P gives a short hint (where to look and what to look for) and Shift+P the full explanation (which number goes where, and why). Hints never write anything. If the board has a wrong number, the hint says where it is first.
* Hints use five techniques, from the easiest: last number, only place, only number, intersection and pair.
* Levels are now measured by the techniques each sudoku needs: Easy only needs the first three (and starts with at least 36 numbers), Medium needs an intersection and Hard needs a pair. Before, many hard sudokus only needed easy techniques, and some needed techniques the hints do not know yet.
* New sudokus are prepared without stopping NVDA; a medium or hard one can take a couple of seconds.

## 0.2.1

* Check and Restart, in the menu of the board, said nothing: their result was cut off when NVDA announced the window and the cell again. Now it is said right after the cell.

## 0.2.0

* Playable sudoku. Tools, MiSudokuAccesible, New sudoku asks for the level (Easy, Medium or Hard) and generates a puzzle with a single solution.
* Write numbers with 1 to 9, notes with Shift+1 to 9, delete with Delete or Backspace, undo with Control+Z. Writing a number removes that note from its row, column and block.
* Cells say their number, "fixed" for the numbers of the puzzle, and their notes. F, C and B read the row, column or block: which numbers it has and which are missing. Tab and Shift+Tab move to the next or previous empty cell, and F5 says how many are left.
* A tone warns when a number clashes with another one in its row, column or block. A short sound and a message celebrate every complete row, column or block, and a melody and the time the solved sudoku.
* Menu of the board: New sudoku, Check (how many cells are wrong, without saying which), Restart and Close the board.
* Every change is saved. Escape closes the board without losing anything; Continue the sudoku, in the Tools submenu, opens it again.

## 0.1.0

* First test version: an empty 9 by 9 board in Tools, MiSudokuAccesible, New sudoku. It can be explored with the arrows, Home and End; NVDA says the row, the column and, when moving into another block, the block number. Escape closes the board.
