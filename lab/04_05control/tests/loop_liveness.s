	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %r12
    pushq %r13
    pushq %r14
    pushq %rbx
    subq $80, %rsp
    jmp start

block2:
    movq %rbx, %rcx
    addq %r12, %rcx
    addq %r13, %rcx
    addq %r14, %rcx
    addq -40(%rbp), %rcx
    addq -48(%rbp), %rcx
    addq -56(%rbp), %rcx
    addq -64(%rbp), %rcx
    addq -72(%rbp), %rcx
    addq -80(%rbp), %rcx
    addq -88(%rbp), %rcx
    addq -96(%rbp), %rcx
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

block3:
    movq $1, %rax
    addq %rax, -104(%rbp)
    jmp block1

block4:
    movq %rbx, %rcx
    addq %r12, %rcx
    addq %r13, %rcx
    addq %r14, %rcx
    addq -40(%rbp), %rcx
    addq -48(%rbp), %rcx
    addq -56(%rbp), %rcx
    addq -64(%rbp), %rcx
    addq -72(%rbp), %rcx
    addq -80(%rbp), %rcx
    addq -88(%rbp), %rcx
    addq -96(%rbp), %rcx
    addq %rdx, %rcx
    movq %rcx, %rdi
    callq print_int
    jmp block3

block5:
    movq %rdx, %rdi
    callq print_int
    jmp block3

block6:
    callq input_int
    movq %rax, %rdx
    cmpq %rbx, %rdx
    jg block4
    jmp block5

block1:
    cmpq $3, -104(%rbp)
    jl block6
    jmp block2

start:
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
    movq -40(%rbp), %rax
    movq %rax, -48(%rbp)
    movq $1, %rax
    addq %rax, -48(%rbp)
    movq -48(%rbp), %rax
    movq %rax, -56(%rbp)
    movq $1, %rax
    addq %rax, -56(%rbp)
    movq -56(%rbp), %rax
    movq %rax, -64(%rbp)
    movq $1, %rax
    addq %rax, -64(%rbp)
    movq -64(%rbp), %rax
    movq %rax, -72(%rbp)
    movq $1, %rax
    addq %rax, -72(%rbp)
    movq -72(%rbp), %rax
    movq %rax, -80(%rbp)
    movq $1, %rax
    addq %rax, -80(%rbp)
    movq -80(%rbp), %rax
    movq %rax, -88(%rbp)
    movq $1, %rax
    addq %rax, -88(%rbp)
    movq -88(%rbp), %rax
    movq %rax, -96(%rbp)
    movq $1, %rax
    addq %rax, -96(%rbp)
    movq $0, -104(%rbp)
    jmp block1

main_conclusion:
    addq $80, %rsp
    popq %rbx
    popq %r14
    popq %r13
    popq %r12
    popq %rbp
    retq 



