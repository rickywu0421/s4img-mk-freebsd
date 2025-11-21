#!/bin/bash

# ==============================================================================
# Configuration
# ==============================================================================

# Path to the official EDK2 source tree.
# Adjust this path if your EDK2 workspace is located elsewhere.
EDK2_DIR="$HOME/software/edk2"

# We use $(pwd) assuming this script is run from the project root.
PROJECT_ROOT="$(pwd)"
PROJECT_PKG_DIR="${PROJECT_ROOT}/uefi"

# Output directory for the final binary.
OUTPUT_DIR="${PROJECT_ROOT}/bin"

# ==============================================================================
# Pre-flight Checks
# ==============================================================================

if [ ! -d "$EDK2_DIR" ]; then
    echo "Error: EDK2 directory not found at: $EDK2_DIR"
    echo "Please ensure EDK2 is cloned and configured correctly."
    exit 1
fi

if [ ! -d "$PROJECT_PKG_DIR/S4ActivatorPkg" ]; then
    echo "Error: S4ActivatorPkg not found at: $PROJECT_PKG_DIR/S4ActivatorPkg"
    echo "Make sure you are running this script from the project root."
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# ==============================================================================
# Environment Setup
# ==============================================================================

# Critical Step: PACKAGES_PATH
# This tells the EDK2 build system where to look for packages.
# We prepend our custom package directory so the build tool finds 'S4ActivatorPkg'.
# Format: /path/to/our/pkg:/path/to/edk2/pkg
export PACKAGES_PATH="$PROJECT_PKG_DIR:$EDK2_DIR"

echo "========================================"
echo "Setting up EDK2 Build Environment"
echo "PACKAGES_PATH: $PACKAGES_PATH"
echo "========================================"

# We need to switch to the EDK2 directory to source the setup script correctly.
# This initializes 'build', 'GenFds', and other build tools in the PATH.
pushd "$EDK2_DIR" > /dev/null

# Force python3 for recent distributions (e.g., Arch Linux)
export PYTHON_COMMAND=python3

# Initialize the environment
. edksetup.sh

# ==============================================================================
# Build Process
# ==============================================================================

echo "Starting Build for S4ActivatorPkg..."

# build flags explanation:
# -p: Platform DSC file (relative to locations in PACKAGES_PATH)
# -a: Target Architecture (X64)
# -t: Toolchain Tag (GCC5 is standard for modern Linux)
# -b: Build Target (DEBUG or RELEASE)
build -p S4ActivatorPkg/S4ActivatorPkg.dsc \
      -a X64 \
      -t GCC5 \
      -b DEBUG

popd > /dev/null

# ==============================================================================
# Artifact Handling
# ==============================================================================

# Define the expected location of the generated binary.
# Note: The path includes the output directory defined in the DSC (Build/S4ActivatorPkg).
BUILD_RESULT="$EDK2_DIR/Build/S4ActivatorPkg/DEBUG_GCC5/X64/Activator.efi"

if [ -f "$BUILD_RESULT" ]; then
    echo "========================================"
    echo "Build Success!"
    cp "$BUILD_RESULT" "$OUTPUT_DIR/Activator.efi"
    echo "Artifact copied to: $OUTPUT_DIR/Activator.efi"
    echo "========================================"
else
    echo "Error: Build command finished but binary not found at expected path:"
    echo "$BUILD_RESULT"
    exit 1
fi