;------------------------------------------------------------------------------
; S4 Activator Trampoline (Thunk)
;------------------------------------------------------------------------------
DEFAULT REL
SECTION .text

global AsmTransferControl

;------------------------------------------------------------------------------
; void
; EFIAPI
; AsmTransferControl (
;   IN UINT64  EntryPoint,   // RCX (Arg1)
;   IN UINT64  Context       // RDX (Arg2) -> PCB Physical Address
;   );
;------------------------------------------------------------------------------

AsmTransferControl:
    ; Disable interrupt
    cli

    ; Conversion from UEFI to FreeBSD
    ; FreeBSD expects the first argument in RDI (System V calling convention)
    mov     RDI, RDX

    ; Jump to the FreeBSD S4 entry point (another trampoline)
    jmp     RCX

    ; Should never reach here
    ret