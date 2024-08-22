import python_assembler as assembler

with open('D:/LocalVSCodes/AOC_Assembler/ARM_assembler/main.txt', 'r') as assembly_file:
    assembly_lines = assembly_file.readlines()

machine_code = assembler.FullCode(assembly_lines)

if 'Error' not in machine_code.response:
    with open('D:/LocalVSCodes/AOC_Assembler/ARM_assembler/machine_code.txt', 'w') as machine_code_file:
        machine_code_file.write(machine_code.full_code)