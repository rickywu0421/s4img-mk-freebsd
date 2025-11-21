#include <Uefi.h>
#include <Library/UefiLib.h>
#include <Library/UefiApplicationEntryPoint.h>
#include <Library/UefiBootServicesTableLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Protocol/LoadedImage.h>
#include <Protocol/SimpleFileSystem.h>
#include <Guid/FileInfo.h>

#include "elf64.h"

#define S4_IMAGE_NAME L"\\s4_image.bin"


EFI_STATUS
EFIAPI
UefiMain (
  IN EFI_HANDLE        ImageHandle,
  IN EFI_SYSTEM_TABLE  *SystemTable
  )
{
    EFI_STATUS                         Status;
    EFI_LOADED_IMAGE_PROTOCOL          *LoadedImage       = NULL;
    EFI_SIMPLE_FILE_SYSTEM_PROTOCOL    *FileSystem        = NULL;
    EFI_FILE_PROTOCOL                  *Root              = NULL;
    EFI_FILE_PROTOCOL                  *S4ImgFile         = NULL;
    Elf64_Ehdr                         Elf64Ehdr;
    UINT16                             PhdrNum;
    UINT16                             PhdrEntSize;
    UINT64                             PhdrOffset;
    Elf64_Phdr                         *Elf64PhdrTable    = NULL;
    UINTN                              ReadSize;

    Print(L"[Activator] Locate Protocols...\n");

    Status = gBS->HandleProtocol(
        ImageHandle,
        &gEfiLoadedImageProtocolGuid,
        (VOID **)&LoadedImage
    );

    if (EFI_ERROR(Status)) {
      Print(L"Error: Cannot get LoadedImage protocol: %r\n", Status);
      goto ErrorExit;
    }

    Status = gBS->HandleProtocol(
        LoadedImage->DeviceHandle,
        &gEfiSimpleFileSystemProtocolGuid,
        (VOID **)&FileSystem
    );

    if (EFI_ERROR(Status)) {
      Print(L"Error: Cannot get SimpleFileSystem protocol: %r\n", Status);
      goto ErrorExit;
    }

    Status = FileSystem->OpenVolume(FileSystem, &Root);

    if (EFI_ERROR(Status)) {
      Print(L"Error: OpenVolume failed: %r\n", Status);
      goto ErrorExit;
    }

    Print(L"[Activator] Open File %s...\n", S4_IMAGE_NAME);

    Status = Root->Open(
             Root,
             &S4ImgFile,
             S4_IMAGE_NAME,
             EFI_FILE_MODE_READ,
             0
             );

    if (EFI_ERROR(Status)) {
      Print(L"Error: OpenVolume failed: %r\n", Status);
      goto ErrorExit;
    }

    ReadSize = sizeof(Elf64_Ehdr);
    Status = S4ImgFile->Read(S4ImgFile, &ReadSize, &Elf64Ehdr);
    
    if (EFI_ERROR(Status)) {
      Print(L"Error: Read ELF64 header failed: %r\n", Status);
      goto ErrorExit;
    }

    Print(L"[Activator] Read File %s and Validate ELF header...\n", 
          S4_IMAGE_NAME);
    
    // Validate the ELF header of the S4 image
    if (((UINT8 *)&Elf64Ehdr)[EI_MAG0] != ELFMAG0 || 
        ((UINT8 *)&Elf64Ehdr)[EI_MAG1] != ELFMAG1 ||
        ((UINT8 *)&Elf64Ehdr)[EI_MAG2] != ELFMAG2 ||
        ((UINT8 *)&Elf64Ehdr)[EI_MAG3] != ELFMAG3) {
      Print(L"Error: File %s is not an ELF file\n", S4_IMAGE_NAME);
      goto ErrorExit;
    }

    if (((UINT8 *)&Elf64Ehdr)[EI_CLASS] != ELFCLASS64) {
      Print(L"Error: We only support 64-bits ELF files for now\n");
      goto ErrorExit;
    }

    if (((UINT8 *)&Elf64Ehdr)[EI_DATA] != ELFDATA2LSB) {
      Print(L"Error: We only support LSB ELF files for now\n");
      goto ErrorExit;
    }

    if (Elf64Ehdr.e_machine != EM_X86_64) {
      Print(L"Error: We only support x86_64 ELF files for now\n");
      goto ErrorExit;
    }


    // Allocate heap space for program headers table
    PhdrNum = Elf64Ehdr.e_phnum;
    PhdrEntSize = Elf64Ehdr.e_phentsize;
    PhdrOffset = Elf64Ehdr.e_phoff;

    Elf64PhdrTable = AllocatePool(PhdrNum * PhdrEntSize);
    if (Elf64PhdrTable == NULL) {
      Print(L"Error: Out of memory!\n");
      goto ErrorExit;
    }

    // Program headers table don't necessarily follow the ELF header.
    // So set the cursor for the sake.
    Status = S4ImgFile->SetPosition(S4ImgFile, PhdrOffset);
    if (EFI_ERROR(Status)) {
      Print(L"Error: Set position %d of file %s failed: %r\n", PhdrOffset, S4_IMAGE_NAME, Status);
      goto ErrorExit;
    }

    ReadSize = PhdrNum * PhdrEntSize;
    Status = S4ImgFile->Read(S4ImgFile, &ReadSize, (VOID *)Elf64PhdrTable);
    if (EFI_ERROR(Status)) {
      Print(L"Error: Read program headers table (size = %d) failed: %r\n", 
            PhdrNum * PhdrEntSize, Status);
      goto ErrorExit;
    }

    Print(L"[Activator] %d program headers in %s. Parse program headers...\n", 
          PhdrNum, S4_IMAGE_NAME);
    
    // Parse program headers
    for (UINT16 Num = 0; Num < PhdrNum; Num++) {
      Elf64_Phdr *CurrentPhdr = &Elf64PhdrTable[Num];

      EFI_PHYSICAL_ADDRESS PAddr = CurrentPhdr->p_paddr;

      switch (CurrentPhdr->p_type) {
        case PT_LOAD:
          UINTN FileSize = CurrentPhdr->p_filesz;
          UINTN MemSize = CurrentPhdr->p_memsz;
          UINTN SegmentOffset = CurrentPhdr->p_offset;
          UINTN Pages = EFI_SIZE_TO_PAGES(MemSize);

          Print(L"[Activator] Segment %d: PT_LOAD segment\n", Num);
          Print(L"[Activator] Allocate %d pages for PT_LOAD segment at %lx...\n", Pages, PAddr);
          
          Status = gBS->AllocatePages(
                   AllocateAddress,
                   EfiLoaderData,
                   Pages,
                   &PAddr);
          if (EFI_ERROR(Status)) {
            Print(L"Error: Failed to allocate pages at 0x%lx: %r\n", CurrentPhdr->p_paddr, Status);
            goto ErrorExit;
          }

          Print(L"[Activator] Read PT_LOAD segment at file offset %d to %lx...\n", SegmentOffset, PAddr);

          Status = S4ImgFile->SetPosition(S4ImgFile, SegmentOffset);
          if (EFI_ERROR(Status)) {
            Print(L"Error: Set position %d of file %s failed: %r\n", SegmentOffset, S4_IMAGE_NAME, Status);
            goto ErrorExit;
          }

          Status = S4ImgFile->Read(S4ImgFile, &FileSize, (VOID *)PAddr);
          if (EFI_ERROR(Status)) {
            Print(L"Error: Read PT_LOAD segment (size = %d) to %lx failed: %r\n", 
                    FileSize, PAddr, Status);
            goto ErrorExit;
          }

          Print(L"[Activator] Successfully loaded PT_LOAD segment at file offset %d to %lx...\n", 
                SegmentOffset, PAddr);

          // TODO: If p_memsz > p_filesz, then we need to zero the extra memory space (may be BSS)

          break;
        case PT_FREEBSD_S4_PCB: 
          Print(L"[Activator] Segment %d: PT_FREEBSD_S4_PCB segment\n", Num);
          break;
        case PT_FREEBSD_S4_TRAMPOLINE: 
          Print(L"[Activator] Segment %d: PT_FREEBSD_S4_TRAMPOLINE segment\n", Num);
          break;
        default: 
          break;
      }
    }

ErrorExit:
    if (Elf64PhdrTable != NULL) {
        FreePool(Elf64PhdrTable);
    }
    if (S4ImgFile != NULL) {
        S4ImgFile->Close(S4ImgFile);
    }
    if (Root != NULL) {
        Root->Close(Root);
    }
    

    gST->ConIn->Reset(gST->ConIn, FALSE);
    EFI_INPUT_KEY Key;
    while (gST->ConIn->ReadKeyStroke(gST->ConIn, &Key) == EFI_NOT_READY);

    return Status;
}