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
    i = 0

    data = []
    text = loc_file.readline()
    text = text.replace('\n', '')    # avoid '/n'

    text = text.split('\t')
    data.append(text[0])           # LOC

    data.append(text[1][0:6])          # LABEL

    data.append(text[1][6:])         # OPCODE

    data.append(text[2])           # OPERAND
    
    while(1):
        # preprocess data
        data = []
        text = loc_file.readline()
        text = text.replace('\n', '')    # avoid '/n'

        text = text.split('\t')
        data = text
        print(text)
        ## create object code
        # init object_code
        object_code = ''
        if data[1] != '.':
            if data[2] == 'END':
                break
