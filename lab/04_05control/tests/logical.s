	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %r12
    pushq %rbx
    subq $0, %rsp
    jmp start

block1:
    movq $0, %rax
    jmp main_conclusion

block2:
    movq $2, %rdi
    callq print_int
    jmp block1

block3:
    cmpq $0, %rbx
    je block2
    jmp block1

block4:
    cmpq $2, %rbx
    je block2
    jmp block1

block5:
    cmpq $1, %rbx
    jl block3
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
    cmpq %r12, %rbx
    jne block7
    jmp block6

block9:
    cmpq $0, %r12
    jg block6
    jmp block8

block10:
    movq %rcx, %rdx
    xorq $1, %rdx
    addq %rsi, %rcx
    addq %rdx, %rcx
    movq %rcx, %rdi
    callq print_int
    cmpq $0, %rbx
    jg block9
    jmp block8

block11:
    cmpq $100, %rbx
    setg %al
    movzbq %al, %rsi
    jmp block10

block12:
    movq $1, %rsi
    jmp block10

block13:
    cmpq %r12, %rbx
    je block11
    jmp block12

block14:
    cmpq $10, %r12
    setl %al
    movzbq %al, %rcx
    jmp block13

block15:
    movq $0, %rcx
    jmp block13

start:
    callq input_int
    movq %rax, %rbx
    callq input_int
    movq %rax, %r12
    cmpq %r12, %rbx
    jl block14
    jmp block15

main_conclusion:
    addq $0, %rsp
    popq %rbx
    popq %r12
    popq %rbp
    retq 



