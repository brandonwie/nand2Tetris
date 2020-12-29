// Use with CPUEmulator.sh in ../tools/
// execute "chmod +x CPUEmulator.sh" in the folder to open it

// Program: Sum1toN.asm
// Computers RAM[1] = 1 + 2 + ... + n
// Usage: put a number (n) in RAM[0]

	@R0
	D=M // D = RAM[0]
	@n
	M=D // n = RAM[0]
	@i
	M=1 // i = 1
	@sum
	M=0 // sum = 0

(LOOP)
	@i
	D=M // D = i
	@n
	D=D-M // D = i - n
	@STOP
	D;JGT // if i - n > 0 (if i > n)  goto STOP

	@sum
	D=M // D = sum
	@i
	D=D+M // D = sum + i
	@sum
	M=D // sum = sum + i
	@i
	M=M+1 // i = i + 1
	@LOOP
	0;JMP

(STOP)
	@sum
	D=M // D = sum
	@R1
	M=D // RAM[1] = sum

(END)
	@END
	0;JMP