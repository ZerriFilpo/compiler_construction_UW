	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp main_start

	.align 16
show:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp show_start

show_start:
    movq %rdi, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax
    jmp show_conclusion

show_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

	.align 16
readsum:
    pushq %rbp
    movq %rsp, %rbp
    pushq %r12
    pushq %r13
    pushq %rbx
    subq $8, %rsp
    jmp readsum_start

block2:
    movq %rbx, %rax
    jmp readsum_conclusion

block3:
    callq input_int
    movq %rax, %rcx
    addq %rcx, %rbx
    addq $1, %r12
    jmp block1

block1:
    cmpq %r13, %r12
    jl block3
    jmp block2

readsum_start:
    movq %rdi, %r13
    movq $0, %rbx
    movq $0, %r12
    jmp block1

readsum_conclusion:
    addq $8, %rsp
    popq %rbx
    popq %r13
    popq %r12
    popq %rbp
    retq 

block4:
    movq $0, %rax
    jmp main_conclusion

block5:
    movq $2, %rdi
    callq print_int
    jmp block4

main_start:
    movq $5, %rdi
    callq show
    callq input_int
    movq %rax, %rcx
    movq %rcx, %rdi
    callq show
    movq $3, %rdi
    callq readsum
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $1, %rdi
    callq show
    movq %rax, %rcx
    cmpq $0, %rcx
    je block5
    jmp block4

main_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 



