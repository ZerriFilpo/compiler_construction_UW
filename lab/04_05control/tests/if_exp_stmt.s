	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    jmp start

block1:
    movq $0, %rax
    jmp main_conclusion

block2:
    movq $7, %rdi
    callq print_int
    jmp block1

block3:
    cmpq $0, %rbx
    jl block2
    jmp block1

block4:
    movq $1, %rdi
    callq print_int
    jmp block3

block5:
    movq $0, %rdi
    callq print_int
    jmp block3

block6:
    movq $1, %rcx
    addq %rdx, %rcx
    movq %rcx, %rdi
    callq print_int
    cmpq $3, %rbx
    jg block4
    jmp block5

block7:
    movq $100, %rdx
    jmp block6

block8:
    movq $200, %rdx
    jmp block6

block9:
    movq %rcx, %rdi
    callq print_int
    cmpq $5, %rbx
    je block7
    jmp block8

block10:
    movq $10, %rcx
    jmp block9

block11:
    movq $20, %rcx
    jmp block9

start:
    callq input_int
    movq %rax, %rbx
    cmpq $0, %rbx
    jg block10
    jmp block11

main_conclusion:
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 



