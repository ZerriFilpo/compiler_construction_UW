	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %r12
    pushq %r13
    pushq %r14
    pushq %rbx
    subq $16, %rsp
    jmp main_start

	.align 16
clobber:
    pushq %rbp
    movq %rsp, %rbp
    pushq %r12
    pushq %r13
    pushq %r14
    pushq %rbx
    subq $16, %rsp
    jmp clobber_start

clobber_start:
    movq %rdi, %rcx
    movq %rcx, %rbx
    addq $1, %rbx
    movq %rbx, %r12
    addq $1, %r12
    movq %r12, %r13
    addq $1, %r13
    movq %r13, %r14
    addq $1, %r14
    movq %r14, -40(%rbp)
    movq $1, %rax
    addq %rax, -40(%rbp)
    movq -40(%rbp), %rdi
    callq print_int
    movq %rbx, %rcx
    addq %r12, %rcx
    addq %r13, %rcx
    addq %r14, %rcx
    addq -40(%rbp), %rcx
    movq %rcx, %rax
    jmp clobber_conclusion

clobber_conclusion:
    addq $16, %rsp
    popq %rbx
    popq %r14
    popq %r13
    popq %r12
    popq %rbp
    retq 

main_start:
    callq input_int
    movq %rax, %rbx
    movq %rbx, %r12
    addq $1, %r12
    movq %r12, %r13
    addq $1, %r13
    movq %r13, %r14
    addq $1, %r14
    movq %r14, -40(%rbp)
    movq $1, %rax
    addq %rax, -40(%rbp)
    movq %rbx, %rdi
    callq clobber
    movq %rax, %rcx
    movq %rbx, %rdx
    addq %r12, %rdx
    addq %r13, %rdx
    addq %r14, %rdx
    addq -40(%rbp), %rdx
    addq %rcx, %rdx
    movq %rdx, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

main_conclusion:
    addq $16, %rsp
    popq %rbx
    popq %r14
    popq %r13
    popq %r12
    popq %rbp
    retq 



