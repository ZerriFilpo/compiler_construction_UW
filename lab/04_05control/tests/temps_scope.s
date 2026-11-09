	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %r12
    pushq %rbx
    subq $0, %rsp
    jmp start

block2:
    movq %rbx, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

block3:
    addq %rcx, %rbx
    addq $1, %r12
    jmp block1

block4:
    imulq $2, %r12, %rcx
    jmp block3

block5:
    movq %r12, %rcx
    addq $100, %rcx
    jmp block3

block6:
    cmpq $1, %r12
    jg block4
    jmp block5

block1:
    callq input_int
    movq %rax, %rcx
    addq %r12, %rcx
    cmpq $0, %rcx
    jg block6
    jmp block2

block7:
    movq %rcx, %rdi
    callq print_int
    movq $0, %r12
    movq $0, %rbx
    jmp block1

block8:
    addq $1, %rcx
    jmp block7

block9:
    subq $1, %rcx
    jmp block7

start:
    callq input_int
    movq %rax, %rcx
    cmpq $0, %rcx
    jg block8
    jmp block9

main_conclusion:
    addq $0, %rsp
    popq %rbx
    popq %r12
    popq %rbp
    retq 



