// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed.
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(MAIN_LOOP)
  @SCREEN  // set screen
  D=A
  @address
  M=D // RAM[address] = 16384

  @counter  // set counter
  M=0 // REM[counter] = 0
  // set max pixel value
  @8192
  D=A
  @maxpixel
  M=D

  @color // set color to white
  M=0

  @KBD  // set keyboard input
  D=M
  @COLOR_SCREEN
  D;JEQ // if REM[keyboard] = 0 goto COLOR_SCREEN

  @color // set color to black otherwise
  M=-1

(COLOR_SCREEN)
	@maxpixel	// if (counter == maxpixel) goto MAIN_LOOP
  D=M
 	@counter
	D=D-M
	@MAIN_LOOP
  D;JEQ

  // start coloring...
  @color
  D=M // D = REM[color]
  @address
  A=M   // Pointer: **Typical pointer semantics: "set the address register to the contents of some memory register"
  M=D		// RAM[address] = value of REM[color]

  @counter
  M=M+1	// counter++
  @address
  M=M+1	// screen address++
  @COLOR_SCREEN //go back to the loop
  0;JMP