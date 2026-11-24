	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp main_start

	.align 16
mix:
    pushq %rbp
    movq %rsp, %rbp
    pushq %r12
    pushq %r13
    pushq %r14
    pushq %rbx
    subq $48, %rsp
    jmp mix_start

mix_start:
    movq %rdi, %rbx
    movq %rsi, %r12
    movq %rdx, %r13
    movq %rbx, %r14
    addq %r12, %r14
    movq %r12, -40(%rbp)
    movq %r13, %rax
    addq %rax, -40(%rbp)
    movq %r13, -48(%rbp)
    movq %rbx, %rax
    addq %rax, -48(%rbp)
    movq %r14, -56(%rbp)
    movq -40(%rbp), %rax
    imulq -56(%rbp), %rax
    movq %rax, -56(%rbp)
    movq -40(%rbp), %rax
    movq %rax, -64(%rbp)
    movq -48(%rbp), %rax
    imulq -64(%rbp), %rax
    movq %rax, -64(%rbp)
    movq -48(%rbp), %rax
    movq %rax, -72(%rbp)
    movq %r14, %rax
    imulq -72(%rbp), %rax
    movq %rax, -72(%rbp)
    movq -56(%rbp), %rcx
    addq -64(%rbp), %rcx
    movq %rcx, -80(%rbp)
    movq -72(%rbp), %rax
    addq %rax, -80(%rbp)
    movq -80(%rbp), %rdi
    movq %r14, %rsi
    callq mix2
    movq %rax, %rcx
    movq %rbx, %rdx
    addq %r12, %rdx
    addq %r13, %rdx
    addq %r14, %rdx
    addq -40(%rbp), %rdx
    addq -48(%rbp), %rdx
    addq -56(%rbp), %rdx
    addq -64(%rbp), %rdx
    addq -72(%rbp), %rdx
    addq -80(%rbp), %rdx
    addq %rcx, %rdx
    movq %rdx, %rax
    jmp mix_conclusion

mix_conclusion:
    addq $48, %rsp
    popq %rbx
    popq %r14
    popq %r13
    popq %r12
    popq %rbp
    retq 

	.align 16
mix2:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp mix2_start

mix2_start:
    movq %rdi, %rcx
    movq %rsi, %rdx
    movq %rcx, %rsi
    subq %rdx, %rsi
    imulq $2, %rsi, %rdi
    addq %rdi, %rsi
    addq %rcx, %rsi
    movq %rsi, %rcx
    addq %rdx, %rcx
    movq %rcx, %rax
    jmp mix2_conclusion

mix2_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

main_start:
    movq $1, %rdi
    movq $2, %rsi
    movq $3, %rdx
    callq mix
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    callq input_int
    movq %rax, %rcx
    movq %rcx, %rdi
    movq $4, %rsi
    movq $5, %rdx
    callq mix
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

main_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 



