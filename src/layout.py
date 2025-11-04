import struct
from dataclasses import dataclass
from typing import List

from .constants import *

@dataclass
class Elf64Ehdr:
    _FORMAT = "<16sHHIQQQIHHHHHH"

    e_ident:     bytearray
    e_etype:     uint16_t
    e_machine:   uint16_t
    e_version:   uint32_t
    e_entry:     uint64_t
    e_phoff:     uint64_t
    e_shoff:     uint64_t
    e_flags:     uint32_t
    e_ehsize:    uint16_t
    e_phentsize: uint16_t
    e_phnum:     uint16_t
    e_shentsize: uint16_t
    e_shnum:     uint16_t
    e_shstrndx:  uint16_t

    @classmethod
    def size(cls):
        return struct.calcsize(cls._FORMAT)

    def __str__(self):
        return (
            "Elf Header:\n"
            f"  e_ident:     0x{self.e_ident.hex()}\n"
            f"  e_etype:     0x{self.e_etype:04x}\n"
            f"  e_machine:   0x{self.e_machine:04x}\n"
            f"  e_version:   0x{self.e_version:08x}\n"
            f"  e_entry:     0x{self.e_entry:016x}\n"
            f"  e_phoff:     0x{self.e_phoff:016x}\n"
            f"  e_shoff:     0x{self.e_shoff:016x}\n"
            f"  e_flags:     0x{self.e_flags:08x}\n"
            f"  e_ehsize:    0x{self.e_ehsize:04x}\n"
            f"  e_phentsize: 0x{self.e_phentsize:04x}\n"
            f"  e_phnum:     0x{self.e_phnum:04x}\n"
            f"  e_shentsize: 0x{self.e_shentsize:04x}\n"
            f"  e_shnum:     0x{self.e_shnum:04x}\n"
            f"  e_shstrndx:  0x{self.e_shstrndx:04x}"
        )
    
    def pack(self):
        return struct.pack(
            self._FORMAT,
            self.e_ident,
            self.e_etype,
            self.e_machine,
            self.e_version,
            self.e_entry,
            self.e_phoff,
            self.e_shoff,
            self.e_flags,
            self.e_ehsize,
            self.e_phentsize,
            self.e_phnum,
            self.e_shentsize,
            self.e_shnum,
            self.e_shstrndx,
        )



@dataclass
class Elf64Phdr:
    _FORMAT = "<IIQQQQQQ"

    p_type:   uint32_t
    p_flags:  uint32_t
    p_offset: uint64_t
    p_vaddr:  uint64_t
    p_paddr:  uint64_t
    p_filesz: uint64_t
    p_memsz:  uint64_t
    p_align:  uint64_t

    @classmethod
    def size(cls):
        return struct.calcsize(cls._FORMAT)

    def __str__(self):
        return (
            "=== Elf64Phdr ===\n"
            f"  p_type:   0x{self.p_type:08x}\n"
            f"  p_flags:  0x{self.p_flags:08x}\n"
            f"  p_offset: 0x{self.p_offset:016x}\n"
            f"  p_vaddr:  0x{self.p_vaddr:016x}\n"
            f"  p_paddr:  0x{self.p_paddr:016x}\n"
            f"  p_filesz: 0x{self.p_filesz:016x}\n"
            f"  p_memsz:  0x{self.p_memsz:016x}\n"
            f"  p_align:  0x{self.p_align:016x}"
        )

    def pack(self):
        return struct.pack(
            self._FORMAT,
            self.p_type,
            self.p_flags,
            self.p_offset,
            self.p_vaddr,
            self.p_paddr,
            self.p_filesz,
            self.p_memsz,
            self.p_align,
        )
    

@dataclass
class S4Pcb:
    _FORMAT = "<QQQQQQI"

    cr0:              uint64_t
    cr3:              uint64_t
    cr4:              uint64_t
    rsp:              uint64_t
    rip:              uint64_t
    gsbase:           uint64_t
    acpic_facs_hwsig: uint32_t

    @classmethod
    def size(cls):
        return struct.calcsize(cls._FORMAT)

    def __str__(self):
        return (
            "=== S4Pcb ===\n"
            f"  cr0:              0x{self.cr0:016x}\n"
            f"  cr3:              0x{self.cr3:016x}\n"
            f"  cr4:              0x{self.cr4:016x}\n"
            f"  rsp:              0x{self.rsp:016x}\n"
            f"  rip:              0x{self.rip:016x}\n"
            f"  gsbase:           0x{self.gsbase:016x}\n"
            f"  acpic_facs_hwsig: 0x{self.acpic_facs_hwsig:08x}"
        )
    
    def pack(self):
        return struct.pack(
            self._FORMAT,
            self.cr0,
            self.cr3,
            self.cr4,
            self.rsp,
            self.rip,
            self.gsbase,
            self.acpic_facs_hwsig,
        )


def create_elf64_header_from_toml(config: dict) -> Elf64Ehdr:
    elf_hdr_cfg = config['elf_header']
    
    e_ident = bytearray(E_IDENT.EI_NIDENT)

    e_ident[E_IDENT.EI_MAG0]       = elf_hdr_cfg['e_ident']['EI_MAG0']
    e_ident[E_IDENT.EI_MAG1]       = elf_hdr_cfg['e_ident']['EI_MAG1']
    e_ident[E_IDENT.EI_MAG2]       = elf_hdr_cfg['e_ident']['EI_MAG2']
    e_ident[E_IDENT.EI_MAG3]       = elf_hdr_cfg['e_ident']['EI_MAG3']
    e_ident[E_IDENT.EI_CLASS]      = elf_hdr_cfg['e_ident']['EI_CLASS']
    e_ident[E_IDENT.EI_DATA]       = elf_hdr_cfg['e_ident']['EI_DATA']
    e_ident[E_IDENT.EI_VERSION]    = elf_hdr_cfg['e_ident']['EI_VERSION']
    e_ident[E_IDENT.EI_OSABI]      = elf_hdr_cfg['e_ident']['EI_OSABI']
    e_ident[E_IDENT.EI_ABIVERSION] = elf_hdr_cfg['e_ident']['EI_ABIVERSION']
    # Padding bytes
    e_ident[E_IDENT.EI_PAD:E_IDENT.EI_NIDENT] = bytes(
        E_IDENT.EI_NIDENT - E_IDENT.EI_PAD
    )

    ehdr = Elf64Ehdr(
        e_ident     = e_ident,
        e_etype     = elf_hdr_cfg['e_etype'],
        e_machine   = elf_hdr_cfg['e_machine'],
        e_version   = elf_hdr_cfg['e_version'],
        e_entry     = elf_hdr_cfg['e_entry'],
        e_phoff     = elf_hdr_cfg['e_phoff'],
        e_shoff     = elf_hdr_cfg['e_shoff'],
        e_flags     = elf_hdr_cfg['e_flags'],
        e_ehsize    = elf_hdr_cfg['e_ehsize'],
        e_phentsize = elf_hdr_cfg['e_phentsize'],
        e_phnum     = elf_hdr_cfg['e_phnum'],
        e_shentsize = elf_hdr_cfg['e_shentsize'],
        e_shnum     = elf_hdr_cfg['e_shnum'],
        e_shstrndx  = elf_hdr_cfg['e_shstrndx'],
    )

    return ehdr


def create_program_headers_from_toml(config: dict) -> List[Elf64Phdr]:
    phdrs = []

    for phdr_cfg in config['program_header']:
        phdr = Elf64Phdr(
            p_type   = phdr_cfg['p_type'],
            p_flags  = phdr_cfg['p_flags'],
            p_offset = phdr_cfg['p_offset'],
            p_vaddr  = phdr_cfg['p_vaddr'],
            p_paddr  = phdr_cfg['p_paddr'],
            p_filesz = phdr_cfg['p_filesz'],
            p_memsz  = phdr_cfg['p_memsz'],
            p_align  = phdr_cfg['p_align'],
        )
        phdrs.append(phdr)

    return phdrs


def create_pcb_data_from_toml(config: dict) -> S4Pcb:
    pcb_cfg = config['pcb_data']

    pcb = S4Pcb(
        cr0              = pcb_cfg['cr0'],
        cr3              = pcb_cfg['cr3'],
        cr4              = pcb_cfg['cr4'],
        rsp              = pcb_cfg['rsp'],
        rip              = pcb_cfg['rip'],
        gsbase           = pcb_cfg['gsbase'],
        acpic_facs_hwsig = pcb_cfg['acpic_facs_hwsig'],
    )

    return pcb
