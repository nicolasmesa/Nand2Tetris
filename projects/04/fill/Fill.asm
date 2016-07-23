// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

// Put your code here.

@black
M = -1

@white
M = 0

@color
M = 0

@8192
D = A

@maxscreen
M = D

(OLOOP)
@KBD
D = M

@SETBLACK
D; JNE

@white
D = M

@color
M = D

@ENDSETBLACK
0; JMP

(SETBLACK)
@black
D = M

@color
M = D

(ENDSETBLACK)

@i
M = 0
(ILOOP)

@i
D = M

@maxscreen
D = D - M

@ENDILOOP
D; JEQ

@SCREEN
D = A

@i
D = D + M

@addr
M = D

@color
D = M

@addr
A = M

M = D

@i
M = M + 1

@ILOOP
0; JMP

(ENDILOOP)


@OLOOP
0; JMP


(END)
@END
0; JMP
