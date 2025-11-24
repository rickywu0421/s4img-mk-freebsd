.code64
.section .text
.global _start

_start:
    cli

hang:
    jmp hang