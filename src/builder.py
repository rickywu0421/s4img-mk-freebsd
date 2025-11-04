import sys
from typing import List
import tomllib

from .constants import *
from .layout import *
from .utils import *

class S4ImgBuilder:
    def __init__(self):
        pass

    def load_toml_config(self, toml_path: str) -> dict:
        try:
            with open(toml_path, 'rb') as f:
                config = tomllib.load(f)
        except OSError as e:
            print(f"Error: Failed to read TOML file: {e}", file=sys.stderr)
            sys.exit(1)
        
        return config



    def make_image_from_toml(self, toml_path: str, trampoline_path: str,
                             output_path: str):
        # Load TOML configuration
        config = self.load_toml_config(toml_path)

        # Create headers from TOML
        elf64_header = create_elf64_header_from_toml(config)
        program_headers = create_program_headers_from_toml(config)
        pcb_data = create_pcb_data_from_toml(config)

        # Identify program headers by type
        pt_load_hdrs = []
        pcb_hdr = None
        trampoline_hdr = None

        for phdr in program_headers:
            if phdr.p_type == P_TYPE.PT_LOAD:
                pt_load_hdrs.append(phdr)
            elif phdr.p_type == P_TYPE.PT_FREEBSD_S4_PCB:
                pcb_hdr = phdr
            elif phdr.p_type == P_TYPE.PT_FREEBSD_S4_TRAMPOLINE:
                trampoline_hdr = phdr

        # Validate required headers
        if len(pt_load_hdrs) == 0:
            print("Error: PT_LOAD header not found in TOML configuration", file=sys.stderr)
            sys.exit(1)
        if pcb_hdr is None:
            print("Error: PT_FREEBSD_S4_PCB header not found in TOML configuration", file=sys.stderr)
            sys.exit(1)
        if trampoline_hdr is None:
            print("Error: PT_FREEBSD_S4_TRAMPOLINE header not found in TOML configuration", file=sys.stderr)
            sys.exit(1)

        # Read trampoline data from file
        try:
            with open(trampoline_path, 'rb') as f:
                trampoline_data = f.read()
        except OSError as e:
            print(f"Error: Failed to read trampoline file: {e}", file=sys.stderr)
            sys.exit(1)

        # Overwrite p_filesz and p_memsz in PT_FREEBSD_S4_TRAMPOLINE
        trampoline_hdr.p_filesz = len(trampoline_data)
        trampoline_hdr.p_memsz = len(trampoline_data)

        # Build the image
        self._build_image(
            elf64_header=elf64_header,
            program_headers=program_headers,
            pt_load_hdrs=pt_load_hdrs,
            pcb_hdr=pcb_hdr,
            trampoline_hdr=trampoline_hdr,
            pcb_data=pcb_data,
            trampoline_data=trampoline_data,
            output_path=output_path
        )

    def _build_image(self,
                     elf64_header: Elf64Ehdr,
                     program_headers: List[Elf64Phdr],
                     pt_load_hdrs: List[Elf64Phdr],
                     pcb_hdr: Elf64Phdr,
                     trampoline_hdr: Elf64Phdr,
                     pcb_data: S4Pcb,
                     trampoline_data: bytes,
                     output_path: str):
        """Internal method to build the S4 image."""

        # Sort program headers by p_offset to ensure correct file layout
        program_headers.sort(key=lambda phdr: phdr.p_offset)

        # Print the headers with the same order defined in TOML
        print(elf64_header)
        print()

        for program_header in program_headers:
            print(program_header)
            print()

        print(pcb_data)
        print()


        ##
        # At this point, we have all the ELF header, program headers, and trampoline data.
        # Now we can assemble them.
        # TODO: We need to verify them
        ##
        blob = bytearray()

        """Fill in ELF header and program headers"""
        blob += elf64_header.pack()

        phdr_info_list = []
        for phdr in program_headers:
            blob += phdr.pack()
            phdr_info_list.append((phdr.p_type, phdr.p_offset, phdr.p_filesz))



        """Fill in segments"""
        for p_type, p_offset, p_size in phdr_info_list:
            if p_type == P_TYPE.PT_LOAD:
                # Padding before the segment
                blob += bytearray(p_offset - len(blob))
                
                # Content of the segment
                blob += bytearray([PT_LOAD_DEFAULT_CONTENT] * p_size)
            elif p_type == P_TYPE.PT_FREEBSD_S4_PCB:
                # Padding before the segment
                blob += bytearray(p_offset - len(blob))
                
                # Content of the segment
                blob += pcb_data.pack()
            # We fill in trampoline data later
            else:
                continue

        """Fill in trampoline (overwrite a specific PT_LOAD portion)"""
        trampoline_offset = trampoline_hdr.p_offset
        trampoline_size = len(trampoline_data)
        blob[trampoline_offset:trampoline_offset+trampoline_size] = trampoline_data

        try:
            with open(output_path, "wb") as f:
                f.write(blob)
        except OSError as e:
            print(f"Error: Failed to write S4 image: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"Successfully write S4 image into {output_path}")
