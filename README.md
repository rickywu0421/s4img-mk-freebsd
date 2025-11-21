# freebsd-s4-tools

A toolkit to fabricate FreeBSD S4 hibernate images (ELF format) and a UEFI Activator for resume testing.

This project consists of two main components:
1.  **Generator:** Python scripts to create a valid ELF64 image containing `PT_FREEBSD_S4_PCB` and `PT_FREEBSD_S4_TRAMPOLINE` headers.
2.  **Activator:** An EDK2-based UEFI application to load the image and restore context.

## Current Status

* [x] **S4 Image Generation:** Functional (Python).
* [x] **UEFI Build System:** Out-of-tree EDK2 build scripts ready.
* [x] **Activator (Phase 1):** Successfully reads `s4_image.bin` from the EFI System Partition.
* [ ] **Activator (Phase 2):** **(WIP)** Parsing ELF/S4 headers and allocating physical memory.
* [ ] **Activator (Phase 3):** Context restoration and trampoline jump.

## Requirements

* Python 3.11+ (Required for `tomllib`)
* EDK2 Build Tools & QEMU (for UEFI development)

## Project Structure

* `generator/`: Python scripts and configuration for fabricating S4 images.
* `uefi/`: EDK2 Package source code (`S4ActivatorPkg`) for the bootloader/activator.
* `scripts/`: Helper scripts for building UEFI apps and running QEMU.
* `bin/`: Directory for build artifacts (`Activator.efi`, `s4_image.bin`) and test environment.

## Usage

The workflow involves generating a fake image, building the UEFI activator, and running the simulation.

### 1. Fabricate S4 Image
Prepare your configuration and run the generator:

```bash
python3 generator/main.py \
    generator/layout/example.toml \
    generator/trampoline/hello_world.bin
```

### 2. Build UEFI Activator
Compile the EDK2 application using the helper script:

```bash
./scripts/build_uefi.sh
```

### 3. Run Simulation
Launch QEMU with OVMF. The script automatically mounts `bin/esp/` as the boot partition.

```bash
./scripts/run_qemu.sh
```

## Configuration
Modify `generator/layout/example.toml` to define:

* ELF Layout: p_paddr, p_vaddr, and alignment for segments.

* Context State: Initial values for cr3, rsp, rip in the PCB.