	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    jmp main_start

	.align 16
even:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp even_start

block1:
    movq $0, %rax
    jmp even_conclusion

block2:
    movq $1, %rax
    jmp even_conclusion

block3:
    subq $1, %rcx
    movq %rcx, %rdi
    callq odd
    movq %rax, %rcx
    movq %rcx, %rax
    jmp even_conclusion

even_start:
    movq %rdi, %rcx
    cmpq $0, %rcx
    je block2
    jmp block3

even_conclusion:
    addq $0, %rsp
    popq %rbp
    retq 

	.align 16
odd:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    jmp odd_start

block4:
    movq $0, %rax
    jmp odd_conclusion

block5:
    movq $0, %rax
    jmp odd_conclusion

block6:
    subq $1, %rcx
    movq %rcx, %rdi
    callq even
    movq %rax, %rcx
    movq %rcx, %rax
    jmp odd_conclusion

odd_start:
    movq %rdi, %rcx
    cmpq $0, %rcx
    je block5
    jmp block6

odd_conclusion:
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
    movq $0, %rdi
    callq print_int
    jmp block7

block10:
    movq %rbx, %rdi
    callq odd
    movq %rax, %rcx
    cmpq $0, %rcx
    je block8
    jmp block9

main_start:
    callq input_int
    movq %rax, %rbx
    movq %rbx, %rdi
    callq even
    movq %rax, %rcx
    cmpq $0, %rcx
    je block9
    jmp block10

main_conclusion:
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 



