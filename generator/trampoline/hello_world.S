.code64
.section .text
.global _start
.intel_syntax noprefix

_start:
    cli

    // ---- Print 'H' -----
    mov dx, 0x3f8 // COM1 Port Address
    mov al, 'H'
    out dx, al

    // ---- Print 'i' -----
    mov dx, 0x3f8 // COM1 Port Address
    mov al, 'i'
    out dx, al

    // ---- Print 'l' -----
    mov dx, 0x3f8 // COM1 Port Address
    mov al, 10
    out dx, al

hang:
    jmp hang