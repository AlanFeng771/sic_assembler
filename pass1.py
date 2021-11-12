LOCCTR = 0
starting_address = 0
tot_size = 0

SYMTAB = dict()
# SYMTAB.update({' ':hex(0)})

OPTAB = {
    'STL':'14', 'JSUB':'48', 'LDA':'00', 'COMP':'28', 'JEQ':'30', 'J':'3c', 'STA':'0c', 'LDL':'08', 'RSUB':'4c', 'LDX':'04', 'TD':'e0', 'RD':'d8', 'STCH':'54', 'TIX':'2c', 'JLT':'38', 'STX':'10', 'LDCH':'50', 'WD':'dc'
}

# open loc.txt
loc_file = open('loc.txt', 'w')

### PASS1

## create symbol table, loc
with open('input.txt', 'r') as file:
    while(1):
        # preprocess data
        data = []
        text = file.readline()
        text = text.replace('\n', '')    # avoid '/n'

        data.append(text[0:6])           # LABEL
        data[0] = data[0].replace(' ', '')

        data.append(text[8:14])          # OPCODE
        data[1] = data[1].replace(' ', '')

        data.append(text[14:])           # OPERAND
        
        # START
        if data[1] == 'START':
            starting_address = int(f'0x{data[2]}', 16)
            LOCCTR = starting_address
            loc_file.writelines(f'{hex(starting_address)[2:]} {text}\n')
            continue

        if data[0]!='':
            if SYMTAB.get(data[0]) != None:
                print('[error] : dulicate symbol')
            else:
                SYMTAB.update({data[0]:hex(LOCCTR)})

        loc_file.writelines(f'{hex(LOCCTR)[2:]} {text}\n')

        if OPTAB.get(data[1]) != None:
            LOCCTR += 3

        elif data[1] == 'WORD':
            LOCCTR += 3

        elif data[1] == 'RESW':
            LOCCTR += 3*int(data[2])

        elif data[1] == 'RESB':
            LOCCTR += int(data[2])

        elif data[1] == 'BYTE':
            type = data[2][0]
            value = data[2][1:].replace('\'', '')

            if type == 'X':
                LOCCTR += int(len(value)/2)
            if type == 'C':
                LOCCTR += len(value)

        elif data[1] == 'END':
            tot_size = LOCCTR-starting_address

            loc_file.writelines(f'{hex(LOCCTR)[2:]} {text}\n')
            loc_file.close()
            break

        else:
            print('[error] : invalid operation code')
        
## create intermediate file           
inter_file = open('output.txt', 'w')
with open('loc.txt', 'r') as loc_file:
    while(1):
        # preprocess data
        data = []
        text = loc_file.readline()
        text = text.replace('\n', '')    # avoid '/n'

        data.append(text[0:4])           # LOC

        data.append(text[5:11])          # LABEL
        data[1] = data[1].replace(' ', '')

        data.append(text[13:19])         # OPCODE
        data[2] = data[2].replace(' ', '')

        data.append(text[19:])           # OPERAND

        ## add object code
        object_code = ''
        if data[2] == 'START':
            # object_code = ' '
            inter_file.writelines(f'{text} {object_code}\n')
            continue
        
        if OPTAB.get(data[2]) != None:
            opcode = data[2]
            operand = data[3].split(',')[0]  # avoid ,X
            if(operand !=' '):
                object_code = OPTAB[opcode]+SYMTAB[operand][2:]
            else:
                object_code = OPTAB[opcode]+'0000'
            
            
        elif data[2] == 'WORD':
            object_code = f'{int(data[3]):06x}'
            # inter_file.writelines(f'{text} {object_code:06x}\n')

        elif data[2] == 'BYTE':
            type = data[3][0]
            value = data[3][1:].replace('\'', '')

            if type == 'X':
                object_code = value

            if type == 'C':
                asic = ''
                for item in value:
                    asic +=  hex(ord(item))[2:]
                
                object_code = asic

        elif data[2] == 'END':
            # object_code = ' '
            inter_file.writelines(f'{text} {object_code}\n')
            inter_file.close()
            break

        inter_file.writelines(f'{text} {object_code}\n')

object_program = open('objectcode.txt', 'w')
with open('output.txt', 'r') as interfile:
    # init first record
    text_len = 0
    program_text = ''
    empty = False
    while(1):
        # preprocess data
        data = []
        text = interfile.readline()
        text = text.replace('\n', '')        # avoid '/n'

        data.append(text[0:4])               # LOC

        data.append(text[5:11])              # LABEL
        data[1] = data[1].replace(' ', '')

        data.append(text[13:19])             # OPCODE
        data[2] = data[2].replace(' ', '')
          
        data.append(text[19:].split(' ')[-2]) # OPERAND

        data.append(text[19:].split(' ')[-1]) # Object code
        
        if data[2] == 'START':
            object_program.write(f'H{data[1]:6s}{starting_address:06x}{tot_size:06x}\n')
            continue
        

        if text_len == 0:
            # if not empty:
            program_text = f'T00{data[0]}__'
            
        if text_len+(len(data[-1])/2)>30:
            program_text = list(program_text)
            size = hex(int(len(program_text[9:])/2))[2:]
            program_text[7] = size[0]
            program_text[8] = size[1]
            program_text = ''.join(program_text)
            object_program.write(program_text+'\n')
            program_text = f'T00{data[0]}__'
            text_len = 0

        if data[-1]!='':
            empty = False
            text_len += int(len(data[-1])/2)
            program_text += data[-1]
        else:
            if not empty:
                program_text = list(program_text)
                size = hex(int(len(program_text[9:])/2))[2:]
                if len(size) == 2:
                    program_text[7] = size[0]
                    program_text[8] = size[1]
                else:
                    program_text[7] = '0'
                    program_text[8] = size[0]
                program_text = ''.join(program_text)
                object_program.write(program_text+'\n')
                empty = True
            text_len = 0
            
        if data[2] == 'END':
            object_program.write(f'E00{SYMTAB[data[3]][2:]}')
            object_program.close()
            break


        



        




        

        

        
        

        
            
          
    
    
    