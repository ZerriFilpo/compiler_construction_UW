	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    jmp start

block1:
    callq input_int
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

block2:
    movq $2, %rdi
    callq print_int
    jmp block1

block3:
    movq $3, %rdi
    callq print_int
    jmp block1

block4:
    callq input_int
    movq %rax, %rcx
    cmpq $5, %rcx
    jg block2
    jmp block3

block5:
    cmpq $0, %rbx
    jg block2
    jmp block4

block6:
    movq $1, %rdi
    callq print_int
    jmp block5

block7:
    movq $0, %rdi
    callq print_int
    jmp block5

block8:
    callq input_int
    movq %rax, %rcx
    cmpq $5, %rcx
    jg block6
    jmp block7

start:
    callq input_int
    movq %rax, %rbx
    cmpq $0, %rbx
    jg block8
    jmp block7

main_conclusion:
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 



