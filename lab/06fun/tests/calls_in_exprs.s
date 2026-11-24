	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    jmp main_start

	.align 16
sq:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp sq_start

sq_start:
    movq %rdi, %rcx
    imulq %rcx, %rcx
    movq %rcx, %rax
    jmp sq_conclusion

sq_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

	.align 16
add:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp add_start

add_start:
    movq %rdi, %rcx
    movq %rsi, %rdx
    addq %rdx, %rcx
    movq %rcx, %rax
    jmp add_conclusion

add_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

block2:
    movq %rbx, %rdi
    callq print_int
    callq input_int
    movq %rax, %rcx
    movq %rcx, %rdi
    callq sq
    movq %rax, %rbx
    movq $1, %rdi
    movq $1, %rsi
    callq add
    movq %rax, %rcx
    movq %rbx, %rax
    cqto 
    idivq %rcx
    movq %rax, %rcx
    movq $7, %rsi
    movq %rcx, %rax
    cqto 
    idivq %rsi
    movq %rdx, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

block3:
    movq %rbx, %rdi
    movq $1, %rsi
    callq add
    movq %rax, %rbx
    jmp block1

block1:
    movq %rbx, %rdi
    callq sq
    movq %rax, %rcx
    cmpq $50, %rcx
    jl block3
    jmp block2

block4:
    movq %rcx, %rdi
    callq print_int
    movq $0, %rbx
    jmp block1

block5:
    movq %rbx, %rdi
    callq sq
    movq %rax, %rcx
    jmp block4

block6:
    movq $0, %rcx
    jmp block4

main_start:
    movq $2, %rdi
    callq sq
    movq %rax, %rbx
    movq $3, %rdi
    callq sq
    movq %rax, %rcx
    movq %rbx, %rdi
    movq %rcx, %rsi
    callq add
    movq %rax, %rbx
    movq $1, %rdi
    movq $1, %rsi
    callq add
    movq %rax, %rcx
    movq %rcx, %rdi
    callq sq
    movq %rax, %rcx
    addq %rcx, %rbx
    movq %rbx, %rdi
    callq print_int
    movq %rbx, %rdi
    movq $1, %rsi
    callq add
    movq %rax, %rcx
    cmpq $10, %rcx
    jg block5
    jmp block6

main_conclusion:
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 



