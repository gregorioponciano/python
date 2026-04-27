#!/usr/bin/env python3
"""CryptoMenu - Interactive cryptographic analysis and attack menu"""

import os
import sys
import time
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import Colors, COMMON_KEYS
from utils.helpers import safe_file_write, is_printable, calculate_entropy, xor_bytes

try:
    from core.crypto_breaker import CryptoBreaker
except ImportError:
    CryptoBreaker = None

try:
    from core.hash_cracker import HashCracker
except ImportError:
    HashCracker = None

try:
    from core.encoder_decoder import EncoderDecoder
except ImportError:
    EncoderDecoder = None

try:
    from core.xor_attacks import XORAttackEngine
except ImportError:
    XORAttackEngine = None


class CryptoMenu:
    """Interactive menu for cryptographic operations and attacks"""

    def __init__(self, config=None):
        self.config = config or {}
        self.crypto_breaker = CryptoBreaker(config) if CryptoBreaker else None
        self.hash_cracker = HashCracker(config) if HashCracker else None
        self.encoder_decoder = EncoderDecoder(config) if EncoderDecoder else None
        self.xor_engine = XORAttackEngine(config) if XORAttackEngine else None

    def run(self, data: bytes) -> Optional[bytes]:
        """Run crypto menu, return selected result or None"""
        while True:
            self._print_header("Crypto Analysis & Attack Menu")
            print(f"{Colors.GREEN}Data size: {len(data)} bytes{Colors.RESET}")
            print(f"{Colors.GREEN}Entropy: {calculate_entropy(data):.4f} bits/byte{Colors.RESET}")
            print(f"{Colors.GREEN}Printable: {is_printable(data)}{Colors.RESET}")
            print()
            print(f"{Colors.YELLOW}[1]{Colors.RESET} XOR Attack")
            print(f"{Colors.YELLOW}[2]{Colors.RESET} AES Attack")
            print(f"{Colors.YELLOW}[3]{Colors.RESET} Hash Crack")
            print(f"{Colors.YELLOW}[4]{Colors.RESET} Decode / Transform")
            print(f"{Colors.YELLOW}[5]{Colors.RESET} Decompress")
            print(f"{Colors.YELLOW}[6]{Colors.RESET} RSA Analysis")
            print(f"{Colors.YELLOW}[0]{Colors.RESET} Back")
            print()
            choice = input(f"{Colors.CYAN}Select option: {Colors.RESET}").strip()

            if choice == "0":
                return None
            elif choice == "1":
                result = self.xor_attack_submenu(data)
                if result is not None:
                    return result
            elif choice == "2":
                result = self.aes_attack_submenu(data)
                if result is not None:
                    return result
            elif choice == "3":
                result = self.hash_crack_submenu(data)
                if result is not None:
                    return result.encode() if isinstance(result, str) else result
            elif choice == "4":
                result = self.decode_submenu(data)
                if result is not None:
                    return result
            elif choice == "5":
                result = self.decompress_submenu(data)
                if result is not None:
                    return result
            elif choice == "6":
                result = self.rsa_submenu(data)
                if result is not None:
                    return result
            else:
                print(f"{Colors.RED}Invalid option.{Colors.RESET}")
                time.sleep(1)

    def _print_header(self, title: str) -> None:
        """Print a formatted header"""
        width = 60
        print(f"\n{Colors.CYAN}{'=' * width}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.WHITE}{title.center(width)}{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * width}{Colors.RESET}\n")

    def _display_results(self, results: list, max_display: int = 10) -> None:
        """Display a list of results with formatting"""
        if not results:
            print(f"{Colors.RED}No results found.{Colors.RESET}")
            return

        count = min(len(results), max_display)
        print(f"\n{Colors.GREEN}Results ({count} of {len(results)}):{Colors.RESET}")
        print(f"{Colors.CYAN}{'-' * 60}{Colors.RESET}")

        for i, result in enumerate(results[:max_display], 1):
            if isinstance(result, tuple):
                label, value = result
                if isinstance(value, bytes):
                    preview = value[:80]
                    printable = is_printable(preview)
                    entropy = calculate_entropy(value)
                    print(f"{Colors.YELLOW}[{i}]{Colors.RESET} {label}")
                    print(f"    Size: {len(value)} bytes | Entropy: {entropy:.2f}")
                    if printable:
                        print(f"    Content: {preview.decode('utf-8', errors='replace')}")
                    else:
                        print(f"    Hex: {preview.hex()[:80]}...")
                else:
                    print(f"{Colors.YELLOW}[{i}]{Colors.RESET} {label}: {value}")
            elif isinstance(result, bytes):
                preview = result[:80]
                printable = is_printable(preview)
                entropy = calculate_entropy(result)
                print(f"{Colors.YELLOW}[{i}]{Colors.RESET} Size: {len(result)} bytes | Entropy: {entropy:.2f}")
                if printable:
                    print(f"    Content: {preview.decode('utf-8', errors='replace')}")
                else:
                    print(f"    Hex: {preview.hex()[:80]}...")
            else:
                print(f"{Colors.YELLOW}[{i}]{Colors.RESET} {result}")
            print()

        if len(results) > max_display:
            print(f"{Colors.MAGENTA}... and {len(results) - max_display} more results{Colors.RESET}")

    def _save_result(self, data: bytes, filename: str) -> bool:
        """Save result data to file"""
        output_dir = self.config.get("output_dir", "output")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        success = safe_file_write(filepath, data, backup=True)
        if success:
            print(f"{Colors.GREEN}[+] Result saved to: {filepath}{Colors.RESET}")
        else:
            print(f"{Colors.RED}[-] Failed to save result.{Colors.RESET}")
        return success

    def xor_attack_submenu(self, data: bytes) -> Optional[bytes]:
        """XOR attack submenu"""
        if self.xor_engine is None:
            print(f"{Colors.RED}XOR Attack Engine not available.{Colors.RESET}")
            return None

        while True:
            self._print_header("XOR Attack Menu")
            print(f"{Colors.YELLOW}[1]{Colors.RESET} Single-byte XOR brute force")
            print(f"{Colors.YELLOW}[2]{Colors.RESET} Multi-byte XOR with known key")
            print(f"{Colors.YELLOW}[3]{Colors.RESET} XOR with common keys")
            print(f"{Colors.YELLOW}[4]{Colors.RESET} XOR key length detection")
            print(f"{Colors.YELLOW}[5]{Colors.RESET} XOR with custom key (hex)")
            print(f"{Colors.YELLOW}[0]{Colors.RESET} Back")
            print()
            choice = input(f"{Colors.CYAN}Select option: {Colors.RESET}").strip()

            if choice == "0":
                return None
            elif choice == "1":
                print(f"{Colors.CYAN}Running single-byte XOR brute force...{Colors.RESET}")
                results = self.xor_engine.single_byte_xor(data)
                if results:
                    for r in results[:10]:
                        print(f"  {Colors.GREEN}Key: {r['key_hex']}  Score: {r['score']:.2f}  Printable: {r['printable_ratio']:.2%}{Colors.RESET}")
                        print(f"  {Colors.WHITE}{r['decrypted'][:100]}{Colors.RESET}\n")
                    save = input(f"{Colors.CYAN}Save best result? (y/n): {Colors.RESET}").strip().lower()
                    if save == "y":
                        best = results[0]
                        result_data = best['decrypted']
                        filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "xor_result.bin"
                        self._save_result(result_data, filename)
                        return result_data
                else:
                    print(f"{Colors.RED}No viable XOR keys found.{Colors.RESET}")
            elif choice == "2":
                key_hex = input(f"{Colors.CYAN}Enter XOR key (hex): {Colors.RESET}").strip()
                try:
                    key = bytes.fromhex(key_hex)
                    result = xor_bytes(data, key)
                    if result:
                        print(f"\n{Colors.GREEN}Decrypted result:{Colors.RESET}")
                        if is_printable(result):
                            print(result.decode("utf-8", errors="replace"))
                        else:
                            print(result.hex())
                        save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                        if save == "y":
                            filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "xor_decrypted.bin"
                            self._save_result(result, filename)
                            return result
                except ValueError:
                    print(f"{Colors.RED}Invalid hex key.{Colors.RESET}")
            elif choice == "3":
                print(f"{Colors.CYAN}Trying common keys...{Colors.RESET}")
                results = []
                for key in COMMON_KEYS:
                    result = xor_bytes(data, key)
                    if result and is_printable(result):
                        results.append((key.decode("utf-8", errors="replace"), result))
                if results:
                    self._display_results(results)
                    idx = input(f"{Colors.CYAN}Select result number (or 0 to skip): {Colors.RESET}").strip()
                    if idx.isdigit() and 0 < int(idx) <= len(results):
                        selected = results[int(idx) - 1]
                        save = input(f"{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                        if save == "y":
                            filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "xor_common.bin"
                            self._save_result(selected[1], filename)
                            return selected[1]
                else:
                    print(f"{Colors.RED}No common keys produced printable output.{Colors.RESET}")
            elif choice == "4":
                print(f"{Colors.CYAN}Detecting XOR key length...{Colors.RESET}")
                key_lengths = self.xor_engine.guess_key_size(data)
                if key_lengths:
                    print(f"\n{Colors.GREEN}Likely key lengths:{Colors.RESET}")
                    for length in key_lengths[:10]:
                        print(f"  Length: {length}")
                else:
                    print(f"{Colors.RED}Could not determine key length.{Colors.RESET}")
            elif choice == "5":
                key_hex = input(f"{Colors.CYAN}Enter custom XOR key (hex): {Colors.RESET}").strip()
                try:
                    key = bytes.fromhex(key_hex)
                    result = xor_bytes(data, key)
                    if result:
                        print(f"\n{Colors.GREEN}Result:{Colors.RESET}")
                        if is_printable(result):
                            print(result.decode("utf-8", errors="replace"))
                        else:
                            print(result.hex())
                        save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                        if save == "y":
                            filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "xor_custom.bin"
                            self._save_result(result, filename)
                            return result
                except ValueError:
                    print(f"{Colors.RED}Invalid hex key.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid option.{Colors.RESET}")
                time.sleep(1)

    def aes_attack_submenu(self, data: bytes) -> Optional[bytes]:
        """AES attack submenu"""
        if self.crypto_breaker is None:
            print(f"{Colors.RED}Crypto Breaker not available.{Colors.RESET}")
            return None

        while True:
            self._print_header("AES Attack Menu")
            print(f"{Colors.YELLOW}[1]{Colors.RESET} AES-ECB detection")
            print(f"{Colors.YELLOW}[2]{Colors.RESET} AES-CBC with known key/IV")
            print(f"{Colors.YELLOW}[3]{Colors.RESET} AES brute force (short key)")
            print(f"{Colors.YELLOW}[4]{Colors.RESET} AES key search in data")
            print(f"{Colors.YELLOW}[0]{Colors.RESET} Back")
            print()
            choice = input(f"{Colors.CYAN}Select option: {Colors.RESET}").strip()

            if choice == "0":
                return None
            elif choice == "1":
                print(f"{Colors.CYAN}Checking for AES-ECB patterns...{Colors.RESET}")
                if len(data) >= 32:
                    blocks = [data[i:i+16] for i in range(0, len(data) - 15, 16)]
                    unique = set(blocks)
                    if len(unique) < len(blocks) * 0.9:
                        print(f"{Colors.GREEN}[+] Data appears to be AES-ECB encrypted (repeated blocks).{Colors.RESET}")
                        print(f"{Colors.GREEN}Block size: 16 bytes{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}[-] No ECB pattern detected.{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[-] Data too short for ECB detection.{Colors.RESET}")
            elif choice == "2":
                key_hex = input(f"{Colors.CYAN}Enter AES key (hex): {Colors.RESET}").strip()
                iv_hex = input(f"{Colors.CYAN}Enter IV (hex, or empty for zeros): {Colors.RESET}").strip()
                try:
                    key = bytes.fromhex(key_hex)
                    iv = bytes.fromhex(iv_hex) if iv_hex else b"\x00" * 16
                    if len(key) not in (16, 24, 32):
                        print(f"{Colors.RED}[-] Invalid AES key size. Must be 16, 24, or 32 bytes.{Colors.RESET}")
                        continue
                    from Crypto.Cipher import AES
                    from Crypto.Util.Padding import unpad
                    if len(data) < 32 or len(data) % 16 != 0:
                        print(f"{Colors.RED}[-] Data length not a multiple of 16.{Colors.RESET}")
                        continue
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    result = cipher.decrypt(data)
                    try:
                        result = unpad(result, 16)
                    except Exception:
                        pass
                    if result:
                        print(f"\n{Colors.GREEN}Decrypted result:{Colors.RESET}")
                        if is_printable(result):
                            print(result.decode("utf-8", errors="replace"))
                        else:
                            print(result.hex())
                        save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                        if save == "y":
                            filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "aes_decrypted.bin"
                            self._save_result(result, filename)
                            return result
                    else:
                        print(f"{Colors.RED}[-] Decryption failed.{Colors.RESET}")
                except ValueError:
                    print(f"{Colors.RED}Invalid hex input.{Colors.RESET}")
                except ImportError:
                    print(f"{Colors.RED}[-] PyCryptodome not available.{Colors.RESET}")
            elif choice == "3":
                print(f"{Colors.YELLOW}[!] AES brute force not implemented in this version.{Colors.RESET}")
                print(f"{Colors.CYAN}Use single-byte XOR attack for short keys instead.{Colors.RESET}")
            elif choice == "4":
                print(f"{Colors.YELLOW}[!] AES key search not implemented in this version.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid option.{Colors.RESET}")
                time.sleep(1)

    def hash_crack_submenu(self, data: bytes) -> Optional[str]:
        """Hash cracking submenu"""
        if self.hash_cracker is None:
            print(f"{Colors.RED}Hash Cracker not available.{Colors.RESET}")
            return None

        while True:
            self._print_header("Hash Crack Menu")
            print(f"{Colors.YELLOW}[1]{Colors.RESET} Crack single hash")
            print(f"{Colors.YELLOW}[2]{Colors.RESET} Crack with wordlist")
            print(f"{Colors.YELLOW}[3]{Colors.RESET} Brute force hash")
            print(f"{Colors.YELLOW}[4]{Colors.RESET} Identify hash type")
            print(f"{Colors.YELLOW}[0]{Colors.RESET} Back")
            print()
            choice = input(f"{Colors.CYAN}Select option: {Colors.RESET}").strip()

            if choice == "0":
                return None
            elif choice == "1":
                hash_str = input(f"{Colors.CYAN}Enter hash: {Colors.RESET}").strip()
                if not hash_str:
                    try:
                        hash_str = data.decode("ascii", errors="ignore").strip()
                        print(f"{Colors.CYAN}Using data as hash: {hash_str[:32]}...{Colors.RESET}")
                    except Exception:
                        print(f"{Colors.RED}Data cannot be used as hash.{Colors.RESET}")
                        continue
                result = self.hash_cracker.crack_hash(hash_str)
                if result:
                    print(f"{Colors.GREEN}[+] Plaintext: {result}{Colors.RESET}")
                    return result
            elif choice == "2":
                hash_str = input(f"{Colors.CYAN}Enter hash: {Colors.RESET}").strip()
                wordlist = input(f"{Colors.CYAN}Wordlist path: {Colors.RESET}").strip()
                if not hash_str:
                    print(f"{Colors.RED}Hash required.{Colors.RESET}")
                    continue
                if wordlist and os.path.exists(wordlist):
                    result = self.hash_cracker.crack_hash(hash_str, wordlist_path=wordlist)
                else:
                    result = self.hash_cracker.crack_hash(hash_str)
                if result:
                    print(f"{Colors.GREEN}[+] Plaintext: {result}{Colors.RESET}")
                    return result
            elif choice == "3":
                hash_str = input(f"{Colors.CYAN}Enter hash: {Colors.RESET}").strip()
                max_len = input(f"{Colors.CYAN}Max length (default 4): {Colors.RESET}").strip()
                max_len = int(max_len) if max_len.isdigit() else 4
                if not hash_str:
                    print(f"{Colors.RED}Hash required.{Colors.RESET}")
                    continue
                result = self.hash_cracker.brute_force(hash_str, max_length=max_len)
                if result:
                    print(f"{Colors.GREEN}[+] Plaintext: {result}{Colors.RESET}")
                    return result
            elif choice == "4":
                hash_str = input(f"{Colors.CYAN}Enter hash: {Colors.RESET}").strip()
                if not hash_str:
                    try:
                        hash_str = data.decode("ascii", errors="ignore").strip()
                    except Exception:
                        print(f"{Colors.RED}Data cannot be used as hash.{Colors.RESET}")
                        continue
                types = self.hash_cracker.identify_hash(hash_str)
                if types:
                    print(f"{Colors.GREEN}Possible types: {', '.join(types)}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Unknown hash type.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid option.{Colors.RESET}")
                time.sleep(1)

    def decode_submenu(self, data: bytes) -> Optional[bytes]:
        """Decode / transform submenu"""
        if self.encoder_decoder is None:
            print(f"{Colors.RED}Encoder/Decoder not available.{Colors.RESET}")
            return None

        while True:
            self._print_header("Decode / Transform Menu")
            print(f"{Colors.YELLOW}[1]{Colors.RESET} Base64 decode")
            print(f"{Colors.YELLOW}[2]{Colors.RESET} Hex decode")
            print(f"{Colors.YELLOW}[3]{Colors.RESET} URL decode")
            print(f"{Colors.YELLOW}[4]{Colors.RESET} ROT13")
            print(f"{Colors.YELLOW}[5]{Colors.RESET} Auto-detect and decode")
            print(f"{Colors.YELLOW}[6]{Colors.RESET} Encode to Base64")
            print(f"{Colors.YELLOW}[7]{Colors.RESET} Encode to Hex")
            print(f"{Colors.YELLOW}[0]{Colors.RESET} Back")
            print()
            choice = input(f"{Colors.CYAN}Select option: {Colors.RESET}").strip()

            if choice == "0":
                return None
            elif choice == "1":
                result = self.encoder_decoder.decode_base64(data)
                if result:
                    print(f"\n{Colors.GREEN}Decoded result:{Colors.RESET}")
                    if is_printable(result):
                        print(result.decode("utf-8", errors="replace"))
                    else:
                        print(result.hex())
                    save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                    if save == "y":
                        filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "decoded_base64.bin"
                        self._save_result(result, filename)
                        return result
                else:
                    print(f"{Colors.RED}[-] Base64 decode failed.{Colors.RESET}")
            elif choice == "2":
                try:
                    text = data.decode("ascii", errors="ignore").strip()
                    result = bytes.fromhex(text)
                    print(f"\n{Colors.GREEN}Decoded result:{Colors.RESET}")
                    if is_printable(result):
                        print(result.decode("utf-8", errors="replace"))
                    else:
                        print(result.hex())
                    save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                    if save == "y":
                        filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "decoded_hex.bin"
                        self._save_result(result, filename)
                        return result
                except ValueError:
                    print(f"{Colors.RED}[-] Invalid hex data.{Colors.RESET}")
            elif choice == "3":
                result = self.encoder_decoder.decode_url(data)
                if result:
                    print(f"\n{Colors.GREEN}Decoded result:{Colors.RESET}")
                    if is_printable(result):
                        print(result.decode("utf-8", errors="replace"))
                    else:
                        print(result.hex())
                    save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                    if save == "y":
                        filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "decoded_url.bin"
                        self._save_result(result, filename)
                        return result
                else:
                    print(f"{Colors.RED}[-] URL decode failed.{Colors.RESET}")
            elif choice == "4":
                result = self.encoder_decoder.decode_rot13(data)
                if result:
                    print(f"\n{Colors.GREEN}ROT13 result:{Colors.RESET}")
                    print(result.decode("utf-8", errors="replace"))
                    save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                    if save == "y":
                        filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "rot13_result.bin"
                        self._save_result(result, filename)
                        return result
            elif choice == "5":
                print(f"{Colors.CYAN}Auto-detecting encoding...{Colors.RESET}")
                results = self.encoder_decoder.decode_all(data)
                if results:
                    self._display_results(results)
                    idx = input(f"{Colors.CYAN}Select result number (or 0 to skip): {Colors.RESET}").strip()
                    if idx.isdigit() and 0 < int(idx) <= len(results):
                        selected = results[int(idx) - 1]
                        result_data = selected[1] if isinstance(selected, tuple) else selected
                        save = input(f"{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                        if save == "y":
                            filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "auto_decoded.bin"
                            self._save_result(result_data, filename)
                            return result_data
                else:
                    print(f"{Colors.RED}No decoding methods succeeded.{Colors.RESET}")
            elif choice == "6":
                result = self.encoder_decoder.encode_base64(data)
                if result:
                    print(f"\n{Colors.GREEN}Base64 encoded:{Colors.RESET}")
                    print(result.decode("utf-8", errors="replace"))
                    save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                    if save == "y":
                        filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "encoded_base64.txt"
                        self._save_result(result, filename)
                        return result
            elif choice == "7":
                result = data.hex().encode()
                print(f"\n{Colors.GREEN}Hex encoded:{Colors.RESET}")
                print(result.decode())
                save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                if save == "y":
                    filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "encoded_hex.txt"
                    self._save_result(result, filename)
                    return result
            else:
                print(f"{Colors.RED}Invalid option.{Colors.RESET}")
                time.sleep(1)

    def decompress_submenu(self, data: bytes) -> Optional[bytes]:
        """Decompress submenu"""
        from core.decompressor import DecompressorEngine

        engine = DecompressorEngine(self.config)

        while True:
            self._print_header("Decompress Menu")
            detected = engine.detect_compression(data)
            print(f"{Colors.GREEN}Detected compression: {detected}{Colors.RESET}")
            print()
            print(f"{Colors.YELLOW}[1]{Colors.RESET} Decompress GZIP")
            print(f"{Colors.YELLOW}[2]{Colors.RESET} Decompress BZ2")
            print(f"{Colors.YELLOW}[3]{Colors.RESET} Decompress LZMA/XZ")
            print(f"{Colors.YELLOW}[4]{Colors.RESET} Decompress ZLIB")
            print(f"{Colors.YELLOW}[5]{Colors.RESET} Decompress ZIP")
            print(f"{Colors.YELLOW}[6]{Colors.RESET} Try all methods")
            print(f"{Colors.YELLOW}[0]{Colors.RESET} Back")
            print()
            choice = input(f"{Colors.CYAN}Select option: {Colors.RESET}").strip()

            if choice == "0":
                return None
            elif choice == "1":
                result = engine.decompress_gzip(data)
                if result:
                    print(f"\n{Colors.GREEN}Decompressed: {len(result)} bytes{Colors.RESET}")
                    if is_printable(result):
                        print(result.decode("utf-8", errors="replace")[:500])
                    else:
                        print(result.hex()[:200])
                    save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                    if save == "y":
                        filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "decompressed_gz.bin"
                        self._save_result(result, filename)
                        return result
                else:
                    print(f"{Colors.RED}[-] GZIP decompression failed.{Colors.RESET}")
            elif choice == "2":
                result = engine.decompress_bz2(data)
                if result:
                    print(f"\n{Colors.GREEN}Decompressed: {len(result)} bytes{Colors.RESET}")
                    if is_printable(result):
                        print(result.decode("utf-8", errors="replace")[:500])
                    else:
                        print(result.hex()[:200])
                    save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                    if save == "y":
                        filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "decompressed_bz2.bin"
                        self._save_result(result, filename)
                        return result
                else:
                    print(f"{Colors.RED}[-] BZ2 decompression failed.{Colors.RESET}")
            elif choice == "3":
                result = engine.decompress_lzma(data)
                if result:
                    print(f"\n{Colors.GREEN}Decompressed: {len(result)} bytes{Colors.RESET}")
                    if is_printable(result):
                        print(result.decode("utf-8", errors="replace")[:500])
                    else:
                        print(result.hex()[:200])
                    save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                    if save == "y":
                        filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "decompressed_lzma.bin"
                        self._save_result(result, filename)
                        return result
                else:
                    print(f"{Colors.RED}[-] LZMA decompression failed.{Colors.RESET}")
            elif choice == "4":
                result = engine.decompress_zlib(data)
                if result:
                    print(f"\n{Colors.GREEN}Decompressed: {len(result)} bytes{Colors.RESET}")
                    if is_printable(result):
                        print(result.decode("utf-8", errors="replace")[:500])
                    else:
                        print(result.hex()[:200])
                    save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                    if save == "y":
                        filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "decompressed_zlib.bin"
                        self._save_result(result, filename)
                        return result
                else:
                    print(f"{Colors.RED}[-] ZLIB decompression failed.{Colors.RESET}")
            elif choice == "5":
                results = engine.decompress_zip(data)
                if results:
                    self._display_results(results)
                    idx = input(f"{Colors.CYAN}Select file number (or 0 to skip): {Colors.RESET}").strip()
                    if idx.isdigit() and 0 < int(idx) <= len(results):
                        name, content = results[int(idx) - 1]
                        save = input(f"{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                        if save == "y":
                            filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or name
                            self._save_result(content, filename)
                            return content
                else:
                    print(f"{Colors.RED}[-] ZIP decompression failed.{Colors.RESET}")
            elif choice == "6":
                results = engine.decompress_all(data)
                if results:
                    self._display_results(results)
                    idx = input(f"{Colors.CYAN}Select result number (or 0 to skip): {Colors.RESET}").strip()
                    if idx.isdigit() and 0 < int(idx) <= len(results):
                        label, content = results[int(idx) - 1]
                        save = input(f"{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                        if save == "y":
                            filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or f"decompressed_{label}.bin"
                            self._save_result(content, filename)
                            return content
                else:
                    print(f"{Colors.RED}[-] No decompression method succeeded.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid option.{Colors.RESET}")
                time.sleep(1)

    def rsa_submenu(self, data: bytes) -> Optional[bytes]:
        """RSA analysis submenu"""
        if self.crypto_breaker is None:
            print(f"{Colors.RED}Crypto Breaker not available.{Colors.RESET}")
            return None

        while True:
            self._print_header("RSA Analysis Menu")
            print(f"{Colors.YELLOW}[1]{Colors.RESET} Detect RSA public key")
            print(f"{Colors.YELLOW}[2]{Colors.RESET} Detect RSA private key")
            print(f"{Colors.YELLOW}[3]{Colors.RESET} Extract RSA modulus")
            print(f"{Colors.YELLOW}[4]{Colors.RESET} Factor small modulus")
            print(f"{Colors.YELLOW}[5]{Colors.RESET} RSA key format conversion")
            print(f"{Colors.YELLOW}[0]{Colors.RESET} Back")
            print()
            choice = input(f"{Colors.CYAN}Select option: {Colors.RESET}").strip()

            if choice == "0":
                return None
            elif choice == "1":
                print(f"{Colors.CYAN}Scanning for RSA public keys...{Colors.RESET}")
                rsa_patterns = [b'-----BEGIN RSA PUBLIC KEY-----', b'-----BEGIN PUBLIC KEY-----']
                found = []
                for pattern in rsa_patterns:
                    offset = 0
                    while True:
                        pos = data.find(pattern, offset)
                        if pos == -1:
                            break
                        end_pos = data.find(b'-----END', pos)
                        if end_pos != -1:
                            end_pos = data.find(b'-----', end_pos + 5)
                            if end_pos != -1:
                                found.append(data[pos:end_pos + 5].decode('utf-8', errors='replace'))
                        offset = pos + 1
                if found:
                    print(f"{Colors.GREEN}Found {len(found)} public key(s):{Colors.RESET}")
                    for i, key in enumerate(found, 1):
                        print(f"  [{i}] {key[:80]}...")
                else:
                    print(f"{Colors.RED}No RSA public keys found.{Colors.RESET}")
            elif choice == "2":
                print(f"{Colors.CYAN}Scanning for RSA private keys...{Colors.RESET}")
                rsa_patterns = [b'-----BEGIN RSA PRIVATE KEY-----', b'-----BEGIN PRIVATE KEY-----']
                found = []
                for pattern in rsa_patterns:
                    offset = 0
                    while True:
                        pos = data.find(pattern, offset)
                        if pos == -1:
                            break
                        end_pos = data.find(b'-----END', pos)
                        if end_pos != -1:
                            end_pos = data.find(b'-----', end_pos + 5)
                            if end_pos != -1:
                                found.append(data[pos:end_pos + 5].decode('utf-8', errors='replace'))
                        offset = pos + 1
                if found:
                    print(f"{Colors.GREEN}Found {len(found)} private key(s):{Colors.RESET}")
                    for i, key in enumerate(found, 1):
                        print(f"  [{i}] {key[:80]}...")
                else:
                    print(f"{Colors.RED}No RSA private keys found.{Colors.RESET}")
            elif choice == "3":
                print(f"{Colors.YELLOW}[!] RSA modulus extraction requires PyCryptodome and a valid PEM key.{Colors.RESET}")
                print(f"{Colors.CYAN}Ensure the data contains a PEM-encoded RSA key.{Colors.RESET}")
            elif choice == "4":
                modulus_str = input(f"{Colors.CYAN}Enter modulus (decimal or hex): {Colors.RESET}").strip()
                if not modulus_str:
                    print(f"{Colors.RED}Modulus required.{Colors.RESET}")
                    continue
                try:
                    if modulus_str.startswith("0x"):
                        n = int(modulus_str, 16)
                    else:
                        n = int(modulus_str)
                    print(f"{Colors.CYAN}Factoring modulus (trial division, small numbers only)...{Colors.RESET}")
                    factors = None
                    limit = int(n ** 0.5) + 1
                    limit = min(limit, 1000000)
                    for i in range(2, limit):
                        if n % i == 0:
                            p = i
                            q = n // i
                            factors = (p, q)
                            break
                    if factors:
                        p, q = factors
                        print(f"{Colors.GREEN}p = {p}{Colors.RESET}")
                        print(f"{Colors.GREEN}q = {q}{Colors.RESET}")
                        result_data = f"p = {p}\nq = {q}\nn = {n}".encode()
                        save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                        if save == "y":
                            filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "rsa_factors.txt"
                            self._save_result(result_data, filename)
                            return result_data
                    else:
                        print(f"{Colors.RED}Could not factor modulus (too large for trial division).{Colors.RESET}")
                except ValueError:
                    print(f"{Colors.RED}Invalid number.{Colors.RESET}")
            elif choice == "5":
                print(f"{Colors.YELLOW}[1]{Colors.RESET} PEM to DER")
                print(f"{Colors.YELLOW}[2]{Colors.RESET} DER to PEM")
                fmt = input(f"{Colors.CYAN}Select conversion: {Colors.RESET}").strip()
                if fmt == "1":
                    try:
                        import base64
                        text = data.decode("utf-8", errors="ignore")
                        b64_data = "".join(line for line in text.splitlines() if not line.startswith("-----"))
                        result = base64.b64decode(b64_data)
                    except Exception as e:
                        print(f"{Colors.RED}[-] PEM to DER conversion failed: {e}{Colors.RESET}")
                        result = None
                elif fmt == "2":
                    try:
                        import base64
                        b64 = base64.b64encode(data).decode("utf-8")
                        lines = [b64[i:i+64] for i in range(0, len(b64), 64)]
                        result = f"-----BEGIN CERTIFICATE-----\n{''.join(chr(10) + l for l in lines)}\n-----END CERTIFICATE-----".encode()
                    except Exception as e:
                        print(f"{Colors.RED}[-] DER to PEM conversion failed: {e}{Colors.RESET}")
                        result = None
                else:
                    print(f"{Colors.RED}Invalid option.{Colors.RESET}")
                    continue
                if result:
                    print(f"\n{Colors.GREEN}Converted result:{Colors.RESET}")
                    print(result.decode("utf-8", errors="replace")[:500])
                    save = input(f"\n{Colors.CYAN}Save result? (y/n): {Colors.RESET}").strip().lower()
                    if save == "y":
                        filename = input(f"{Colors.CYAN}Filename: {Colors.RESET}").strip() or "rsa_converted.bin"
                        self._save_result(result, filename)
                        return result
                else:
                    print(f"{Colors.RED}Conversion failed.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid option.{Colors.RESET}")
                time.sleep(1)
