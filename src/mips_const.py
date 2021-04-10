REGISTERS = [
    '$0',                                                    # Always equal to zero
    '$at',                                                      # Assembler temporary; used by the assembler
    '$v0', '$v1',                                               # Return value from a function call
    '$a0', '$a1', '$a2', '$a3',                                 # First four parameters from a function call
    '$t0', '$t1', '$t2', '$t3', '$t4', '$t5', '$t6', '$t7',     # Temporary variables; need not be preserved
    '$s0', '$s1', '$s2', '$s3', '$s4', '$s5', '$s6', '$s7',     # Function variables; must be preserved
    '$t8', '$t9',                                               # Two more temporary variables
    '$k0', '$k1',                                               # Kernel use registers; may change unexpectedly
    '$gp',                                                      # Global pointer
    '$sp',                                                      # Stack pointer
    '$fp',                                                      # Stack frame pointer
    '$ra'                                                       # Return address of the last subroutine call
]

SUPPLEMENT = """

 _StringEqual:
    subu $sp, $sp, 8
    sw $fp, 8($sp)
    sw $ra, 4($sp)
    addiu $fp, $sp, 8
    lw $a0, 4($fp)
    lw $a1, 8($fp)
    stre $v0, $a0, $a1
    # EndFunc
    move $sp, $fp
    lw $ra, -4($fp)
    lw $fp, 0($fp)
    jr $ra

 _ReadLine:
    subu $sp, $sp, 8
    sw $fp, 8($sp)
    sw $ra, 4($sp)
    addiu $fp, $sp, 8
    li $a0, 101
    li $v0, 9
    syscall
    addi $a0, $v0, 0
    li $v0, 8
    li $a1, 101
    syscall
    addiu $v0, $a0, 0
    # EndFunc
    move $sp, $fp
    lw $ra, -4($fp)
    lw $fp, 0($fp)
    jr $ra
"""
INSTRUCTIONS = set([
    'ADD',
    'ADDI',
    'ADDIU',
    'ADDU',
    'CLO',
    'CLZ',
    'LA',
    'LI',
    'LUI',
    'MOVE',
    'NEGU',
    'SEB',
    'SEH',
    'SUB',
    'SUBU',
    'ROTR',
    'ROTRV',
    'SLL',
    'SLLV',
    'SRA',
    'SRAV',
    'SRL',
    'SRLV',
    'AND',
    'ANDI',
    'EXT',
    'INS',
    'NOP',
    'NOR',
    'NOT',
    'OR',
    'ORI',
    'WSBH',
    'XOR',
    'XORI',
    'MOVN',
    'MOVZ',
    'SLT',
    'SLTI',
    'SLTIU',
    'SLTU',
    'DIV',
    'DIVU',
    'MADD',
    'MADDU',
    'MSUB',
    'MSUBU',
    'MUL',
    'MULT',
    'MULTU',
    'MFHI',
    'MFLO',
    'MTHI',
    'MTLO',
    'B',
    'BAL',
    'BEQ',
    'BEQZ',
    'BGEZ',
    'BGEZAL',
    'BGTZ',
    'BLEZ',
    'BLTZ',
    'BLTZAL',
    'BNE',
    'BNEZ',
    'J',
    'JAL',
    'JALR',
    'JR',
    'LB',
    'LBU',
    'LH',
    'LHU',
    'LW',
    'LWL',
    'LWR',
    'SB',
    'SH',
    'SW',
    'SWL',
    'SWR',
    'ULW',
    'USW',
    'LL',
    'SC',
    'SYSCALL',
    'SLT',
    'SEQ',
    'REM',
    'STRE'
])