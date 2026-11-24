	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    jmp main_start

	.align 16
soma:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp soma_start

soma_start:
    movq %rdi, %rcx
    movq %rsi, %rdx
    addq %rdx, %rcx
    movq %rcx, %rax
    jmp soma_conclusion

soma_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

	.align 16
positivo:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp positivo_start

block1:
    cmpq $100, %rcx
    setl %al
    movzbq %al, %rcx
    movq %rcx, %rax
    jmp positivo_conclusion

block2:
    movq $0, %rax
    jmp positivo_conclusion

positivo_start:
    movq %rdi, %rcx
    cmpq $0, %rcx
    jg block1
    jmp block2

positivo_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

	.align 16
escolhe:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp escolhe_start

block3:
    movq $0, %rax
    jmp escolhe_conclusion

block4:
    movq %rcx, %rax
    jmp escolhe_conclusion

block5:
    movq %rdx, %rax
    jmp escolhe_conclusion

block6:
    cmpq $0, %rcx
    je block4
    jmp block5

escolhe_start:
    movq %rdi, %rcx
    movq %rsi, %rdx
    cmpq %rdx, %rcx
    jg block4
    jmp block6

escolhe_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

block7:
    movq $0, %rax
    jmp main_conclusion

block8:
    movq $1, %rdi
    callq print_int
    jmp block7

block9:
    cmpq $5, %rbx
    je block7
    jmp block8

main_start:
    movq $1, %rdi
    movq $2, %rsi
    callq soma
    movq %rax, %rbx
    movq %rbx, %rdi
    callq print_int
    movq %rbx, %rdi
    movq $1, %rsi
    callq soma
    movq %rax, %rcx
    movq %rcx, %rdi
    movq $3, %rsi
    callq escolhe
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq %rbx, %rdi
    callq positivo
    movq %rax, %rcx
    cmpq $0, %rcx
    je block7
    jmp block9

main_conclusion:
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 



