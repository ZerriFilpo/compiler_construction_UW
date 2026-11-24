	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp main_start

	.align 16
count:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp count_start

block1:
    subq $1, %rcx
    movq %rcx, %rdi
    callq count
    movq %rax, %rcx
    movq $1, %rdx
    addq %rcx, %rdx
    movq %rdx, %rax
    jmp count_conclusion

block2:
    movq $0, %rax
    jmp count_conclusion

count_start:
    movq %rdi, %rcx
    cmpq $0, %rcx
    je block2
    jmp block1

count_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

	.align 16
ack:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    jmp ack_start

block3:
    movq %rcx, %rbx
    subq $1, %rbx
    subq $1, %rdx
    movq %rcx, %rdi
    movq %rdx, %rsi
    callq ack
    movq %rax, %rcx
    movq %rbx, %rdi
    movq %rcx, %rsi
    callq ack
    movq %rax, %rcx
    movq %rcx, %rax
    jmp ack_conclusion

block4:
    subq $1, %rcx
    movq %rcx, %rdi
    movq $1, %rsi
    callq ack
    movq %rax, %rcx
    movq %rcx, %rax
    jmp ack_conclusion

block5:
    cmpq $0, %rdx
    je block4
    jmp block3

block6:
    movq %rdx, %rcx
    addq $1, %rcx
    movq %rcx, %rax
    jmp ack_conclusion

ack_start:
    movq %rdi, %rcx
    movq %rsi, %rdx
    cmpq $0, %rcx
    je block6
    jmp block5

ack_conclusion:
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 

main_start:
    movq $10000, %rdi
    callq count
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $2, %rdi
    movq $3, %rsi
    callq ack
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

main_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 



