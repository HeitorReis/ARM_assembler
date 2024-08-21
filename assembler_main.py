import python_assembler as assembler

with open('main.txt', 'r') as assembly_file:
    assembly_lines = assembly_file.readlines()[:]

machine_code = assembler.FullCode(assembly_lines)

with open('machine_code.txt', 'w') as machine_code_file:
    machine_code_file.write(machine_code.full_code_in_txt)

print(machine_code.response)