// Use with CPUEmulator.sh in ../tools/
// execute "chmod +x CPUEmulator.sh" in the folder to open it

// Adds up two numbers
// RAM[2] = RAM[0] + RAM[1]
// Usage: put the values that you wish to add
// 		  in RAM[0] and RAM[1]

	@0
	D=M

	@1
	D=D+M

	@2
	M=D
