// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// set temp = 0
  @temp
  M=0
// set count = 0
  @count
  M=0

// (LOOP) start
(LOOP)
// if count == R1 => if (R1 - count) = 0; JUMP TO END
  @R1
  D=M // D = REM[R1]
  @count
  D=D-M // D = REM[R1] - count
  @ASSIGN
  D;JEQ

// temp = temp + R0
  @R0
  D=M // D = REM[R0]
  @temp
  M=M+D // RAM[temp] = RAM[temp] + RAM[R0]
// count++
  @count
  M=M+1
// go back to loop
  @LOOP
  0;JMP

// assign final result to R2
(ASSIGN)
  @temp
  D=M
  @R2
  M=D
  @END
  0;JMP

//END loop
(END)
  @END
  0;JMP