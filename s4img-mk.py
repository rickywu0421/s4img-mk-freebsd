import os
import sys
from src.builder import S4ImgBuilder

def usage():
    print("python3 s4img-mk.py <toml path> <trampoline path> <output path>")
    
def main():
    if len(sys.argv) > 3:
        toml_path = sys.argv[1]
        trampoline_path = sys.argv[2]
        output_path = sys.argv[3]
    else:
        usage()
        sys.exit(1)

    S4ImgBuilder().make_image_from_toml(toml_path, trampoline_path, output_path)



if __name__ == "__main__":
    main()
    