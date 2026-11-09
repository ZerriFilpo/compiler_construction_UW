	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp start

block2:
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

block4:
    addq $1, %rdx
    jmp block1

block5:
    movq %rdx, %rsi
    imulq %rdi, %rsi
    addq %rsi, %rcx
    addq $1, %rdi
    jmp block3

block3:
    cmpq %rdx, %rdi
    jl block5
    jmp block4

block6:
    movq $0, %rdi
    jmp block3

block1:
    cmpq %r8, %rdx
    jl block6
    jmp block2

start:
    callq input_int
    movq %rax, %r8
    movq $0, %rdx
    movq $0, %rcx
    jmp block1

main_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 



