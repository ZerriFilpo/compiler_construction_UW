	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp main_start

	.align 16
sign:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp sign_start

block1:
    movq $1, %rcx
    negq %rcx
    movq %rcx, %rax
    jmp sign_conclusion

block2:
    movq $0, %rax
    jmp sign_conclusion

block3:
    movq $1, %rax
    jmp sign_conclusion

block4:
    cmpq $0, %rcx
    jl block1
    jmp block2

sign_start:
    movq %rdi, %rcx
    cmpq $0, %rcx
    jg block3
    jmp block4

sign_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

	.align 16
maxim:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp maxim_start

block5:
    movq %rdx, %rax
    jmp maxim_conclusion

block6:
    movq %rcx, %rax
    jmp maxim_conclusion

maxim_start:
    movq %rdi, %rcx
    movq %rsi, %rdx
    cmpq %rdx, %rcx
    jg block6
    jmp block5

maxim_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

	.align 16
noret:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp noret_start

noret_start:
    movq %rdi, %rcx
    addq $1, %rcx
    movq $0, %rax
    jmp noret_conclusion

noret_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

main_start:
    movq $5, %rdi
    callq sign
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $5, %rcx
    negq %rcx
    movq %rcx, %rdi
    callq sign
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $0, %rdi
    callq sign
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $3, %rdi
    movq $7, %rsi
    callq maxim
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $9, %rdi
    movq $2, %rsi
    callq maxim
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $4, %rdi
    callq noret
    movq $100, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

main_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 



