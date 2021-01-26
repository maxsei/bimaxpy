import cffi
import os
from pathlib import Path
import pycparser
import requests
import json
import tarfile
import io
from pathlib import Path


def main():
    # Architechture and OS name parsing
    goarch = os.uname().machine
    if goarch == "x86_64":
        goarch = "amd64"
    goos = os.uname().sysname.lower()

    # Paths the tar should be extracted to
    base = Path(f"releases/{goos}_{goarch}")
    header_filename = base.joinpath("libbimax.h")

    # If we don't have the package download the release
    if not base.exists:
        # Request release of Architechture and OS
        url = f"https://github.com/maxsei/bimax/releases/download/v0.0.1/{goos}_{goarch}.tar.gz"
        resp = requests.get(url)
        if not resp.ok:
            raise Exception(
                f"could not find release for os: {goos} arch: {goarch} at {url}"
            )
        # Read in the content of the request and extract tar
        buf = io.BytesIO(resp.content)
        archive = tarfile.open(fileobj=buf)
        archive.extractall()

    # Preprocess header file
    pp = pycparser.preprocess_file(
        str(header_filename),
        cpp_path="gcc",
        cpp_args=[
            "-E",
            "-x",
            "c",
            "-std=c99",
        ],
    )
    # pycparser.c_ast.Compound
    # ast = pycparser.c_parser.CParser().parse(pp)

    # TODO: simply commenting out the void pointer compile time check that go
    # does for now but the future would be cool to do static simplification of
    # the ast in the header file i.e. replacing int[2 + 2] with int[4]<25-01-21, Max Schulte> #

    pp = "\n".join(
        filter(
            lambda x: "_check_for_64_bit_pointer_matching_GoInt" not in x,
            pp.split("\n"),
        )
    )

    # Build and compile cffi library with included headers and shared objects
    ffi = cffi.FFI()
    ffi.cdef(pp)
    print(str(base))
    ffi.set_source(
        "bimaxpy._bimax",
        f'#include "{header_filename.absolute()}"',
        library_dirs=[str(base.absolute())],
        libraries=["bimax"],
        extra_link_args=[f"-Wl,-rpath={base.absolute()}"],
    )
    ffi.compile(verbose=True)


if __name__ == "__main__":
    main()
