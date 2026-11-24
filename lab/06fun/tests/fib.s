	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp main_start

	.align 16
fib:
    pushq %rbp
    movq %rsp, %rbp
    pushq %r12
    pushq %rbx
    subq $0, %rsp
    jmp fib_start

block1:
    movq $0, %rax
    jmp fib_conclusion

block2:
    movq %rbx, %rax
    jmp fib_conclusion

block3:
    movq %rbx, %rcx
    subq $1, %rcx
    movq %rcx, %rdi
    callq fib
    movq %rax, %r12
    movq %rbx, %rcx
    subq $2, %rcx
    movq %rcx, %rdi
    callq fib
    movq %rax, %rcx
    movq %r12, %rdx
    addq %rcx, %rdx
    movq %rdx, %rax
    jmp fib_conclusion

fib_start:
    movq %rdi, %rbx
    cmpq $2, %rbx
    jl block2
    jmp block3

fib_conclusion:
    addq $0, %rsp
    popq %rbx
    popq %r12
    popq %rbp
    retq 

	.align 16
fact:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    jmp fact_start

block4:
    movq $1, %rax
    jmp fact_conclusion

block5:
    movq %rbx, %rcx
    subq $1, %rcx
    movq %rcx, %rdi
    callq fact
    movq %rax, %rcx
    movq %rbx, %rdx
    imulq %rcx, %rdx
    movq %rdx, %rax
    jmp fact_conclusion

fact_start:
    movq %rdi, %rbx
    cmpq $0, %rbx
    je block4
    jmp block5

fact_conclusion:
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 

main_start:
    movq $10, %rdi
    callq fib
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $5, %rdi
    callq fact
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    callq input_int
    movq %rax, %rcx
    movq %rcx, %rdi
    callq fib
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

main_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 



