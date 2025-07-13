# assembler_main.py
import python_assembler as assembler

with open('D:/LocalVSCodes/ARM_assembler/main.txt', 'r') as assembly_file:
    assembly_lines = assembly_file.readlines()

machine_code = assembler.FullCode(assembly_lines)

if 'Error' not in machine_code.response:
    # Escreve o código de máquina puro no ficheiro de saída
    with open('D:/LocalVSCodes/ARM_assembler/machine_code.txt', 'w') as machine_code_file:
        machine_code_file.write(machine_code.full_code)
    
    # Imprime a versão de depuração detalhada no terminal
    print("--- DEBUG OUTPUT ---")
    print(machine_code.debug_output)
    print("\nMachine code successfully generated.")
else:
    # Imprime a mensagem de erro detalhada
    print(f"Assembly failed: {machine_code.response}")