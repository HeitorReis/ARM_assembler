# {instruction}_{support}_{condition}: r{rd_addr} = r{rh_addr}, (r{ro_addr} or {imm_value}) 
# {branch}_{condition}: {imm_value}

instructions = {
    # 3 variables
    'add': ['00', '0000'],
    'sub': ['00', '0001'],
    'mul': ['00', '0010'],
    'div': ['00', '0011'],
    'and': ['00', '0100'],
    'or':  ['00', '0101'],
    'xor': ['00', '0110'],
    'not': ['00', '0111'],
    'mov': ['00', '1000'],
    'teq': ['00', '0001'],
    'cmp': ['00', '0001'],
    
    # 2 variables
    'load': ['01', '0001'],
    'store': ['01', '0000'],
    
    # 1 variable
    'b': ['11', '0000'],
    'bl': ['11', '1000'],
    
    # 0 variable
    'l': ['11', '0100'],
    'll': ['11', '1100']  # Link and save current position
}

condition_setting = {
    'do':   '0000',
    'eq':   '0001',
    'neq':  '0010',
    'gt':   '0011',
    'gteq': '0100',
    'lt':   '0101',
    'lteq': '0110'
}

support_bits = {
    'i':    '10',
    's':    '01',
    'is':   '11',
    'si':   '11',
    'na':   '00'
}

class Instruction:

    binary32_line: str
    assembly_line: str
    
    condition: str
    opCode: str
    branchValue: str
    destinyRegister: str
    hitRegister: str
    immediateValue: str = 0
    operandRegister: str
    supportBits: str = 'na'
    
    disassembler_response: str = '-> Success'
    decoder_response: str = '-> Success'
    response: str = '-> Success'

    def __init__(self, assembly_single_line: str):
        
        self.disassembler_response = '-> Success'
        self.decoder_response = '-> Success'
        self.response = '-> Success'
        
        self.assembly_line = assembly_single_line
        self.disassembler_response = self.disassemble(self.assembly_line)
        if 'Error' in str(self.disassembler_response):
            self.response = self.disassembler_response
        else:
            self.decoder_response = self.decode_assembly(self.assembly_line)
            if 'Error' in self.decoder_response:
                self.response = self.decoder_response
    
    def decode_assembly(self, assembly_line: str) -> str:
        self.binary32_line = condition_setting[self.condition] # 4
        self.binary32_line += instructions[self.opCode][0] # 2
        self.binary32_line += support_bits[self.supportBits] # 2
        self.binary32_line += instructions[self.opCode][1] # 4, = 12
        
        if self.opCode == 'l' or  self.opCode == 'll':
            if self.supportBits != 'na':
                return '-> Error: Syntax (Link cannot use immediate or set CPSR flags)'
            self.binary32_line += format(0, '020b') # 20, = 32
            return '-> Success'
            
        if self.opCode == 'b' or self.opCode == 'bl':
            if 's' in self.supportBits:
                return '-> Error: Syntax (Branch cannot set CPSR flags)'
            self.binary32_line += format(0, '010b') # 10, = 22
            if 'i' in self.supportBits:
                self.binary32_line += self.getSignedBinary(self.immediateValue) # 10, = 32
                return '-> Success'
            else:
                self.binary32_line += format(int(self.operandRegister[1:]), '05b') # 5, = 27
                self.binary32_line += format(0, '05b') # 5, = 32
                return '-> Success'
        
        if 'r' not in self.destinyRegister:
            return '-> Error: Syntax (registers must have "r" before address value)'
        self.binary32_line += format(int(self.destinyRegister[1:]), '05b') # 5, = 17
        
        if self.opCode == 'mov':
            if 's' in self.supportBits:
                return '-> Error: Syntax (Move cannot set CPSR flags)'
            if 'i' in self.supportBits:
                self.binary32_line += '00000' # 5, = 22
                self.binary32_line += self.getSignedBinary(self.immediateValue) # 10, 32
                return '-> Success'
            self.binary32_line += format(int(self.hitRegister[1:]), '05b') # 5, = 22
            self.binary32_line += format(0, '010b') # 10, = 32
            return '-> Success'
        
        if 'r' not in self.hitRegister:
            return '-> Error: Syntax (registers must have "r" before address value)' # 5, = 17
        self.binary32_line += format(int(self.hitRegister[1:]), '05b') # 5, = 22
        if self.opCode == 'load' or self.opCode == 'store':
            if 's' in self.condition:
                return '-> Error: Syntax (Load / Store cannot set CPSR flags)'
            if 'i' not in self.condition:
                if 'r' not in self.operandRegister:
                    return '-> Error: Syntax (registers must have "r" before address value)'
                self.binary32_line += format(int(self.operandRegister[1:]), '05b') # 5, = 27
                self.binary32_line += format(0, '05b') # 5, = 32
                return '-> Success'
            self.binary32_line += self.getSignedBinary(self.immediateValue) # 10, = 32
            return '-> Success'
        
        if self.opCode in instructions.keys() and self.opCode != 'mov':
            if 'i' in self.supportBits:
                self.binary32_line += self.getSignedBinary(self.immediateValue) # 10, = 32
                return '-> Success'
            if 'r' not in self.operandRegister:
                return '-> Error: Syntax (registers must have "r" before address value)'
            self.binary32_line += format(int(self.operandRegister[1:]), '05b') # 5, = 27
            self.binary32_line += format(0, '05b') # 5, = 32
            return '-> Success'
    
    def getSignedBinary(self, immediateValue: str) -> str:
        if int(immediateValue) >= 0:
            return format(int(immediateValue), '010b')
        return '1'+format(1+(not (-int(immediateValue))), '010b')[1:]
    
    def disassemble(self, assembly_line: str) -> str:
        self.disassembler_response = self.getOpCode(assembly_line)
        if 'Error' in self.disassembler_response:
            return self.disassembler_response
        
        if self.opCode == 'l' or  self.opCode == 'll':
            return 'Success'
        
        if self.opCode == 'b' or self.opCode == 'bl':
            self.disassembler_response = self.getBranchValue(assembly_line)
            return self.disassembler_response
        
        if self.opCode == 'load' or self.opCode == 'store':
            self.disassembler_response = self.getLoadStoreRegisters(assembly_line)
            return self.disassembler_response
        
        if self.opCode == 'mov':
            self.disassembler_response = self.getMoveRegisters(assembly_line)
            return self.disassembler_response
        
        if (
                self.opCode == 'add'
                or self.opCode == 'sub'
                or self.opCode == 'mul'
                or self.opCode == 'div'
                or self.opCode == 'and'
                or self.opCode == 'or'
                or self.opCode == 'xor'
                or self.opCode == 'not'
                or self.opCode == 'teq'
                or self.opCode == 'cmp'
            ):
            self.disassembler_response = self.getDataProcessingRegisters(assembly_line)
            return self.disassembler_response
        
        return '-> Error: invalid OpCode'
    
    def getOpCode(self, assembly_line: str) -> str:
        for c_index, char in enumerate(assembly_line):
            if char == ':':
                self.opCode = assembly_line[:c_index].strip()
                self.disassembler_response = self.getCondition(self.opCode)
                if 'Error' in self.disassembler_response:
                    return self.disassembler_response
                return '-> Success'
        return '-> Error: Syntax (lacking ":")'
    
    def getCondition(self, fullOpCode: str) -> str:
        if fullOpCode[-2:] == 'eq':
            if fullOpCode[-4:-2] == 'gt' or fullOpCode[-4:-2] == 'lt':
                self.condition = fullOpCode[-4:]
                self.opCode = fullOpCode[:-4]
            elif fullOpCode[-3] == 'n':
                self.condition = fullOpCode[-3:]
                self.opCode = fullOpCode[:-3]
            else:
                self.condition = fullOpCode[-2:]
                self.opCode = fullOpCode[:-2]
        
        elif fullOpCode[-2:] == 'gt' or fullOpCode[-2:] == 'lt':
            self.condition = fullOpCode[-2:]
            self.opCode = fullOpCode[:-2]
        
        else:
            self.condition = 'do'
        
        self.disassembler_response = self.getSupportBits(self.opCode)
        if 'Error' in self.disassembler_response:
            return self.disassembler_response
        
        if self.opCode not in instructions.keys():
            return '-> Error: Syntax (invalid OpCode)'
        
        return '-> Success'
    
    def getSupportBits(self, opCodeWithBits: str):
        if opCodeWithBits[-1] == 's' or opCodeWithBits[-1] == 'i':
            if opCodeWithBits[-2] == 's' or opCodeWithBits[-2] == 'i':
                self.supportBits = opCodeWithBits[-2:]
                self.opCode = opCodeWithBits[:-2]
                return '-> Success'
            self.supportBits = opCodeWithBits[-1]
            self.opCode = opCodeWithBits[:-1]
            return '-> Success'
        
        self.supportBits = 'na'
        return '-> Success'
    
    def getMoveRegisters(self, assembly_line: str) -> str:
        # Only 2 registers
        # Only Rd and Rh
        self.disassembler_response = self.getDestinyRegister(assembly_line)
        if 'Error' in self.disassembler_response:
            return self.disassembler_response
        
        self.disassembler_response = self.getMoveHitRegister(assembly_line)
        if 'Error' in self.disassembler_response:
            return self.disassembler_response
        
        return '-> Success'
    
    def getMoveHitRegister(self, assembly_line: str) -> str:
        for c_index, char in enumerate(assembly_line):
            if char == '=':
                self.hitRegister = assembly_line[c_index+1:].strip()
                return '-> Success'
        return '-> Error: Syntax (invalid Rh)'
    
    def getBranchValue(self, assembly_line: str) -> str:
        for c_index, char in enumerate(assembly_line):
            if char == ':':
                if 'i' in self.supportBits:
                    self.immediateValue = assembly_line[c_index+1:].strip()
                    return '-> Success'
                else:
                    self.operandRegister = assembly_line[c_index+1:].strip()
                    return '-> Success'
        return '-> Error: Syntax (invalid branch offset value)'
    
    def getLoadStoreRegisters(self, assembly_line: str) -> str:
        self.disassembler_response = self.getDestinyRegister(assembly_line)
        if 'Error' in self.disassembler_response:
            return self.disassembler_response
        
        self.disassembler_response = self.getHitRegister(assembly_line)
        if 'Error' in self.disassembler_response:
            return self.disassembler_response
    
    def getDataProcessingRegisters(self, assembly_line: str) -> str:
        self.disassembler_response = self.getDestinyRegister(assembly_line)
        if 'Error' in self.disassembler_response:
            return self.disassembler_response
        
        self.disassembler_response = self.getHitRegister(assembly_line)
        if 'Error' in self.disassembler_response:
            return self.disassembler_response
        
        self.disassembler_response = self.getOperand2(assembly_line)
        if 'Error' in self.disassembler_response:
            return self.disassembler_response
    
    def getDestinyRegister(self, assembly_line: str) -> str:
        for c_index, char in enumerate(assembly_line):
            if char == ':':
                opCode_end = c_index
            elif char == '=':
                self.destinyRegister = assembly_line[opCode_end+1:c_index-1].strip()
                return '-> Success'
        return '-> Error: Syntax (invalid Rd)'
    
    def getHitRegister(self, assembly_line: str) -> str:
        for c_index, char in enumerate(assembly_line):
            if char == '=':
                rd_end = c_index
            elif char == ',':
                self.hitRegister = assembly_line[rd_end+1:c_index].strip()
                return '-> Success'
        return '-> Error: Syntax (invalid Rh)'
    
    def getOperand2(self, assembly_line: str) -> str:
        for c_index, char in enumerate(assembly_line):
            if char == ',':
                operand = assembly_line[c_index+1:].strip()
                if 'i' in self.supportBits:
                    self.immediateValue = operand
                else:
                    self.operandRegister = operand
                return '-> Success'
        return '-> Error: Syntax (invalid Ro)'


class FullCode(Instruction):

    assembly_list: list
    code_list: list
    full_code: str
    response: str = '-> Success'

    def __init__(self, assembly_code_lines: list):
        self.assembly_list = assembly_code_lines
        self.response = self.decode_full_code(self.assembly_list)
    
    def decode_full_code(self, assembly_list: str) -> str:
        self.code_list = []
        
        for row_index, row in enumerate(assembly_list):
            # print('Line begin. ', end='')
            line = Instruction(row)
            if 'Error' in line.response:
                print(f'{line.response} in line {row_index+1}.')
                self.response = line.response
            else:
                self.code_list.append(line.binary32_line+'\n')
            # print('Line end.')
        
        # print(self.response)
        if 'Error' in self.response:
            return self.response
        else:
            self.full_code = ''.join(self.code_list)
            return self.response