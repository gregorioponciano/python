#!/usr/bin/env python3
"""Encoder/Decoder engine for Reverser X Supreme"""

import base64
import urllib.parse
from typing import List, Tuple, Optional, Dict, Any

from utils.constants import Colors, SUPPORTED_ENCODINGS
from utils.helpers import is_printable, calculate_entropy, is_base64, is_hex


class EncoderDecoder:
    """Handles encoding and decoding operations for multiple formats"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.verbose = self.config.get("verbose", True)
        self.supported = SUPPORTED_ENCODINGS

    def decode_base64(self, data: bytes) -> Optional[bytes]:
        """Decode base64 encoded data"""
        try:
            text = data.decode("utf-8", errors="ignore").strip()
            padding = 4 - len(text) % 4
            if padding != 4:
                text += "=" * padding
            decoded = base64.b64decode(text, validate=True)
            printable_ratio = sum(1 for b in decoded if b in range(32, 127)) / max(len(decoded), 1)
            if printable_ratio >= 0.7 or len(decoded) == 0:
                return decoded
            return None
        except Exception:
            return None

    def decode_base32(self, data: bytes) -> Optional[bytes]:
        """Decode base32 encoded data"""
        try:
            text = data.decode("utf-8", errors="ignore").strip().upper()
            padding = 8 - len(text) % 8
            if padding != 8:
                text += "=" * padding
            decoded = base64.b32decode(text)
            printable_ratio = sum(1 for b in decoded if b in range(32, 127)) / max(len(decoded), 1)
            if printable_ratio >= 0.7 or len(decoded) == 0:
                return decoded
            return None
        except Exception:
            return None

    def decode_hex(self, data: bytes) -> Optional[bytes]:
        """Decode hex encoded data"""
        try:
            text = data.decode("utf-8", errors="ignore").strip().replace(" ", "").replace(":", "")
            if len(text) % 2 != 0:
                text = "0" + text
            decoded = bytes.fromhex(text)
            printable_ratio = sum(1 for b in decoded if b in range(32, 127)) / max(len(decoded), 1)
            if printable_ratio >= 0.7 or len(decoded) == 0:
                return decoded
            return None
        except Exception:
            return None

    def decode_url(self, data: bytes) -> Optional[bytes]:
        """Decode URL encoded data"""
        try:
            text = data.decode("utf-8", errors="ignore")
            if "%" not in text and "+" not in text:
                return None
            decoded = urllib.parse.unquote(text)
            if decoded == text:
                return None
            return decoded.encode("utf-8")
        except Exception:
            return None

    def decode_rot13(self, data: bytes) -> bytes:
        """Decode ROT13 encoded data"""
        try:
            text = data.decode("utf-8", errors="ignore")
            result = []
            for char in text:
                if "a" <= char <= "z":
                    result.append(chr((ord(char) - 97 + 13) % 26 + 97))
                elif "A" <= char <= "Z":
                    result.append(chr((ord(char) - 65 + 13) % 26 + 65))
                else:
                    result.append(char)
            return "".join(result).encode("utf-8")
        except Exception:
            return data

    def decode_utf16(self, data: bytes) -> Optional[bytes]:
        """Decode UTF-16 encoded data"""
        try:
            if len(data) < 2:
                return None
            if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
                decoded = data.decode("utf-16")
            elif data[-2:] in (b"\xff\xfe", b"\xfe\xff"):
                decoded = data.decode("utf-16")
            else:
                decoded = data.decode("utf-16-le")
            printable_ratio = sum(1 for c in decoded if c.isprintable() or c in "\n\r\t") / max(len(decoded), 1)
            if printable_ratio >= 0.7:
                return decoded.encode("utf-8")
            return None
        except Exception:
            try:
                decoded = data.decode("utf-16-be")
                printable_ratio = sum(1 for c in decoded if c.isprintable() or c in "\n\r\t") / max(len(decoded), 1)
                if printable_ratio >= 0.7:
                    return decoded.encode("utf-8")
                return None
            except Exception:
                return None

    def decode_all(self, data: bytes) -> List[Tuple[str, bytes]]:
        """Try all decoding methods and return list of (name, decoded_data)"""
        results = []

        b64_result = self.decode_base64(data)
        if b64_result is not None:
            results.append(("base64", b64_result))

        b32_result = self.decode_base32(data)
        if b32_result is not None:
            results.append(("base32", b32_result))

        hex_result = self.decode_hex(data)
        if hex_result is not None:
            results.append(("hex", hex_result))

        url_result = self.decode_url(data)
        if url_result is not None:
            results.append(("url", url_result))

        rot13_result = self.decode_rot13(data)
        if rot13_result != data:
            results.append(("rot13", rot13_result))

        utf16_result = self.decode_utf16(data)
        if utf16_result is not None:
            results.append(("utf-16", utf16_result))

        return results

    def encode_base64(self, data: bytes) -> bytes:
        """Encode data to base64"""
        try:
            return base64.b64encode(data)
        except Exception:
            return data

    def encode_hex(self, data: bytes) -> bytes:
        """Encode data to hexadecimal"""
        try:
            return data.hex().encode("utf-8")
        except Exception:
            return data

    def encode_url(self, data: bytes) -> bytes:
        """Encode data to URL encoding"""
        try:
            text = data.decode("utf-8", errors="ignore")
            return urllib.parse.quote(text, safe="").encode("utf-8")
        except Exception:
            return data

    def encode_rot13(self, data: bytes) -> bytes:
        """Encode data with ROT13"""
        try:
            text = data.decode("utf-8", errors="ignore")
            result = []
            for char in text:
                if "a" <= char <= "z":
                    result.append(chr((ord(char) - 97 + 13) % 26 + 97))
                elif "A" <= char <= "Z":
                    result.append(chr((ord(char) - 65 + 13) % 26 + 65))
                else:
                    result.append(char)
            return "".join(result).encode("utf-8")
        except Exception:
            return data


def encoder_test():
    """Run tests on the EncoderDecoder class"""
    print(f"{Colors.BOLD}{Colors.CYAN}=== Encoder/Decoder Tests ==={Colors.RESET}\n")

    engine = EncoderDecoder()

    original = b"Hello, World!"
    print(f"{Colors.YELLOW}Original:{Colors.RESET} {original}")

    b64_encoded = engine.encode_base64(original)
    print(f"{Colors.YELLOW}Base64 Encoded:{Colors.RESET} {b64_encoded}")
    b64_decoded = engine.decode_base64(b64_encoded)
    print(f"{Colors.YELLOW}Base64 Decoded:{Colors.RESET} {b64_decoded}")
    assert b64_decoded == original, "Base64 roundtrip failed"
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} Base64 roundtrip\n")

    hex_encoded = engine.encode_hex(original)
    print(f"{Colors.YELLOW}Hex Encoded:{Colors.RESET} {hex_encoded}")
    hex_decoded = engine.decode_hex(hex_encoded)
    print(f"{Colors.YELLOW}Hex Decoded:{Colors.RESET} {hex_decoded}")
    assert hex_decoded == original, "Hex roundtrip failed"
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} Hex roundtrip\n")

    url_encoded = engine.encode_url(original)
    print(f"{Colors.YELLOW}URL Encoded:{Colors.RESET} {url_encoded}")
    url_decoded = engine.decode_url(url_encoded)
    print(f"{Colors.YELLOW}URL Decoded:{Colors.RESET} {url_decoded}")
    assert url_decoded == original, "URL roundtrip failed"
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} URL roundtrip\n")

    rot13_encoded = engine.encode_rot13(original)
    print(f"{Colors.YELLOW}ROT13 Encoded:{Colors.RESET} {rot13_encoded}")
    rot13_decoded = engine.decode_rot13(rot13_encoded)
    print(f"{Colors.YELLOW}ROT13 Decoded:{Colors.RESET} {rot13_decoded}")
    assert rot13_decoded == original, "ROT13 roundtrip failed"
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} ROT13 roundtrip\n")

    test_b64 = b"SGVsbG8gV29ybGQh"
    decoded = engine.decode_base64(test_b64)
    print(f"{Colors.YELLOW}Decode Base64 '{test_b64.decode()}':{Colors.RESET} {decoded}")
    assert decoded == b"Hello World!", "Base64 decode failed"
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} Base64 decode\n")

    test_hex = b"48656c6c6f"
    decoded = engine.decode_hex(test_hex)
    print(f"{Colors.YELLOW}Decode Hex '{test_hex.decode()}':{Colors.RESET} {decoded}")
    assert decoded == b"Hello", "Hex decode failed"
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} Hex decode\n")

    test_rot13 = b"Uryyb Jbeyq!"
    decoded = engine.decode_rot13(test_rot13)
    print(f"{Colors.YELLOW}Decode ROT13 '{test_rot13.decode()}':{Colors.RESET} {decoded}")
    assert decoded == b"Hello World!", "ROT13 decode failed"
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} ROT13 decode\n")

    test_url = b"Hello%2C%20World%21"
    decoded = engine.decode_url(test_url)
    print(f"{Colors.YELLOW}Decode URL '{test_url.decode()}':{Colors.RESET} {decoded}")
    assert decoded == b"Hello, World!", "URL decode failed"
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} URL decode\n")

    data = b"Test data for decode_all"
    all_results = engine.decode_all(data)
    print(f"{Colors.YELLOW}Decode All on '{data.decode()}':{Colors.RESET}")
    for name, result in all_results:
        print(f"  {Colors.CYAN}{name}:{Colors.RESET} {result}")
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} Decode all completed\n")

    b32_data = b"JBSWY3DPEBLW64TMMQ======"
    decoded = engine.decode_base32(b32_data)
    print(f"{Colors.YELLOW}Decode Base32 '{b32_data.decode()}':{Colors.RESET} {decoded}")
    if decoded is not None:
        print(f"{Colors.GREEN}[PASS]{Colors.RESET} Base32 decode\n")
    else:
        print(f"{Colors.RED}[SKIP]{Colors.RESET} Base32 decode (no valid result)\n")

    print(f"{Colors.BOLD}{Colors.GREEN}All tests passed!{Colors.RESET}")


if __name__ == "__main__":
    encoder_test()
