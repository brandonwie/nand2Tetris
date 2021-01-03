// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// concept: Add R0, R1 times and assign it to R2

// set counter
  @count
  M=0

// Loop until counter = R1
(LOOP)
  // if (R1 - count) = 0; JUMP TO END
  @R1
  D=M // D = REM[R1]
  @count
  D=D-M // D = D(R1) - count
  @END
  D;JEQ //

  // Add R0 to R2(accumulator)
  @R0
  D=M // D = REM[R0]
  @R2
  M=M+D // R2 = R2 + R0
  // count++
  @count
  M=M+1
  // Go back to loop
  @LOOP
  0;JMP

//END loop
(END)
  @END
  0;JMP