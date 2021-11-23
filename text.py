from os import write


LOCCTR = 0
starting_address = 0
tot_size = 0

SYMTAB = dict()

OPTAB = {
    'STL':'14', 'JSUB':'48', 'LDA':'00', 'COMP':'28', 'JEQ':'30', 'J':'3c', 'STA':'0c', 'LDL':'08', 'RSUB':'4c', 'LDX':'04', 'TD':'e0', 'RD':'d8', 'STCH':'54', 'TIX':'2c', 'JLT':'38', 'STX':'10', 'LDCH':'50', 'WD':'dc'
}

loc = open('loc.txt', 'w')

with open('input.txt', 'r') as lines:
    data = []

    line = lines.readline()
    line = line.replace('\n', '')

    data.append(line[0:6])
    data += line[6:].split('\t')

    starting_address = int(data[2], 16)
    LOCCTR = starting_address
    
    loc.write(f'{LOCCTR:04x}\t{line}\n')
    # print(data)
    while(1):
        data = []
        line = lines.readline()
        line = line.replace('\n', '')
        data = line.split('\t')
        if len(data) == 2:
            data.append('')
        
        loc.write(f'{LOCCTR:04x}\t{line}\n')
        # print(data)
        if data[0] != '.':
            if data[0] != '':
                if SYMTAB.get(data[0]) != None:
                    print('[error] : dulicate symbol')
                else:
                    SYMTAB.update({data[0] : hex(LOCCTR)[2:]})
            
            if OPTAB.get(data[1]) != None:
                LOCCTR += 3

            elif data[1] == 'WORD':
                LOCCTR += 3

            elif data[1] == 'BYTE':
                type = data[2][0]
                if type == 'C':
                    length = len(data[2][1:]) - 2 
                    LOCCTR += length
                
                if type == 'X':
                    length = len(data[2][1:]) - 2 
                    length /= 2
                    length = int(length)
                    LOCCTR += length
                    
            elif data[1] == 'RESW':
                size = int(data[2]) * 3
                LOCCTR += size

            elif data[1] == 'RESB':
                size = int(data[2])
                LOCCTR += size

            if data[1] == 'END':
                tot_size = LOCCTR - starting_address
                loc.close()
                break

output = open('output.txt', 'w')
objcode = open('objectcode.txt', 'w')
text = ''
with open('loc.txt') as loc:
    line = loc.readline()
    line = line.replace('\n', '')
    data = []
    data.append(line[0:4])
    data.append(line[5:10])
    data += line[10:].split('\t')
    output.write(f'{line}\n')
    objcode.write(f'H{data[1]}00{data[0]}{tot_size:06x}\n')
    while(1):
        opcode = ''
        line = loc.readline()
        line = line.replace('\n', '')

        data = []
        data = line.split('\t')
        if len(data) == 3:
            data.append('')

        if data[1] != '.':
            if OPTAB.get(data[2]) != None:
                operand = data[3].split(',')
                x = False if len(operand)==2 else True
                if data[3] != '':
                    if x:
                        opcode = OPTAB[data[2]] + SYMTAB[operand[0]]
                    else:
                        opcode = OPTAB[data[2]] + hex(int(SYMTAB[operand[0]][0])+8)[2:] + SYMTAB[operand[0]][1:]
                else:
                    opcode = OPTAB[data[2]] + '0000'

            elif data[2] == 'WORD':
                opcode = f'{int(data[3]):06x}'
                           
            elif data[2] == 'BYTE':
                type = data[3][0]
                if type == 'C':
                    for ascii in data[3][1:].replace('\'', ''):
                        opcode += hex(ord(ascii))[2:]
                
                if type == 'X':
                    opcode = data[3][1:].replace('\'', '')
                    
            
            if data[2] == 'END':
                output.write(f'{line}\n')
                num = int(len(text[9:])/2)
                
                text = list(text)
                if num <= 15:
                    text[7] = '0'
                    text[8] = hex(num)[2]
                    text = ''.join(text)
                else:
                    text[7] = hex(num)[2]
                    text[8] = hex(num)[3]
                    text = ''.join(text)
                
                objcode.write(f'{text}\n')
                objcode.write(f'E{starting_address:06x}\n')
                output.close()
                objcode.close()
                break

            if len(text+opcode)>69 or opcode=='':
                if len(text)>9:
                    num = int(len(text[9:])/2)

                    text = list(text)
                    if num <= 15:
                        text[7] = '0'
                        text[8] = hex(num)[2]
                        text = ''.join(text)
                    else:
                        text[7] = hex(num)[2]
                        text[8] = hex(num)[3]
                        text = ''.join(text)
 
                    objcode.write(f'{text}\n')
                text = ''
            if opcode != '':
                if len(text) == 0:
                    text = f'T00{data[0]}__{opcode}'
                else:
                    text += opcode
            
            

        
        output.write(f'{line}\t{opcode}\n')
    