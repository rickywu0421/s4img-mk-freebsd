#include <Uefi.h>
#include <Library/UefiLib.h>
#include <Library/UefiApplicationEntryPoint.h>
#include <Library/UefiBootServicesTableLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Protocol/LoadedImage.h>
#include <Protocol/SimpleFileSystem.h>
#include <Guid/FileInfo.h>

#define S4_IMAGE_NAME L"\\s4_image.bin"


EFI_STATUS
EFIAPI
UefiMain (
  IN EFI_HANDLE        ImageHandle,
  IN EFI_SYSTEM_TABLE  *SystemTable
  )
{
    EFI_STATUS                         Status;
    EFI_LOADED_IMAGE_PROTOCOL          *LoadedImage;
    EFI_SIMPLE_FILE_SYSTEM_PROTOCOL    *FileSystem;
    EFI_FILE_PROTOCOL                  *Root;
    EFI_FILE_PROTOCOL                  *S4ImgFile;
    UINTN                              S4ImgFileInfoSize;
    EFI_FILE_INFO                      *S4ImgFileInfo;
    UINTN                              S4ImgFileSize;
    VOID                               *S4ImgBuffer;

    Print(L"[Activator] Step 1: Locate Protocols...\n");

    Status = gBS->HandleProtocol(
        ImageHandle,
        &gEfiLoadedImageProtocolGuid,
        (VOID **)&LoadedImage
    );

    if (EFI_ERROR(Status)) {
      Print(L"Error: Cannot get LoadedImage protocol: %r\n", Status);
      return Status;
    }

    Status = gBS->HandleProtocol(
        LoadedImage->DeviceHandle,
        &gEfiSimpleFileSystemProtocolGuid,
        (VOID **)&FileSystem
    );

    if (EFI_ERROR(Status)) {
      Print(L"Error: Cannot get SimpleFileSystem protocol: %r\n", Status);
      return Status;
    }

    Status = FileSystem->OpenVolume(FileSystem, &Root);

    if (EFI_ERROR(Status)) {
      Print(L"Error: OpenVolume failed: %r\n", Status);
      return Status;
    }

    Print(L"[Activator] Step 2: Open File %s...\n", S4_IMAGE_NAME);

    Status = Root->Open(
             Root,
             &S4ImgFile,
             S4_IMAGE_NAME,
             EFI_FILE_MODE_READ,
             0
             );

    if (EFI_ERROR(Status)) {
      Print(L"Error: OpenVolume failed: %r\n", Status);
      return Status;
    }

    S4ImgFileInfoSize = 0;
    S4ImgFileInfo = NULL;

    Status = S4ImgFile->GetInfo(
             S4ImgFile,
             &gEfiFileInfoGuid,
             &S4ImgFileInfoSize,
             S4ImgFileInfo
             );

    if (Status == EFI_BUFFER_TOO_SMALL) {
      S4ImgFileInfo = AllocatePool(S4ImgFileInfoSize);
      Status = S4ImgFile->GetInfo(
             S4ImgFile,
             &gEfiFileInfoGuid,
             &S4ImgFileInfoSize,
             S4ImgFileInfo
             );
    }

    if (EFI_ERROR(Status)) {
      Print(L"Error: Cannot get file info: %r\n", Status);
      return Status;
    }

    S4ImgFileSize = S4ImgFileInfo->FileSize;
    Print(L"[Activator] File Size: %lu bytes\n", S4ImgFileSize);
    FreePool(S4ImgFileInfo);


    S4ImgBuffer = AllocatePool(S4ImgFileSize);
    if (S4ImgBuffer == NULL) {
      Print(L"Error: Out of memory!\n");
      return EFI_OUT_OF_RESOURCES;
    }

    Status = S4ImgFile->Read(S4ImgFile, &S4ImgFileSize, S4ImgBuffer);
    if (EFI_ERROR(Status)) {
      Print(L"Error: Read file failed: %r\n", Status);
      return Status;
    }

    Print(L"[Activator] Read Success! First 4 bytes: %02X %02X %02X %02X\n",
        ((UINT8*)S4ImgBuffer)[0], ((UINT8*)S4ImgBuffer)[1],
        ((UINT8*)S4ImgBuffer)[2], ((UINT8*)S4ImgBuffer)[3]);

    // We'll start parsing the S4 image in the following commits.
    // For now, let's do clean up and call it a day :)
    FreePool(S4ImgBuffer);
    S4ImgFile->Close(S4ImgFile);
    Root->Close(Root);

    Print(L"Phase 1 Complete. Press any key to exit...\n");

    gST->ConIn->Reset(gST->ConIn, FALSE);
    EFI_INPUT_KEY Key;
    while (gST->ConIn->ReadKeyStroke(gST->ConIn, &Key) == EFI_NOT_READY);

    return EFI_SUCCESS;
}