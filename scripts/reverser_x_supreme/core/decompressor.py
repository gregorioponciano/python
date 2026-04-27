import gzip
import zipfile
import bz2
import lzma
import zlib
import io
from typing import List, Tuple, Optional

from utils.constants import Colors
from utils.helpers import calculate_entropy, is_printable


class DecompressorEngine:
    MAGIC_GZIP = b'\x1f\x8b'
    MAGIC_ZIP = b'PK\x03\x04'
    MAGIC_BZ2 = b'BZ'
    MAGIC_LZMA = b'\xfd7zXZ\x00'
    MAGIC_ZLIB_WINDOW = 15

    def __init__(self, config=None):
        self.config = config or {}
        self.max_decompressed_size = self.config.get("max_decompressed_size", 100 * 1024 * 1024)

    def decompress_gzip(self, data: bytes) -> Optional[bytes]:
        try:
            if len(data) < 2 or data[:2] != self.MAGIC_GZIP:
                try:
                    return gzip.decompress(data)
                except Exception:
                    return None
            result = gzip.decompress(data)
            if len(result) > self.max_decompressed_size:
                return None
            return result
        except Exception:
            return None

    def decompress_zip(self, data: bytes) -> List[Tuple[str, bytes]]:
        results = []
        try:
            if len(data) < 4 or data[:4] != self.MAGIC_ZIP:
                if b'PK' not in data[:4]:
                    return results
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                bad_file = zf.testzip()
                if bad_file is not None:
                    return results
                for info in zf.infolist():
                    if info.is_dir():
                        continue
                    if info.file_size > self.max_decompressed_size:
                        continue
                    try:
                        file_data = zf.read(info.filename)
                        results.append((info.filename, file_data))
                    except Exception:
                        continue
        except Exception:
            return results
        return results

    def decompress_bz2(self, data: bytes) -> Optional[bytes]:
        try:
            if len(data) < 2 or data[:2] != self.MAGIC_BZ2:
                try:
                    return bz2.decompress(data)
                except Exception:
                    return None
            result = bz2.decompress(data)
            if len(result) > self.max_decompressed_size:
                return None
            return result
        except Exception:
            return None

    def decompress_lzma(self, data: bytes) -> Optional[bytes]:
        try:
            if len(data) < 6 or data[:6] != self.MAGIC_LZMA:
                try:
                    return lzma.decompress(data)
                except Exception:
                    return None
            result = lzma.decompress(data)
            if len(result) > self.max_decompressed_size:
                return None
            return result
        except Exception:
            return None

    def decompress_zlib(self, data: bytes) -> Optional[bytes]:
        try:
            try:
                result = zlib.decompress(data)
            except zlib.error:
                try:
                    result = zlib.decompress(data, -self.MAGIC_ZLIB_WINDOW)
                except zlib.error:
                    try:
                        result = zlib.decompress(data, self.MAGIC_ZLIB_WINDOW | 32)
                    except zlib.error:
                        return None
            if len(result) > self.max_decompressed_size:
                return None
            return result
        except Exception:
            return None

    def decompress_all(self, data: bytes) -> List[Tuple[str, bytes]]:
        results = []
        gzip_result = self.decompress_gzip(data)
        if gzip_result is not None:
            results.append(("gzip", gzip_result))
        zip_result = self.decompress_zip(data)
        if zip_result:
            for name, content in zip_result:
                results.append((f"zip:{name}", content))
        bz2_result = self.decompress_bz2(data)
        if bz2_result is not None:
            results.append(("bz2", bz2_result))
        lzma_result = self.decompress_lzma(data)
        if lzma_result is not None:
            results.append(("lzma", lzma_result))
        zlib_result = self.decompress_zlib(data)
        if zlib_result is not None:
            results.append(("zlib", zlib_result))
        return results

    def detect_compression(self, data: bytes) -> str:
        if len(data) < 2:
            return "unknown"
        if data[:2] == self.MAGIC_GZIP:
            return "gzip"
        if data[:2] == self.MAGIC_BZ2:
            return "bz2"
        if data[:6] == self.MAGIC_LZMA:
            return "lzma"
        if len(data) >= 4 and data[:4] == self.MAGIC_ZIP:
            return "zip"
        try:
            zlib.decompress(data)
            return "zlib"
        except zlib.error:
            pass
        try:
            zlib.decompress(data, -self.MAGIC_ZLIB_WINDOW)
            return "zlib_raw"
        except zlib.error:
            pass
        try:
            zlib.decompress(data, self.MAGIC_ZLIB_WINDOW | 32)
            return "zlib_auto"
        except zlib.error:
            pass
        return "unknown"


def decompressor_test():
    print(f"{Colors.CYAN}[Decompressor Test]{Colors.RESET}")
    engine = DecompressorEngine()
    original = b"Hello, this is a test of the decompressor engine! " * 10
    print(f"Original data size: {len(original)} bytes")
    print(f"Original entropy: {calculate_entropy(original):.4f}")
    gzip_data = gzip.compress(original)
    print(f"\nGZIP compressed: {len(gzip_data)} bytes")
    gzip_decompressed = engine.decompress_gzip(gzip_data)
    if gzip_decompressed == original:
        print(f"{Colors.GREEN}[PASS]{Colors.RESET} GZIP decompression successful")
    else:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} GZIP decompression failed")
    bz2_data = bz2.compress(original)
    print(f"\nBZ2 compressed: {len(bz2_data)} bytes")
    bz2_decompressed = engine.decompress_bz2(bz2_data)
    if bz2_decompressed == original:
        print(f"{Colors.GREEN}[PASS]{Colors.RESET} BZ2 decompression successful")
    else:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} BZ2 decompression failed")
    lzma_data = lzma.compress(original)
    print(f"\nLZMA compressed: {len(lzma_data)} bytes")
    lzma_decompressed = engine.decompress_lzma(lzma_data)
    if lzma_decompressed == original:
        print(f"{Colors.GREEN}[PASS]{Colors.RESET} LZMA decompression successful")
    else:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} LZMA decompression failed")
    zlib_data = zlib.compress(original)
    print(f"\nZLIB compressed: {len(zlib_data)} bytes")
    zlib_decompressed = engine.decompress_zlib(zlib_data)
    if zlib_decompressed == original:
        print(f"{Colors.GREEN}[PASS]{Colors.RESET} ZLIB decompression successful")
    else:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} ZLIB decompression failed")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("test_file.txt", original)
        zf.writestr("subdir/nested.txt", b"Nested file content")
    zip_data = zip_buffer.getvalue()
    print(f"\nZIP archive size: {len(zip_data)} bytes")
    zip_files = engine.decompress_zip(zip_data)
    if len(zip_files) == 2:
        print(f"{Colors.GREEN}[PASS]{Colors.RESET} ZIP extraction successful ({len(zip_files)} files)")
        for name, content in zip_files:
            printable = is_printable(content.decode("utf-8", errors="ignore"))
            print(f"  - {name}: {len(content)} bytes (printable: {printable})")
    else:
        print(f"{Colors.RED}[FAIL]{Colors.RESET} ZIP extraction failed (expected 2, got {len(zip_files)})")
    print(f"\n{Colors.CYAN}Detection Tests:{Colors.RESET}")
    print(f"GZIP magic -> {engine.detect_compression(gzip_data)}")
    print(f"BZ2 magic -> {engine.detect_compression(bz2_data)}")
    print(f"LZMA magic -> {engine.detect_compression(lzma_data)}")
    print(f"ZLIB magic -> {engine.detect_compression(zlib_data)}")
    print(f"ZIP magic -> {engine.detect_compression(zip_data)}")
    print(f"Random data -> {engine.detect_compression(b'not compressed data')}")
    print(f"\n{Colors.CYAN}Decompress All Test:{Colors.RESET}")
    all_results = engine.decompress_all(gzip_data)
    print(f"GZIP data via decompress_all: {len(all_results)} result(s)")
    all_results = engine.decompress_all(zip_data)
    print(f"ZIP data via decompress_all: {len(all_results)} result(s)")
    all_results = engine.decompress_all(b'not compressed')
    print(f"Plain data via decompress_all: {len(all_results)} result(s)")
    print(f"\n{Colors.GREEN}All tests completed.{Colors.RESET}")


if __name__ == "__main__":
    decompressor_test()
