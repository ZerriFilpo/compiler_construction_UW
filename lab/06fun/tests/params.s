	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %r12
    pushq %rbx
    subq $0, %rsp
    jmp main_start

	.align 16
six:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp six_start

six_start:
    imulq $100000, %rdi, %rdi
    imulq $10000, %rsi, %rsi
    addq %rsi, %rdi
    imulq $1000, %rdx, %rdx
    movq %rdi, %rsi
    addq %rdx, %rsi
    imulq $100, %rcx, %rcx
    movq %rsi, %rdx
    addq %rcx, %rdx
    imulq $10, %r8, %rcx
    addq %rcx, %rdx
    movq %rdx, %rcx
    addq %r9, %rcx
    movq %rcx, %rax
    jmp six_conclusion

six_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

	.align 16
sub:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp sub_start

sub_start:
    movq %rdi, %rcx
    movq %rsi, %rdx
    subq %rdx, %rcx
    movq %rcx, %rax
    jmp sub_conclusion

sub_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

main_start:
    movq $1, %rdi
    movq $2, %rsi
    movq $3, %rdx
    movq $4, %rcx
    movq $5, %r8
    movq $6, %r9
    callq six
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $10, %rdi
    movq $3, %rsi
    callq sub
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $3, %rdi
    movq $10, %rsi
    callq sub
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $9, %rdi
    movq $8, %rsi
    callq sub
    movq %rax, %rbx
    movq $5, %rdi
    movq $2, %rsi
    callq sub
    movq %rax, %r12
    movq $7, %rdi
    movq $1, %rsi
    callq sub
    movq %rax, %r9
    movq %rbx, %rdi
    movq $2, %rsi
    movq %r12, %rdx
    movq $4, %rcx
    movq $5, %r8
    callq six
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

main_conclusion:
    addq $0, %rsp
    popq %rbx
    popq %r12
    popq %rbp
    retq 



