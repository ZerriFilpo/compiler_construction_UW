	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp main_start

	.align 16
g:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp g_start

g_start:
    movq %rdi, %rcx
    addq $1, %rcx
    movq %rcx, %rax
    jmp g_conclusion

g_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

	.align 16
f:
    pushq %rbp
    movq %rsp, %rbp
    pushq %r12
    pushq %r13
    pushq %rbx
    subq $8, %rsp
    jmp f_start

f_start:
    movq %rdi, %rbx
    movq %rsi, %r12
    movq %rbx, %rdi
    callq g
    movq %rax, %r13
    movq %r12, %rdi
    callq g
    movq %rax, %rcx
    movq %rbx, %rdx
    addq %r12, %rdx
    addq %r13, %rdx
    addq %rcx, %rdx
    movq %rdx, %rax
    jmp f_conclusion

f_conclusion:
    addq $8, %rsp
    popq %rbx
    popq %r13
    popq %r12
    popq %rbp
    retq 

main_start:
    movq $10, %rdi
    movq $20, %rsi
    callq f
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

main_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 



