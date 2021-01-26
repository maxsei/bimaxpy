import _bimax
import numpy as np
from typing import Tuple


def BimaxBinaryMatrix(arr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    arr = arr.astype(np.uint8)
    result = _bimax.lib.BiMaxBinaryMatrixC(*arr.shape, arr.tobytes())
    return _result_to_arrs(result)


def BiMaxVertices(uu: np.ndarray, vv: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    result = _bimax.lib.BiMaxVerticesC(len(uu), uu.tolist(), len(vv), vv.tolist())
    return _result_to_arrs(result)


def _result_to_arrs(result) -> Tuple[np.ndarray, np.ndarray]:
    rows = _length_and_dataptr_to_arr(result.r0, result.r1)
    cols = _length_and_dataptr_to_arr(result.r2, result.r3)
    return rows, cols


def _length_and_dataptr_to_arr(length, dataptr) -> np.ndarray:
    buf = _bimax.ffi.buffer(dataptr[0:length])
    size = _bimax.ffi.sizeof(dataptr)
    dtype = _bimax.ffi.typeof(dataptr).item.cname.replace(" ", "")
    return np.frombuffer(buf[:], dtype=dtype)


def main():
    mat = np.array(
        [
            [0, 0, 1, 0],
            [1, 1, 1, 0],
            [0, 1, 0, 1],
            [1, 1, 0, 0],
        ],
        dtype=np.uint8,
    )
    print(BimaxBinaryMatrix(mat))

    uu = np.array([0, 1, 1, 1, 2, 2, 3, 3], dtype=np.int64)
    vv = np.array([6, 4, 5, 6, 5, 7, 4, 5], dtype=np.int64)
    print(BiMaxVertices(uu, vv))


if __name__ == "__main__":
    main()
