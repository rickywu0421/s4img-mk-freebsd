#!/bin/sh

# ==============================================================================
# Configuration
# ==============================================================================

# We use $(pwd) assuming this script is run from the project root.
PROJECT_ROOT="$(pwd)"
PROJECT_PKG_DIR="${PROJECT_ROOT}/uefi"

# Offical EDK2 as a submodule in this project
EDK2_DIR="${PROJECT_PKG_DIR}/edk2"

# Output directory for the final binary.
OUTPUT_DIR="${PROJECT_ROOT}/bin"

TOOLCHAIN="GCC5"
export PYTHON_COMMAND=python3

echo "Using Toolchain Tag: $TOOLCHAIN"

# ==============================================================================
# OS Detection
# ==============================================================================

if [ "$(uname -s)" == "FreeBSD" ]; then
    echo "Detected OS: FreeBSD"

    COMPAT_DIR="${PROJECT_ROOT}/bin/compat"
    mkdir -p "$COMPAT_DIR"

    # 1. Fix MAKE: shim 'make' to 'gmake'
    ln -sf /usr/local/bin/gmake "$COMPAT_DIR/make"
    
    # 2. Fix GCC Tools: Find the latest installed GCC version (e.g., gcc13)
    # This looks for /usr/local/bin/gcc[0-9]* and picks the last one
    GCC_PATH=$(ls /usr/local/bin/gcc[0-9]* 2>/dev/null | sort -V | tail -n 1)
    
    if [ -z "$GCC_PATH" ]; then
        echo "Error: GCC not found. Please run 'pkg install gcc'."
        exit 1
    fi
    
    # Extract version suffix (e.g., "13" from "gcc13")
    GCC_NAME=$(basename "$GCC_PATH")
    VER_SUFFIX=${GCC_NAME#gcc}
    
    echo "  -> Found GCC version: $GCC_NAME (suffix: $VER_SUFFIX)"
    
    # Create symlinks for all GCC toolchain binaries
    ln -sf "$GCC_PATH"                         "$COMPAT_DIR/gcc"
    ln -sf "/usr/local/bin/g++$VER_SUFFIX"     "$COMPAT_DIR/g++"
    ln -sf "/usr/local/bin/gcc-ar$VER_SUFFIX"  "$COMPAT_DIR/gcc-ar"
    ln -sf "/usr/local/bin/gcc-nm$VER_SUFFIX"  "$COMPAT_DIR/gcc-nm"
    ln -sf "/usr/local/bin/gcc-ranlib$VER_SUFFIX" "$COMPAT_DIR/gcc-ranlib"

    # 4. Inject compat dir to PATH
    export PATH="$COMPAT_DIR:$PATH"
    echo "  -> Toolchain shims active in $COMPAT_DIR"
else
    echo "Detected OS: Linux"
    export MAKE="make"
fi

# ==============================================================================
# Pre-flight Checks
# ==============================================================================

if [ ! -d "$EDK2_DIR" ]; then
    echo "Error: EDK2 directory not found at: $EDK2_DIR"
    echo "Please ensure EDK2 is cloned and configured correctly."
    exit 1
fi

# Check if BaseTools are compiled
if [ ! -f "$EDK2_DIR/BaseTools/Source/C/bin/GenFw" ]; then
    echo "Error: EDK2 BaseTools are not compiled."
    echo "Please compile them first:"
    if [ "$(uname -s)" == "FreeBSD" ]; then
        echo "  gmake -C uefi/edk2/BaseTools"
    else
        echo "  make -C uefi/edk2/BaseTools"
    fi
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
# Save current directory for later restoration (sh-compatible alternative to pushd)
SAVED_DIR="$(pwd)"
cd "$EDK2_DIR" || exit 1

# Force python3 for recent distributions (e.g., Arch Linux)
export PYTHON_COMMAND=python3

# Initialize the environment
. ./edksetup.sh

# ==============================================================================
# Build Process
# ==============================================================================

echo "Starting Build for S4ActivatorPkg..."

# build flags explanation:
# -p: Platform DSC file (relative to locations in PACKAGES_PATH)
# -a: Target Architecture (X64)
# -t: Toolchain Tag
# -b: Build Target (DEBUG or RELEASE)
build -p S4ActivatorPkg/S4ActivatorPkg.dsc \
      -a X64 \
      -t "$TOOLCHAIN" \
      -b DEBUG

# Return to saved directory (sh-compatible alternative to popd)
cd "$SAVED_DIR" || exit 1

# =====================================================================w=========
# Artifact Handling
# ==============================================================================

# Define the expected location of the generated binary.
# Note: The path includes the output directory defined in the DSC (Build/S4ActivatorPkg).
BUILD_RESULT="$EDK2_DIR/Build/S4ActivatorPkg/DEBUG_${TOOLCHAIN}/X64/Activator.efi"

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