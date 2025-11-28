# freebsd-s4-tools

A toolkit to fabricate FreeBSD S4 hibernate images (ELF format) and a UEFI Activator for resume testing.

This project consists of two main components:
1.  **Generator:** Python scripts to create a valid ELF64 image containing `PT_FREEBSD_S4_PCB` and `PT_FREEBSD_S4_TRAMPOLINE` headers.
2.  **Activator:** An EDK2-based UEFI application to load the image and restore context.

## Current Status

* [x] **S4 Image Generation:** Functional (Python).
* [x] **UEFI Build System:** Out-of-tree EDK2 build scripts ready.
* [x] **Activator (Phase 1):** Successfully reads `s4_image.bin` from the EFI System Partition.
* [x] **Activator (Phase 2):** Parsing ELF/S4 headers and allocating physical memory.
* [x] **Activator (Phase 3):** Context restoration and trampoline jump.

## Prerequisites & Installationres
Before cloning, ensure you have the necessary system packages installed.

### Arch Linux
Requires `base-devel` for build tools, plus QEMU and OVMF for testing.

```bash
pacman -S base-devel git python nasm gcc make qemu-full edk2-ovmf
```

### FreeBSD
Requires `gcc` and `binutils` (for EDK2 GCC5 toolchain compatibility), `gmake`, and virtualization tools.

#### Option 1: Using Binary Packages (Recommended)
```bash
pkg install git bash python gcc binutils gmake nasm edk2-bhyve mtools
```
Note: mtools is used for creating FAT disk images for Bhyve testing.

#### Option 2: Using Ports Collection
If you need to customize build options, you can install these tools via the Ports Collection (e.g., `/usr/ports/devel/git`, `/usr/ports/lang/python3`, etc.).

## Project Structure

* `generator/`: Python scripts and configuration for fabricating S4 images.
* `uefi/`: Contains the `S4ActivatorPkg` source and the **EDK2 submodule**.
* `scripts/`: Helper scripts for building UEFI apps and running QEMU.
* `bin/`: Directory for build artifacts (`Activator.efi`, `s4_image.bin`) and test environment.

## Initialization (One-time Setup)

This repository vendors EDK2 as a git submodule. You must clone the repository recursively and compile the build tools before use.

### 1. Clone the Repository
Use the `--recursive` flag to fetch the project, vendored EDK2 submodule, and submodules used in EDK2.

```bash
git clone --recursive https://github.com/rickywu0421/freebsd-s4-tools.git
cd freebsd-s4-tools
```
Note: If you have already cloned the repo without the recursive flag, run: `git submodule update --init --recursive`


### 2. Compile EDK2 BaseTools
The build tools (build, GenFds, etc.) need to be compiled for your host OS.

#### Arch Linux
Under the top directory of this repo, run:
```bash
make -C uefi/edk2/BaseTools
```

#### FreeBSD
Under the top directory of this repo, run:
```bash
gmake -C uefi/edk2/BaseTools
```

## Development Cycle
Once initialized, use the following workflow to generate images and test the loader.

### 1. Fabricate S4 Image

Prepare your configuration and run the generator:

```bash
python3 generator/main.py \
    generator/layout/example.toml \
    generator/trampoline/hello_world.bin
```

### 2. Build UEFI Activator

Compile the EDK2 application using the helper script. This script automatically handles the `PACKAGES_PATH` environment variables.

```bash
./scripts/build_uefi.sh
```

### 3. Run Simulation

#### Arch Linux

Launch QEMU with OVMF. The script automatically mounts `bin/esp/` as the boot partition and redirects the virtual serial port (COM1) to the terminal.

```
./scripts/run_qemu.sh
```

#### FreeBSD

Launch Bhyve with OVMF. The script automatically creates a FAT32 disk image containing the artifacts and redirects the virtual serial port (COM1) to the terminal.

```
sudo ./scripts/run_bhyve.sh
```

Note: Root privileges are required for Bhyve networking and device creation.

## Configuration
Modify `generator/layout/example.toml` to define:

ELF Layout: p_paddr, p_vaddr, and alignment for segments.

Context State: Initial values for cr3, rsp, rip in the PCB.