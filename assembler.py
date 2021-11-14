import numpy as np
LOCCTR = 0
starting_address = 0
tot_size = 0

# create symbol table
SYMTAB = dict()

# create opcode table
OPTAB = {
    'STL':'14', 'JSUB':'48', 'LDA':'00', 'COMP':'28', 'JEQ':'30', 'J':'3c', 'STA':'0c', 'LDL':'08', 'RSUB':'4c', 'LDX':'04', 'TD':'e0', 'RD':'d8', 'STCH':'54', 'TIX':'2c', 'JLT':'38', 'STX':'10', 'LDCH':'50', 'WD':'dc'
}

# open loc.txt
loc_file = open('loc.txt', 'w')

### PASS1
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
        
        # check is symbol exit in symbol table 1/show error, 0/insert in symbol table  
        if data[0]!='':
            if SYMTAB.get(data[0]) != None:
                print('[error] : dulicate symbol')
            else:
                SYMTAB.update({data[0]:hex(LOCCTR)})
        
        # output loc.txt
        loc_file.writelines(f'{LOCCTR:x} {text}\n')

        ## move loc counter
        # normal opcode
        if OPTAB.get(data[1]) != None:
            LOCCTR += 3

        # assembler directive
        elif data[1] == 'WORD':
            LOCCTR += 3

        elif data[1] == 'RESW':
            LOCCTR += 3*int(data[2])

        elif data[1] == 'RESB':
            LOCCTR += int(data[2])

        elif data[1] == 'BYTE':
            type = data[2][0]                      # c(charactor)/x(hex number)
            value = data[2][1:].replace('\'', '')  # 'value' -> value

            if type == 'X':
                LOCCTR += int(len(value)/2)
            if type == 'C':
                LOCCTR += len(value)

        # END
        elif data[1] == 'END':
            tot_size = LOCCTR-starting_address

            loc_file.writelines(f'{hex(LOCCTR)[2:]} {text}\n')
            loc_file.close()
            break

        else:
            print('[error] : invalid operation code')

# open output.txt         
list_file = open('output.txt', 'w')

# open objectcode.txt
object_program = open('objectcode.txt', 'w')

# update part of string
def update_str(source, target, start=0, end=0):
    sour = list(source)
    tar = list(target)
    range = np.arange(start, end+1)
    for i, item in enumerate(range):
        sour[item] = tar[i]
    
    return ''.join(sour)

### PASS2
with open('loc.txt', 'r') as loc_file:
    '''
    Header record :
     -------------------------------------------------------------------------
    | 1bit |  6bit  |           6bit            |             6bit            |
    |-------------------------------------------------------------------------
    |  H   | [NAME] |   [program starting loc]  |  [ total program length ]   |
     -------------------------------------------------------------------------
    Text record : 
     -----------------------------------------------------
    | 1bit |         6bit        |   2bit   | (max:30bit) |
    |-----------------------------------------------------
    |  T   | [text starting loc] |   [LEN]  |  [ ... ]    |
     -----------------------------------------------------
    End record :
     ----------------------------------
    | 1bit |           6bit            |
    |----------------------------------
    |  E   |   [program starting loc]  |
     ----------------------------------
    '''

    # init first record
    text_len = 0        # LEN
    program_text = ''   # Text record
    Isempty = False       # jump black block

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

        ## create object code
        # init object_code
        object_code = ''

        # START
        if data[2] == 'START':
            list_file.writelines(f'{text}\n')                                            #  output listing line
            object_program.write(f'H{data[1]:6s}{starting_address:06x}{tot_size:06x}\n') #  output Header record
            continue
        # normal opcode
        if OPTAB.get(data[2]) != None:
            opcode = data[2]
            operand = data[3].split(',')[0]  # avoid ,X

            # check Is operand -> None 1/set(0000)
            if(operand !=' '):
                object_code = OPTAB[opcode]+SYMTAB[operand][2:]
            else:
                object_code = OPTAB[opcode]+'0000'
        
        # assembler directive   
        elif data[2] == 'WORD':
            object_code = f'{int(data[3]):06x}'

        elif data[2] == 'BYTE':
            type = data[3][0]                       # c(charactor)/x(hex number)
            value = data[3][1:].replace('\'', '')   # 'value' -> value

            if type == 'X':
                object_code = value
            if type == 'C':
                # char -> ascii
                asic = ''   
                for item in value:
                    asic +=  hex(ord(item))[2:]
                object_code = asic
            
        list_file.writelines(f'{text} {object_code}\n')

        ## create object program
        if text_len == 0:
            program_text = f'T00{data[0]}__'         # new Text record

        # check Is text record's length over max length 1/output Text record and new Text record
        if text_len+(len(object_code)/2)>30:
            # update Text record's LEN
            size = hex(int(len(program_text[9:])/2))[2:]
            program_text = update_str(program_text, size, 7, 8)
            
            # out Text record
            object_program.write(program_text+'\n')   

            # new Text record
            program_text = f'T00{data[0]}__'          
            text_len = 0
        
        # trailing object code
        if object_code!='':
            Isempty = False
            text_len += int(len(object_code)/2)
            program_text += object_code

        else:
            # check trailing object code is empty 1/new line, 0/output Text record
            if not Isempty:
                size = hex(int(len(program_text[9:])/2))[2:]
                if len(size) == 2:
                    program_text = update_str(program_text, size, 7, 8)
                else:
                    program_text = update_str(program_text, '0'+size, 7, 8)

                object_program.write(program_text+'\n')
                Isempty = True
            
            text_len = 0

        # END
        if data[2] == 'END':
            object_program.write(f'E00{SYMTAB[data[3]][2:]}')
            object_program.close()
            list_file.close()
            break
        
        




        



        




        

        

        
        

        
            
          
    
    
    