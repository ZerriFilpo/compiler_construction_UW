	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %r12
    pushq %r13
    pushq %rbx
    subq $8, %rsp
    jmp start

block1:
    movq %rbx, %rcx
    addq %r12, %rcx
    addq %r13, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

block2:
    movq $1, %rdi
    callq print_int
    jmp block1

block3:
    movq $2, %rdi
    callq print_int
    jmp block1

block4:
    cmpq $0, %r13
    jg block2
    jmp block3

block5:
    movq $3, %rdi
    callq print_int
    jmp block1

block6:
    cmpq $0, %r12
    jg block4
    jmp block5

block7:
    movq $4, %rdi
    callq print_int
    jmp block1

block8:
    movq $5, %rdi
    callq print_int
    jmp block1

block9:
    cmpq $0, %r12
    jg block7
    jmp block8

start:
    callq input_int
    movq %rax, %rbx
    callq input_int
    movq %rax, %r12
    callq input_int
    movq %rax, %r13
    cmpq $0, %rbx
    jg block6
    jmp block9

main_conclusion:
    addq $8, %rsp
    popq %rbx
    popq %r13
    popq %r12
    popq %rbp
    retq 



