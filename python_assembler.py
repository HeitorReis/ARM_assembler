instructions = {
    'add': ['00', '0000'],
    'sub': ['00', '0001'],
    'mul': ['00', '0010'],
    'div': ['00', '0011'],
    'and': ['00', '0100'],
    'or_': ['00', '0101'],
    'xor': ['00', '0110'],
    'not': ['00', '0111'],
    'mov': ['00', '1000'],
    'br_': ['11', '0000'],
    'brl': ['11', '1000'],
    'lnk': ['11', '0100'],
    'llk': ['11', '1100'],  # Link and save current position
    'lod': ['01', '0001'],
    'str': ['01', '0000'],
    'teq': ['00', '0001'],
    'cmp': ['00', '0001']
}

condition_setting = {
    'do': '0000',
    'eq': '0001',
    'neq': '0010',
    'gt': '0011',
    'gteq': '0100',
    'lt': '0101',
    'lteq': '0110'
}

support_bits = {
    'i': '10',
    's': '01',
    'is': '11',
    'si': '11'
}

class Instruction:

    machine_code: str
    assembly_line: str
    response: str

    def __init__(self, assembly_single_line: str):
        self.assembly_line = assembly_single_line
        self.response = self.decode_assembly()

    def decode_assembly(self):
        instruction_parts = self.assembly_line.split(' ')
        
        if instruction_parts[0] not in condition_setting.keys():
            return print(f'-> Error: invalid condition ({instruction_parts[0]}).')
        
        for cond_index, cond_key in enumerate(condition_setting.keys()):
            if instruction_parts[0] in cond_key:
                self.machine_code = condition_setting[cond_key]
                break

        instr_aux1 = instruction_parts[1][0:3]
        if len(instruction_parts[1]) > 3:
            instr_aux2 = instruction_parts[1][3:]
        if instr_aux1 not in instructions.keys():
            return print(f'-> Error: invalid instruction ({instr_aux1}).')

        for instr_index, instr_key in enumerate(instructions.keys()):
            opCode = instructions[instr_key][1]
            if instr_aux1 in instr_key:
                self.machine_code += instructions[instr_key][0]
                break

        is_imm = False
        if len(instruction_parts[1]) > 3:
            for sup_index, sup_key in enumerate(support_bits.keys()):
                if sup_key is instr_aux2:
                    self.machine_code += support_bits[sup_key]
                    if 'i' in sup_key:
                        is_imm = True
                    break
            self.machine_code += '00'

        self.machine_code += opCode

        if 'b' in instruction_parts[1] and 'su' not in instruction_parts[1]:
            self.machine_code += format(int(instruction_parts[2]), '015b')

        else:
            self.machine_code += format(int(instruction_parts[2]), '05b')
            self.machine_code += format(int(instruction_parts[3]), '05b')

            if is_imm:
                self.machine_code += format(int(instruction_parts[4]), '010b')
            elif not (self.machine_code[4:5] == '00' and self.machine_code[8:11] == '1000'):
                self.machine_code += format(int(instruction_parts[4]), '05b')
                self.machine_code += str('00000')
            else:
                self.machine_code += str('0000000000')
        
        return '-> Success'


class FullCode(Instruction):

    assembly_list: list
    full_code: list
    full_code_in_txt: str = ''
    response: str

    def __init__(self, assembly_code_lines: list):
        self.full_code = []
        self.full_code_in_txt = ''
        self.assembly_list = assembly_code_lines
        self.response = self.decode_full_code()
    
    def decode_full_code(self):
        
        for row_index, row in enumerate(self.assembly_list):
            
            if row[-1:] == '\n':
                row = row[:-1]
            
            this_instr = Instruction(row)
            
            if this_instr.response == '-> Success':
                self.full_code.append(this_instr.machine_code)
                self.full_code_in_txt += str(this_instr.machine_code) + '\n'
            
            else:  
                return str(this_instr.response) + f' in line {row_index}'
            
        return 'Success'