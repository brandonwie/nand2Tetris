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

(START)
  @SCREEN  // set screen
  D=A
  @address
  M=D // RAM[address] = 16384

  @counter  // set counter
  M=0 // REM[counter] = 0
  // set max pixel value
  @8192
  D=A
  @capacity // RAM[capacity] = 8192
  M=D

  @color // set color to white
  M=0

  @KBD  // set keyboard input
  D=M
  @COLOR_SCREEN
  D;JEQ // if REM[keyboard] = 0 start coloring with white
  // otherwise
  @color // set color to black and enter coloring
  M=-1

(COLOR_SCREEN)
	@capacity	// if (counter == capacity) goto START
  D=M
 	@counter
	D=D-M // D = capatity - counter
	@START
  D;JEQ // jump to START if screen is fully occupied

  // start coloring...
  @color
  D=M // D = RAM[color]
  // Pointer: **Typical pointer semantics: "set the address register to the contents of some memory register"
  @address
  A=M   // A(register) = RAM[address]
  M=D		// RAM[address] = value of REM[color]

  @counter
  M=M+1	// counter++
  @address
  M=M+1	// screen address++
  @COLOR_SCREEN // keep color screen
  0;JMP