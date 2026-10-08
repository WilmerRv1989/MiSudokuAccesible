# MiSudokuAccesible

*Accessible sudoku for NVDA, for all ages.*

Hi, I'm Wilmer. I have always wanted to play sudoku: it is a wonderful way to practice concentration and attention, a few minutes every day. But I never found a sudoku that felt truly comfortable with a screen reader, so I decided to make my own.

MiSudokuAccesible is the second game in my collection for NVDA, after [MiAjedrezAccesible](https://github.com/WilmerRv1989/MiAjedrezAccesible). I made it with two kinds of players in mind: anyone who wants a good sudoku with NVDA, and children who are just starting to learn. That is why it does not only let you play: it teaches you how to think through each move.

* Full manual, in Spanish: [addon/doc/es/readme.md](addon/doc/es/readme.md).
* Versión en español: [readme.md](readme.md).

## What you will find

* **Sudokus of 9 by 9** in three levels. Each level is measured by the techniques you need to solve it, not just by how many numbers are given, so "Hard" really means hard.
* **Mini sudokus of 4 by 4 and 6 by 6**, perfect for beginners and for children.
* **Hints that teach.** Press P and I will tell you where to look; press Shift+P and I will explain which number goes where, and why. Hints never write the number for you: finding it is the fun part.
* **Help on or off.** When you feel ready, play without hints or clash warnings, just like on paper.
* **Learn to play**, a guided course of 13 lessons: from the rules, to moving around the board, to intersections and pairs, with endless practice of each technique. For now, the course is in Spanish only.
* **The sudoku of the day**, the same for everyone, so you can build a habit and keep your days in a row.
* **My statistics**, a settings panel and a list of keyboard shortcuts.

Every cell can be read by speech and braille, and everything is saved automatically: close the board, or even NVDA, and continue later where you left off. The add-on works with NVDA 2026.1 and later, does not need the Internet and does not send any data.

## Where to start

Everything opens from the NVDA menu (NVDA+N), Tools, MiSudokuAccesible:

* If you have never played sudoku, start with **Learn to play**, from lesson 1. Take your time.
* If you already know how to play, choose **New sudoku** or try the **Sudoku of the day**.
* If you get stuck, press **P**. That is what hints are for.

## Keys on the board

| Key | Action |
|---|---|
| Arrows | Move between cells |
| Home / End | First or last cell of the row |
| Tab / Shift+Tab | Next or previous empty cell |
| 1 to 9 | Write that number |
| Shift+1 to 9 | Add or remove that number as a note |
| Delete or Backspace | Delete the number of the cell or, if it has none, its notes |
| Control+Z | Undo the last change |
| P | Short hint: where to look and what to look for |
| Shift+P | Full hint: which number goes where, and why |
| N | Read the notes of the cell |
| F / C / B | Read the row, column or block: which numbers it has and which are missing |
| F5 | How many empty cells are left |
| Applications or Shift+F10 | Menu of the board |
| Escape | Close the board (the sudoku is saved) |

Blocks are numbered from left to right and from top to bottom. You can change any key in NVDA's Input gestures, category MiSudokuAccesible.

## How I made it

I developed MiSudokuAccesible with the assistance of Claude, an AI model by Anthropic. Claude wrote most of the code following my instructions, looked into NVDA's documentation and code, and suggested technical solutions. The direction and the decisions were mine: the design of the add-on, the course and the way it teaches, the sounds, how it behaves with the screen reader, and what to leave out.

I tested and approved every version, feature, key and spoken message myself with NVDA. I tell you this because I believe it is the honest thing to do. If you find a bug, it is my responsibility, and you would help me a lot by letting me know.

## Get in touch

If something does not work, if you have an idea, or if you simply want to tell me how it went, write to me at contacto@wilmer-rv.com or open an [issue on GitHub](https://github.com/WilmerRv1989/MiSudokuAccesible/issues). I read everything.

Made with love by Wilmer Rodríguez Vega ([wilmer-rv.com](https://wilmer-rv.com)).

Licensed under the GNU General Public License, version 2 or later.
