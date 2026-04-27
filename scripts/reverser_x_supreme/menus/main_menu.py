#!/usr/bin/env python3
"""Main menu implementation for Reverser X Supreme"""

import os
import sys
import time
import base64
import hashlib
import zipfile
import io
from typing import List, Optional

from utils.constants import Colors, VERSION, MAGIC_NUMBERS, COMMON_KEYS
from utils.helpers import (
    print_analysis,
    safe_file_write,
    get_file_hash,
    find_repeating_patterns,
    is_printable,
    calculate_entropy,
    xor_bytes,
)
from core import (
    ReverserEngine,
    AdvancedAnalyzer,
    CryptoBreaker,
    HashCracker,
    DecompressorEngine,
    EncoderDecoder,
    XORAttackEngine,
)


class MainMenu:
    """Main menu for Reverser X Supreme"""

    def __init__(self, config=None):
        self.config = config or {}
        self.engine = ReverserEngine(config=self.config)
        self.crypto = CryptoBreaker(config=self.config)
        self.hash_cracker = HashCracker(config=self.config)
        self.decompressor = DecompressorEngine(config=self.config)
        self.encoder = EncoderDecoder(config=self.config)
        self.xor_engine = XORAttackEngine(config=self.config)
        self.loaded_data = None
        self.loaded_file = None
        self.output_dir = self.config.get("output_dir", "output")
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self, title=None):
        self.clear_screen()
        print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}  Reverser X Supreme v{VERSION}{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")
        if title:
            print(f"\n{Colors.YELLOW}{title}{Colors.RESET}\n")
        else:
            print()

    @staticmethod
    def calculate_entropy(data: bytes) -> float:
        if not data:
            return 0.0
        length = len(data)
        freq = {}
        for byte in data:
            freq[byte] = freq.get(byte, 0) + 1
        entropy = 0.0
        for count in freq.values():
            p = count / length
            if p > 0:
                import math
                entropy -= p * math.log2(p)
        return entropy

    @staticmethod
    def print_menu_option(number, text, color=Colors.GREEN):
        print(f"  {Colors.BOLD}[{number}]{Colors.RESET} {color}{text}{Colors.RESET}")

    def get_user_input(self, prompt, valid_options=None) -> str:
        while True:
            try:
                choice = input(f"{Colors.YELLOW}{prompt}{Colors.RESET} ").strip()
                if valid_options and choice not in valid_options:
                    print(f"{Colors.RED}Invalid option. Choose from: {', '.join(valid_options)}{Colors.RESET}")
                    continue
                return choice
            except (EOFError, KeyboardInterrupt):
                print(f"\n{Colors.RED}Operation cancelled.{Colors.RESET}")
                return ""

    def load_file_menu(self):
        self.print_header("Load File")
        filepath = input(f"{Colors.YELLOW}Enter file path: {Colors.RESET} ").strip()
        if not filepath:
            print(f"{Colors.RED}No file specified.{Colors.RESET}")
            time.sleep(1)
            return
        filepath = os.path.expanduser(filepath)
        if not os.path.exists(filepath):
            print(f"{Colors.RED}File not found: {filepath}{Colors.RESET}")
            time.sleep(1)
            return
        if not os.path.isfile(filepath):
            print(f"{Colors.RED}Not a file: {filepath}{Colors.RESET}")
            time.sleep(1)
            return
        try:
            file_size = os.path.getsize(filepath)
            if file_size > 100 * 1024 * 1024:
                confirm = input(f"{Colors.YELLOW}File is {file_size / (1024*1024):.1f}MB. Load anyway? (y/n): {Colors.RESET} ").strip().lower()
                if confirm != "y":
                    print(f"{Colors.RED}Load cancelled.{Colors.RESET}")
                    time.sleep(1)
                    return
            with open(filepath, "rb") as f:
                self.loaded_data = f.read()
            self.loaded_file = filepath
            print(f"\n{Colors.GREEN}[+] File loaded successfully!{Colors.RESET}")
            print(f"  {Colors.CYAN}Path:{Colors.RESET} {filepath}")
            print(f"  {Colors.CYAN}Size:{Colors.RESET} {file_size} bytes ({file_size / 1024:.2f} KB)")
            md5_hash = hashlib.md5(self.loaded_data).hexdigest()
            sha256_hash = hashlib.sha256(self.loaded_data).hexdigest()
            print(f"  {Colors.CYAN}MD5:{Colors.RESET} {md5_hash}")
            print(f"  {Colors.CYAN}SHA256:{Colors.RESET} {sha256_hash[:32]}...")
            entropy = calculate_entropy(self.loaded_data)
            print(f"  {Colors.CYAN}Entropy:{Colors.RESET} {entropy:.4f} / 8.0000")
            if entropy > 7.5:
                print(f"  {Colors.RED}[!] High entropy - possibly encrypted or compressed{Colors.RESET}")
            elif entropy > 6.0:
                print(f"  {Colors.YELLOW}[~] Medium entropy - possibly encoded{Colors.RESET}")
            else:
                print(f"  {Colors.GREEN}[+] Low entropy - likely plaintext or structured data{Colors.RESET}")
            for magic, ftype in MAGIC_NUMBERS.items():
                if self.loaded_data[:len(magic)] == magic:
                    print(f"  {Colors.MAGENTA}[*] Detected type: {ftype}{Colors.RESET}")
                    break
            print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
            input()
        except PermissionError:
            print(f"{Colors.RED}Permission denied: {filepath}{Colors.RESET}")
            time.sleep(1)
        except Exception as e:
            print(f"{Colors.RED}Error loading file: {e}{Colors.RESET}")
            time.sleep(1)

    def load_example_menu(self):
        self.print_header("Load Example Data")
        self.print_menu_option(1, "Test ZIP Archive")
        self.print_menu_option(2, "Test XOR Encrypted Data")
        self.print_menu_option(3, "Test Base64 Encoded Data")
        self.print_menu_option(4, "Test High Entropy Data")
        self.print_menu_option(0, "Back to Main Menu")
        choice = self.get_user_input("Choose an option:", ["0", "1", "2", "3", "4"])
        if choice == "0":
            return
        elif choice == "1":
            self.loaded_data = self.create_test_zip()
            self.loaded_file = "example.zip"
            print(f"{Colors.GREEN}[+] Test ZIP loaded ({len(self.loaded_data)} bytes){Colors.RESET}")
        elif choice == "2":
            self.loaded_data = self.create_test_xor()
            self.loaded_file = "example_xor.bin"
            print(f"{Colors.GREEN}[+] Test XOR data loaded ({len(self.loaded_data)} bytes){Colors.RESET}")
        elif choice == "3":
            original = b"Hello, this is a test of Base64 encoding in Reverser X Supreme!"
            self.loaded_data = base64.b64encode(original)
            self.loaded_file = "example_base64.txt"
            print(f"{Colors.GREEN}[+] Test Base64 data loaded ({len(self.loaded_data)} bytes){Colors.RESET}")
        elif choice == "4":
            self.loaded_data = bytes([i % 256 for i in range(1024)])
            self.loaded_file = "example_entropy.bin"
            print(f"{Colors.GREEN}[+] Test high entropy data loaded ({len(self.loaded_data)} bytes){Colors.RESET}")
        time.sleep(1)

    def create_test_zip(self) -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("readme.txt", "This is a test file inside a ZIP archive.\n" * 10)
            zf.writestr("data/config.json", '{"key": "value", "secret": "test123"}')
            zf.writestr("data/notes.txt", "Important notes for testing purposes.")
        return buffer.getvalue()

    def create_test_xor(self) -> bytes:
        plaintext = b"This is a secret message encrypted with XOR. " * 5
        key = b"secretkey"
        result = bytearray(len(plaintext))
        for i in range(len(plaintext)):
            result[i] = plaintext[i] ^ key[i % len(key)]
        return bytes(result)

    def analysis_menu(self):
        while True:
            self.print_header("Analysis Menu")
            if self.loaded_data:
                self.print_menu_option(1, "Full Analysis")
                self.print_menu_option(2, "Statistical Analysis")
                self.print_menu_option(3, "Pattern Detection")
                self.print_menu_option(4, "Entropy Analysis")
                self.print_menu_option(5, "String Search")
                self.print_menu_option(6, "Extract Strings")
                self.print_menu_option(0, "Back to Main Menu")
                choice = self.get_user_input("Choose an option:", ["0", "1", "2", "3", "4", "5", "6"])
            else:
                self.print_menu_option(1, "Load File First", color=Colors.RED)
                self.print_menu_option(0, "Back to Main Menu")
                choice = self.get_user_input("Choose an option:", ["0", "1"])
            if choice == "0":
                break
            elif choice == "1" and self.loaded_data:
                self.full_analysis()
            elif choice == "2" and self.loaded_data:
                self.statistical_analysis()
            elif choice == "3" and self.loaded_data:
                self.pattern_detection()
            elif choice == "4" and self.loaded_data:
                self.entropy_analysis()
            elif choice == "5" and self.loaded_data:
                self.string_search()
            elif choice == "6" and self.loaded_data:
                self.extract_strings_menu()

    def full_analysis(self):
        if not self.loaded_data:
            print(f"{Colors.RED}No data loaded.{Colors.RESET}")
            time.sleep(1)
            return
        self.print_header("Full Analysis")
        print(f"{Colors.CYAN}[*] Starting full analysis...{Colors.RESET}")
        print(f"{Colors.CYAN}[*] File: {self.loaded_file}{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Size: {len(self.loaded_data)} bytes{Colors.RESET}\n")
        print(f"{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
        print(f"{Colors.YELLOW}  FILE IDENTIFICATION{Colors.RESET}")
        print(f"{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
        detected = False
        for magic, ftype in MAGIC_NUMBERS.items():
            if self.loaded_data[:len(magic)] == magic:
                print(f"  {Colors.GREEN}[+] Detected: {ftype}{Colors.RESET}")
                detected = True
                break
        if not detected:
            print(f"  {Colors.YELLOW}[~] No known file signature detected{Colors.RESET}")
        print(f"\n{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
        print(f"{Colors.YELLOW}  ENTROPY ANALYSIS{Colors.RESET}")
        print(f"{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
        entropy = calculate_entropy(self.loaded_data)
        print(f"  Shannon Entropy: {Colors.BOLD}{entropy:.4f}{Colors.RESET} / 8.0000")
        if entropy > 7.5:
            print(f"  Assessment: {Colors.RED}Very High - Encrypted/Compressed{Colors.RESET}")
        elif entropy > 6.5:
            print(f"  Assessment: {Colors.YELLOW}High - Possibly encoded{Colors.RESET}")
        elif entropy > 4.0:
            print(f"  Assessment: {Colors.GREEN}Medium - Mixed content{Colors.RESET}")
        else:
            print(f"  Assessment: {Colors.GREEN}Low - Structured/Plaintext{Colors.RESET}")
        print(f"\n{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
        print(f"{Colors.YELLOW}  STRING EXTRACTION{Colors.RESET}")
        print(f"{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
        strings = self.extract_strings(self.loaded_data, min_length=4)
        print(f"  Found {len(strings)} strings (min length 4)")
        if strings:
            print(f"  {Colors.CYAN}First 20 strings:{Colors.RESET}")
            for s in strings[:20]:
                print(f"    {Colors.WHITE}{s}{Colors.RESET}")
            if len(strings) > 20:
                print(f"    {Colors.YELLOW}... and {len(strings) - 20} more{Colors.RESET}")
        print(f"\n{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
        print(f"{Colors.YELLOW}  PATTERN DETECTION{Colors.RESET}")
        print(f"{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
        patterns = find_repeating_patterns(self.loaded_data)
        if patterns:
            print(f"  Found {len(patterns)} repeating patterns")
            for pattern, count in patterns[:10]:
                printable_pattern = pattern.decode("utf-8", errors="replace")
                print(f"    {Colors.WHITE}'{printable_pattern}' x{count}{Colors.RESET}")
        else:
            print(f"  {Colors.YELLOW}[~] No significant repeating patterns found{Colors.RESET}")
        print(f"\n{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
        print(f"{Colors.YELLOW}  ENCODING DETECTION{Colors.RESET}")
        print(f"{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
        try:
            text = self.loaded_data.decode("utf-8")
            if is_printable(self.loaded_data):
                print(f"  {Colors.GREEN}[+] Valid UTF-8 text{Colors.RESET}")
        except UnicodeDecodeError:
            print(f"  {Colors.YELLOW}[~] Not valid UTF-8{Colors.RESET}")
        try:
            decoded = base64.b64decode(self.loaded_data, validate=True)
            print(f"  {Colors.GREEN}[+] Valid Base64 detected{Colors.RESET}")
        except Exception:
            print(f"  {Colors.RED}[-] Not valid Base64{Colors.RESET}")
        print(f"\n{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
        print(f"{Colors.YELLOW}  HASHES{Colors.RESET}")
        print(f"{Colors.YELLOW}{'=' * 50}{Colors.RESET}")
        md5_hash = hashlib.md5(self.loaded_data).hexdigest()
        sha1_hash = hashlib.sha1(self.loaded_data).hexdigest()
        sha256_hash = hashlib.sha256(self.loaded_data).hexdigest()
        print(f"  MD5:    {Colors.WHITE}{md5_hash}{Colors.RESET}")
        print(f"  SHA1:   {Colors.WHITE}{sha1_hash}{Colors.RESET}")
        print(f"  SHA256: {Colors.WHITE}{sha256_hash}{Colors.RESET}")
        print(f"\n{Colors.GREEN}[+] Analysis complete!{Colors.RESET}")
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def statistical_analysis(self):
        if not self.loaded_data:
            print(f"{Colors.RED}No data loaded.{Colors.RESET}")
            time.sleep(1)
            return
        self.print_header("Statistical Analysis")
        print(f"{Colors.CYAN}[*] Analyzing byte distribution...{Colors.RESET}\n")
        byte_freq = [0] * 256
        for byte in self.loaded_data:
            byte_freq[byte] += 1
        total = len(self.loaded_data)
        print(f"{Colors.YELLOW}Byte Frequency Distribution:{Colors.RESET}")
        print(f"  {Colors.CYAN}Range        Count      Percentage{Colors.RESET}")
        print(f"  {Colors.CYAN}{'-' * 40}{Colors.RESET}")
        for i in range(0, 256, 16):
            chunk_count = sum(byte_freq[i:i+16])
            pct = (chunk_count / total) * 100
            bar = "#" * int(pct / 2)
            print(f"  {Colors.WHITE}0x{i:02x}-0x{i+15:02x}  {chunk_count:>10}  {pct:>6.2f}%  {bar}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Byte Statistics:{Colors.RESET}")
        non_zero = sum(1 for f in byte_freq if f > 0)
        max_freq = max(byte_freq)
        min_freq = min(f for f in byte_freq if f > 0) if non_zero > 0 else 0
        max_byte = byte_freq.index(max_freq)
        print(f"  {Colors.CYAN}Unique bytes:{Colors.RESET} {non_zero} / 256")
        print(f"  {Colors.CYAN}Most common:{Colors.RESET} 0x{max_byte:02x} ({max_freq} occurrences)")
        if non_zero > 0:
            print(f"  {Colors.CYAN}Least common:{Colors.RESET} {min_freq} occurrences")
        chi_squared = 0.0
        expected = total / 256
        for freq in byte_freq:
            chi_squared += ((freq - expected) ** 2) / expected if expected > 0 else 0
        print(f"  {Colors.CYAN}Chi-squared:{Colors.RESET} {chi_squared:.2f}")
        if chi_squared < 256:
            print(f"  {Colors.GREEN}[+] Distribution appears uniform (random-like){Colors.RESET}")
        else:
            print(f"  {Colors.YELLOW}[~] Distribution is non-uniform (structured data){Colors.RESET}")
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def pattern_detection(self):
        if not self.loaded_data:
            print(f"{Colors.RED}No data loaded.{Colors.RESET}")
            time.sleep(1)
            return
        self.print_header("Pattern Detection")
        print(f"{Colors.CYAN}[*] Searching for repeating patterns...{Colors.RESET}\n")
        patterns = find_repeating_patterns(self.loaded_data)
        if patterns:
            print(f"{Colors.GREEN}[+] Found {len(patterns)} repeating patterns:{Colors.RESET}\n")
            for i, (pattern, count) in enumerate(patterns[:20], 1):
                printable = pattern.decode("utf-8", errors="replace")
                hex_repr = pattern.hex()
                print(f"  {Colors.BOLD}[{i}]{Colors.RESET} Count: {count}")
                print(f"    {Colors.CYAN}Hex:{Colors.RESET} {hex_repr[:64]}{'...' if len(hex_repr) > 64 else ''}")
                print(f"    {Colors.CYAN}ASCII:{Colors.RESET} {printable[:64]}")
                print()
        else:
            print(f"{Colors.YELLOW}[~] No significant repeating patterns found.{Colors.RESET}")
        print(f"\n{Colors.YELLOW}XOR Key Detection:{Colors.RESET}")
        for key_size in range(1, 9):
            multi_results = self.xor_engine.multi_byte_xor(self.loaded_data, key_size)
            if multi_results:
                best = multi_results[0]
                decrypted = best['decrypted']
                printable_ratio = best['printable_ratio']
                if printable_ratio > 0.7:
                    print(f"  {Colors.GREEN}[+] Possible XOR key (size {key_size}): {best['key_hex']} (printable: {printable_ratio:.2%}){Colors.RESET}")
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def extract_strings(self, data: bytes, min_length: int = 4) -> List[str]:
        strings = []
        current = []
        for byte in data:
            if byte in range(32, 127) or byte in (9, 10, 13):
                current.append(chr(byte))
            else:
                if len(current) >= min_length:
                    strings.append("".join(current))
                current = []
        if len(current) >= min_length:
            strings.append("".join(current))
        return strings

    def extract_strings_menu(self):
        self.print_header("String Extraction")
        self.print_menu_option(1, "Extract strings (min length 4)")
        self.print_menu_option(2, "Extract strings (min length 6)")
        self.print_menu_option(3, "Extract strings (min length 8)")
        self.print_menu_option(4, "Extract UTF-16 strings")
        self.print_menu_option(5, "Search for specific pattern")
        self.print_menu_option(0, "Back")
        choice = self.get_user_input("Choose an option:", ["0", "1", "2", "3", "4", "5"])
        if choice == "0":
            return
        elif choice in ("1", "2", "3"):
            min_lengths = {"1": 4, "2": 6, "3": 8}
            min_len = min_lengths[choice]
            strings = self.extract_strings(self.loaded_data, min_length=min_len)
            print(f"\n{Colors.GREEN}[+] Found {len(strings)} strings (min length {min_len}):{Colors.RESET}\n")
            for s in strings[:50]:
                print(f"  {Colors.WHITE}{s}{Colors.RESET}")
            if len(strings) > 50:
                print(f"  {Colors.YELLOW}... and {len(strings) - 50} more{Colors.RESET}")
        elif choice == "4":
            strings = []
            try:
                text = self.loaded_data.decode("utf-16", errors="ignore")
                current = []
                for char in text:
                    if ord(char) in range(32, 127) or ord(char) in (9, 10, 13):
                        current.append(char)
                    else:
                        if len(current) >= 4:
                            strings.append("".join(current))
                        current = []
                if len(current) >= 4:
                    strings.append("".join(current))
            except Exception:
                pass
            print(f"\n{Colors.GREEN}[+] Found {len(strings)} UTF-16 strings:{Colors.RESET}\n")
            for s in strings[:50]:
                print(f"  {Colors.WHITE}{s}{Colors.RESET}")
        elif choice == "5":
            pattern = input(f"{Colors.YELLOW}Enter search pattern (hex or text): {Colors.RESET} ").strip()
            if not pattern:
                return
            try:
                if all(c in "0123456789abcdefABCDEF" for c in pattern):
                    search_bytes = bytes.fromhex(pattern)
                else:
                    search_bytes = pattern.encode("utf-8")
            except ValueError:
                search_bytes = pattern.encode("utf-8")
            positions = []
            start = 0
            while True:
                pos = self.loaded_data.find(search_bytes, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            if positions:
                print(f"\n{Colors.GREEN}[+] Found {len(positions)} occurrences at positions:{Colors.RESET}")
                for pos in positions[:20]:
                    print(f"  {Colors.WHITE}Offset 0x{pos:08x} ({pos}){Colors.RESET}")
                if len(positions) > 20:
                    print(f"  {Colors.YELLOW}... and {len(positions) - 20} more{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}[-] Pattern not found.{Colors.RESET}")
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def entropy_analysis(self):
        if not self.loaded_data:
            print(f"{Colors.RED}No data loaded.{Colors.RESET}")
            time.sleep(1)
            return
        self.print_header("Entropy Analysis")
        block_size = 256
        print(f"{Colors.CYAN}[*] Block size: {block_size} bytes{Colors.RESET}\n")
        print(f"  {Colors.CYAN}Offset         Entropy    Bar{Colors.RESET}")
        print(f"  {Colors.CYAN}{'-' * 60}{Colors.RESET}")
        for i in range(0, len(self.loaded_data), block_size):
            block = self.loaded_data[i:i+block_size]
            if len(block) < 32:
                continue
            ent = calculate_entropy(block)
            bar_len = int(ent / 8 * 30)
            bar = "#" * bar_len
            if ent > 7.5:
                color = Colors.RED
            elif ent > 6.0:
                color = Colors.YELLOW
            else:
                color = Colors.GREEN
            print(f"  {Colors.WHITE}0x{i:08x}  {ent:.4f}    {color}{bar}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Overall Entropy: {calculate_entropy(self.loaded_data):.4f} / 8.0000{Colors.RESET}")
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def string_search(self):
        self.print_header("String Search")
        search_term = input(f"{Colors.YELLOW}Enter string to search for: {Colors.RESET} ").strip()
        if not search_term:
            return
        try:
            search_bytes = search_term.encode("utf-8")
        except UnicodeEncodeError:
            print(f"{Colors.RED}Invalid search string.{Colors.RESET}")
            time.sleep(1)
            return
        positions = []
        start = 0
        while True:
            pos = self.loaded_data.find(search_bytes, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        if positions:
            print(f"\n{Colors.GREEN}[+] Found {len(positions)} occurrences of '{search_term}':{Colors.RESET}\n")
            for pos in positions:
                context_start = max(0, pos - 20)
                context_end = min(len(self.loaded_data), pos + len(search_bytes) + 20)
                context = self.loaded_data[context_start:context_end]
                context_str = context.decode("utf-8", errors="replace")
                print(f"  {Colors.WHITE}Offset 0x{pos:08x}: ...{context_str}...{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}[-] '{search_term}' not found in data.{Colors.RESET}")
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def crypto_menu(self):
        while True:
            self.print_header("Cryptography")
            if self.loaded_data:
                self.print_menu_option(1, "XOR Attack")
                self.print_menu_option(2, "AES Analysis")
                self.print_menu_option(3, "RSA Analysis")
                self.print_menu_option(4, "Hash Cracking")
                self.print_menu_option(0, "Back to Main Menu")
                choice = self.get_user_input("Choose an option:", ["0", "1", "2", "3", "4"])
            else:
                self.print_menu_option(1, "Load File First", color=Colors.RED)
                self.print_menu_option(0, "Back to Main Menu")
                choice = self.get_user_input("Choose an option:", ["0", "1"])
            if choice == "0":
                break
            elif choice == "1" and self.loaded_data:
                self.xor_attack_menu()
            elif choice == "2" and self.loaded_data:
                self.aes_attack_menu()
            elif choice == "3" and self.loaded_data:
                self.rsa_analysis_menu()
            elif choice == "4":
                self.hash_crack_menu()

    def xor_attack_menu(self):
        if not self.loaded_data:
            print(f"{Colors.RED}No data loaded.{Colors.RESET}")
            time.sleep(1)
            return
        while True:
            self.print_header("XOR Attack")
            self.print_menu_option(1, "Single-byte XOR brute force")
            self.print_menu_option(2, "Multi-byte XOR analysis")
            self.print_menu_option(3, "Known plaintext attack")
            self.print_menu_option(4, "XOR with custom key")
            self.print_menu_option(5, "Try common keys")
            self.print_menu_option(0, "Back")
            choice = self.get_user_input("Choose an option:", ["0", "1", "2", "3", "4", "5"])
            if choice == "0":
                break
            elif choice == "1":
                print(f"\n{Colors.CYAN}[*] Trying all 256 single-byte XOR keys...{Colors.RESET}\n")
                results = self.xor_engine.single_byte_xor(self.loaded_data)
                for r in results[:10]:
                    print(f"  {Colors.GREEN}Key: {r['key_hex']}  Score: {r['score']:.2f}{Colors.RESET}")
                    print(f"  {Colors.WHITE}{r['decrypted'][:100]}{Colors.RESET}\n")
            elif choice == "2":
                key_size = input(f"{Colors.YELLOW}Enter key size (1-50): {Colors.RESET} ").strip()
                try:
                    key_size = int(key_size)
                    if key_size < 1 or key_size > 50:
                        raise ValueError
                except ValueError:
                    print(f"{Colors.RED}Invalid key size.{Colors.RESET}")
                    time.sleep(1)
                    continue
                multi_results = self.xor_engine.multi_byte_xor(self.loaded_data, key_size)
                if multi_results:
                    best = multi_results[0]
                    decrypted = best['decrypted']
                    key = best['key']
                    print(f"\n{Colors.GREEN}[+] Key found: {key.hex()}{Colors.RESET}")
                    print(f"{Colors.WHITE}{decrypted.decode('utf-8', errors='replace')[:200]}{Colors.RESET}\n")
                    save = input(f"{Colors.YELLOW}Save decrypted data? (y/n): {Colors.RESET} ").strip().lower()
                    if save == "y":
                        output_path = os.path.join(self.output_dir, "xor_decrypted.bin")
                        with open(output_path, "wb") as f:
                            f.write(decrypted)
                        print(f"{Colors.GREEN}[+] Saved to {output_path}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[-] Could not find XOR key.{Colors.RESET}")
            elif choice == "3":
                known = input(f"{Colors.YELLOW}Enter known plaintext: {Colors.RESET} ").strip()
                if not known:
                    continue
                known_bytes = known.encode("utf-8")
                if len(known_bytes) > len(self.loaded_data):
                    print(f"{Colors.RED}Plaintext longer than data.{Colors.RESET}")
                    time.sleep(1)
                    continue
                key = bytearray(len(known_bytes))
                for i in range(len(known_bytes)):
                    key[i] = self.loaded_data[i] ^ known_bytes[i]
                print(f"\n{Colors.GREEN}[+] Derived key: {bytes(key).hex()}{Colors.RESET}")
                print(f"{Colors.GREEN}[+] Key as text: {bytes(key).decode('utf-8', errors='replace')}{Colors.RESET}\n")
                full_decrypt = xor_bytes(self.loaded_data, bytes(key))
                print(f"{Colors.WHITE}{full_decrypt.decode('utf-8', errors='replace')[:200]}{Colors.RESET}\n")
            elif choice == "4":
                key_input = input(f"{Colors.YELLOW}Enter XOR key (hex or text): {Colors.RESET} ").strip()
                if not key_input:
                    continue
                try:
                    if all(c in "0123456789abcdefABCDEF" for c in key_input):
                        key = bytes.fromhex(key_input)
                    else:
                        key = key_input.encode("utf-8")
                except ValueError:
                    key = key_input.encode("utf-8")
                decrypted = xor_bytes(self.loaded_data, key)
                print(f"\n{Colors.GREEN}[+] Decrypted with key: {key.hex()}{Colors.RESET}")
                print(f"{Colors.WHITE}{decrypted.decode('utf-8', errors='replace')[:300]}{Colors.RESET}\n")
                save = input(f"{Colors.YELLOW}Save decrypted data? (y/n): {Colors.RESET} ").strip().lower()
                if save == "y":
                    output_path = os.path.join(self.output_dir, "xor_custom_decrypted.bin")
                    with open(output_path, "wb") as f:
                        f.write(decrypted)
                    print(f"{Colors.GREEN}[+] Saved to {output_path}{Colors.RESET}")
            elif choice == "5":
                print(f"\n{Colors.CYAN}[*] Trying common keys...{Colors.RESET}\n")
                for key in COMMON_KEYS[:20]:
                    decrypted = xor_bytes(self.loaded_data, key)
                    printable_ratio = sum(1 for b in decrypted if b in range(32, 127)) / len(decrypted)
                    if printable_ratio > 0.7:
                        print(f"  {Colors.GREEN}Key: {key.decode('utf-8', errors='replace')} (printable: {printable_ratio:.2%}){Colors.RESET}")
                        print(f"  {Colors.WHITE}{decrypted.decode('utf-8', errors='replace')[:100]}{Colors.RESET}\n")
            print(f"{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
            input()

    def aes_attack_menu(self):
        if not self.loaded_data:
            print(f"{Colors.RED}No data loaded.{Colors.RESET}")
            time.sleep(1)
            return
        self.print_header("AES Analysis")
        entropy = calculate_entropy(self.loaded_data)
        print(f"{Colors.CYAN}[*] Data entropy: {entropy:.4f}{Colors.RESET}")
        if entropy > 7.5:
            print(f"{Colors.YELLOW}[~] High entropy suggests encryption or compression{Colors.RESET}")
        if len(self.loaded_data) % 16 == 0:
            print(f"{Colors.GREEN}[+] Data length is a multiple of 16 (AES block size){Colors.RESET}")
        else:
            print(f"{Colors.RED}[-] Data length is NOT a multiple of 16{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Possible AES modes:{Colors.RESET}")
        if len(self.loaded_data) >= 16:
            blocks = [self.loaded_data[i:i+16] for i in range(0, len(self.loaded_data), 16)]
            unique_blocks = set(blocks)
            print(f"  {Colors.CYAN}Total blocks:{Colors.RESET} {len(blocks)}")
            print(f"  {Colors.CYAN}Unique blocks:{Colors.RESET} {len(unique_blocks)}")
            if len(unique_blocks) < len(blocks) * 0.9:
                print(f"  {Colors.YELLOW}[~] Repeated blocks detected - possible ECB mode{Colors.RESET}")
            else:
                print(f"  {Colors.GREEN}[+] No repeated blocks - likely CBC/CTR mode{Colors.RESET}")
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def hash_crack_menu(self):
        while True:
            self.print_header("Hash Cracking")
            self.print_menu_option(1, "Identify hash type")
            self.print_menu_option(2, "Crack hash with wordlist")
            self.print_menu_option(3, "Brute force hash")
            self.print_menu_option(4, "Generate hash from text")
            self.print_menu_option(0, "Back")
            choice = self.get_user_input("Choose an option:", ["0", "1", "2", "3", "4"])
            if choice == "0":
                break
            elif choice == "1":
                hash_str = input(f"{Colors.YELLOW}Enter hash: {Colors.RESET} ").strip()
                if hash_str:
                    self.hash_cracker.identify_hash(hash_str)
            elif choice == "2":
                hash_str = input(f"{Colors.YELLOW}Enter hash: {Colors.RESET} ").strip()
                if hash_str:
                    wordlist = input(f"{Colors.YELLOW}Wordlist path (empty for default): {Colors.RESET} ").strip()
                    if wordlist and os.path.exists(wordlist):
                        self.hash_cracker.crack_hash(hash_str, wordlist_path=wordlist)
                    else:
                        self.hash_cracker.crack_hash(hash_str)
            elif choice == "3":
                hash_str = input(f"{Colors.YELLOW}Enter hash: {Colors.RESET} ").strip()
                if hash_str:
                    max_len = input(f"{Colors.YELLOW}Max length (default 4): {Colors.RESET} ").strip()
                    try:
                        max_len = int(max_len) if max_len else 4
                    except ValueError:
                        max_len = 4
                    self.hash_cracker.brute_force(hash_str, max_length=max_len)
            elif choice == "4":
                text = input(f"{Colors.YELLOW}Enter text: {Colors.RESET} ").strip()
                if text:
                    print(f"\n{Colors.YELLOW}Hash values:{Colors.RESET}")
                    print(f"  {Colors.CYAN}MD5:    {hashlib.md5(text.encode()).hexdigest()}{Colors.RESET}")
                    print(f"  {Colors.CYAN}SHA1:   {hashlib.sha1(text.encode()).hexdigest()}{Colors.RESET}")
                    print(f"  {Colors.CYAN}SHA256: {hashlib.sha256(text.encode()).hexdigest()}{Colors.RESET}")
                    print(f"  {Colors.CYAN}SHA512: {hashlib.sha512(text.encode()).hexdigest()}{Colors.RESET}")
            print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
            input()

    def decode_menu(self):
        while True:
            self.print_header("Encode/Decode")
            if self.loaded_data:
                self.print_menu_option(1, "Base64 Decode")
                self.print_menu_option(2, "Base64 Encode")
                self.print_menu_option(3, "Hex Decode")
                self.print_menu_option(4, "Hex Encode")
                self.print_menu_option(5, "URL Decode")
                self.print_menu_option(6, "URL Encode")
                self.print_menu_option(7, "ROT13")
                self.print_menu_option(8, "Auto Detect Encoding")
                self.print_menu_option(0, "Back to Main Menu")
                choice = self.get_user_input("Choose an option:", ["0", "1", "2", "3", "4", "5", "6", "7", "8"])
            else:
                self.print_menu_option(1, "Load File First", color=Colors.RED)
                self.print_menu_option(0, "Back to Main Menu")
                choice = self.get_user_input("Choose an option:", ["0", "1"])
            if choice == "0":
                break
            elif choice == "1":
                try:
                    decoded = base64.b64decode(self.loaded_data)
                    print(f"\n{Colors.GREEN}[+] Base64 decoded ({len(decoded)} bytes){Colors.RESET}")
                    print(f"{Colors.WHITE}{decoded.decode('utf-8', errors='replace')[:500]}{Colors.RESET}\n")
                except Exception as e:
                    print(f"{Colors.RED}[-] Base64 decode failed: {e}{Colors.RESET}")
            elif choice == "2":
                try:
                    encoded = base64.b64encode(self.loaded_data)
                    print(f"\n{Colors.GREEN}[+] Base64 encoded ({len(encoded)} bytes){Colors.RESET}")
                    print(f"{Colors.WHITE}{encoded.decode('utf-8')[:500]}{Colors.RESET}\n")
                except Exception as e:
                    print(f"{Colors.RED}[-] Base64 encode failed: {e}{Colors.RESET}")
            elif choice == "3":
                try:
                    hex_str = self.loaded_data.decode("utf-8").strip()
                    decoded = bytes.fromhex(hex_str)
                    print(f"\n{Colors.GREEN}[+] Hex decoded ({len(decoded)} bytes){Colors.RESET}")
                    print(f"{Colors.WHITE}{decoded.decode('utf-8', errors='replace')[:500]}{Colors.RESET}\n")
                except Exception as e:
                    print(f"{Colors.RED}[-] Hex decode failed: {e}{Colors.RESET}")
            elif choice == "4":
                encoded = self.loaded_data.hex()
                print(f"\n{Colors.GREEN}[+] Hex encoded ({len(encoded)} chars){Colors.RESET}")
                print(f"{Colors.WHITE}{encoded[:500]}{Colors.RESET}\n")
            elif choice == "5":
                try:
                    from urllib.parse import unquote
                    text = self.loaded_data.decode("utf-8", errors="replace")
                    decoded = unquote(text)
                    print(f"\n{Colors.GREEN}[+] URL decoded:{Colors.RESET}")
                    print(f"{Colors.WHITE}{decoded[:500]}{Colors.RESET}\n")
                except Exception as e:
                    print(f"{Colors.RED}[-] URL decode failed: {e}{Colors.RESET}")
            elif choice == "6":
                try:
                    from urllib.parse import quote
                    text = self.loaded_data.decode("utf-8", errors="replace")
                    encoded = quote(text)
                    print(f"\n{Colors.GREEN}[+] URL encoded:{Colors.RESET}")
                    print(f"{Colors.WHITE}{encoded[:500]}{Colors.RESET}\n")
                except Exception as e:
                    print(f"{Colors.RED}[-] URL encode failed: {e}{Colors.RESET}")
            elif choice == "7":
                try:
                    text = self.loaded_data.decode("utf-8", errors="replace")
                    result = []
                    for char in text:
                        if "a" <= char <= "z":
                            result.append(chr((ord(char) - 97 + 13) % 26 + 97))
                        elif "A" <= char <= "Z":
                            result.append(chr((ord(char) - 65 + 13) % 26 + 65))
                        else:
                            result.append(char)
                    print(f"\n{Colors.GREEN}[+] ROT13:{Colors.RESET}")
                    print(f"{Colors.WHITE}{''.join(result)[:500]}{Colors.RESET}\n")
                except Exception as e:
                    print(f"{Colors.RED}[-] ROT13 failed: {e}{Colors.RESET}")
            elif choice == "8":
                print(f"\n{Colors.CYAN}[*] Auto-detecting encoding...{Colors.RESET}\n")
                try:
                    text = self.loaded_data.decode("utf-8")
                    print(f"  {Colors.GREEN}[+] Valid UTF-8{Colors.RESET}")
                except UnicodeDecodeError:
                    print(f"  {Colors.RED}[-] Not valid UTF-8{Colors.RESET}")
                try:
                    text = self.loaded_data.decode("latin-1")
                    print(f"  {Colors.GREEN}[+] Valid Latin-1{Colors.RESET}")
                except UnicodeDecodeError:
                    print(f"  {Colors.RED}[-] Not valid Latin-1{Colors.RESET}")
                try:
                    decoded = base64.b64decode(self.loaded_data, validate=True)
                    print(f"  {Colors.GREEN}[+] Valid Base64{Colors.RESET}")
                except Exception:
                    print(f"  {Colors.RED}[-] Not valid Base64{Colors.RESET}")
                try:
                    hex_str = self.loaded_data.decode("utf-8").strip()
                    bytes.fromhex(hex_str)
                    print(f"  {Colors.GREEN}[+] Valid Hex{Colors.RESET}")
                except Exception:
                    print(f"  {Colors.RED}[-] Not valid Hex{Colors.RESET}")
            print(f"{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
            input()

    def decompress_menu(self):
        while True:
            self.print_header("Decompression")
            if self.loaded_data:
                detected = self.decompressor.detect_compression(self.loaded_data)
                self.print_menu_option(1, f"Auto Decompress (detected: {detected})")
                self.print_menu_option(2, "Decompress GZIP")
                self.print_menu_option(3, "Decompress ZIP")
                self.print_menu_option(4, "Decompress BZ2")
                self.print_menu_option(5, "Decompress LZMA")
                self.print_menu_option(6, "Decompress ZLIB")
                self.print_menu_option(0, "Back to Main Menu")
                choice = self.get_user_input("Choose an option:", ["0", "1", "2", "3", "4", "5", "6"])
            else:
                self.print_menu_option(1, "Load File First", color=Colors.RED)
                self.print_menu_option(0, "Back to Main Menu")
                choice = self.get_user_input("Choose an option:", ["0", "1"])
            if choice == "0":
                break
            elif choice == "1":
                results = self.decompressor.decompress_all(self.loaded_data)
                if results:
                    for name, data in results:
                        print(f"\n{Colors.GREEN}[+] {name} decompressed: {len(data)} bytes{Colors.RESET}")
                        entropy = calculate_entropy(data)
                        print(f"  {Colors.CYAN}Entropy: {entropy:.4f}{Colors.RESET}")
                        if is_printable(data.decode("utf-8", errors="ignore")):
                            print(f"  {Colors.WHITE}{data.decode('utf-8', errors='replace')[:200]}{Colors.RESET}")
                        output_path = os.path.join(self.output_dir, f"decompressed_{name}.bin")
                        with open(output_path, "wb") as f:
                            f.write(data)
                        print(f"  {Colors.GREEN}[+] Saved to {output_path}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[-] No decompression succeeded.{Colors.RESET}")
            elif choice == "2":
                result = self.decompressor.decompress_gzip(self.loaded_data)
                if result:
                    print(f"\n{Colors.GREEN}[+] GZIP decompressed: {len(result)} bytes{Colors.RESET}")
                    output_path = os.path.join(self.output_dir, "decompressed_gz.bin")
                    with open(output_path, "wb") as f:
                        f.write(result)
                    print(f"  {Colors.GREEN}[+] Saved to {output_path}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[-] GZIP decompression failed.{Colors.RESET}")
            elif choice == "3":
                results = self.decompressor.decompress_zip(self.loaded_data)
                if results:
                    for name, data in results:
                        print(f"\n{Colors.GREEN}[+] Extracted: {name} ({len(data)} bytes){Colors.RESET}")
                        output_path = os.path.join(self.output_dir, f"extracted_{name}")
                        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else self.output_dir, exist_ok=True)
                        with open(output_path, "wb") as f:
                            f.write(data)
                        print(f"  {Colors.GREEN}[+] Saved to {output_path}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[-] ZIP extraction failed.{Colors.RESET}")
            elif choice == "4":
                result = self.decompressor.decompress_bz2(self.loaded_data)
                if result:
                    print(f"\n{Colors.GREEN}[+] BZ2 decompressed: {len(result)} bytes{Colors.RESET}")
                    output_path = os.path.join(self.output_dir, "decompressed_bz2.bin")
                    with open(output_path, "wb") as f:
                        f.write(result)
                    print(f"  {Colors.GREEN}[+] Saved to {output_path}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[-] BZ2 decompression failed.{Colors.RESET}")
            elif choice == "5":
                result = self.decompressor.decompress_lzma(self.loaded_data)
                if result:
                    print(f"\n{Colors.GREEN}[+] LZMA decompressed: {len(result)} bytes{Colors.RESET}")
                    output_path = os.path.join(self.output_dir, "decompressed_lzma.bin")
                    with open(output_path, "wb") as f:
                        f.write(result)
                    print(f"  {Colors.GREEN}[+] Saved to {output_path}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[-] LZMA decompression failed.{Colors.RESET}")
            elif choice == "6":
                result = self.decompressor.decompress_zlib(self.loaded_data)
                if result:
                    print(f"\n{Colors.GREEN}[+] ZLIB decompressed: {len(result)} bytes{Colors.RESET}")
                    output_path = os.path.join(self.output_dir, "decompressed_zlib.bin")
                    with open(output_path, "wb") as f:
                        f.write(result)
                    print(f"  {Colors.GREEN}[+] Saved to {output_path}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}[-] ZLIB decompression failed.{Colors.RESET}")
            print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
            input()

    def rsa_analysis_menu(self):
        if not self.loaded_data:
            print(f"{Colors.RED}No data loaded.{Colors.RESET}")
            time.sleep(1)
            return
        self.print_header("RSA Analysis")
        print(f"{Colors.CYAN}[*] Analyzing data for RSA indicators...{Colors.RESET}\n")
        text = self.loaded_data.decode("utf-8", errors="ignore")
        if "BEGIN RSA PUBLIC KEY" in text or "BEGIN PUBLIC KEY" in text:
            print(f"{Colors.GREEN}[+] PEM-encoded RSA public key detected{Colors.RESET}")
        if "BEGIN RSA PRIVATE KEY" in text or "BEGIN PRIVATE KEY" in text:
            print(f"{Colors.RED}[!] PEM-encoded RSA private key detected!{Colors.RESET}")
        if b"\x30\x82" in self.loaded_data[:10]:
            print(f"{Colors.GREEN}[+] Possible DER-encoded ASN.1 structure{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Looking for large prime-like numbers...{Colors.RESET}")
        for i in range(0, len(self.loaded_data) - 128, 64):
            chunk = self.loaded_data[i:i+128]
            chunk_entropy = calculate_entropy(chunk)
            if chunk_entropy > 7.0:
                print(f"  {Colors.YELLOW}[~] High-entropy block at 0x{i:08x} (entropy: {chunk_entropy:.4f}){Colors.RESET}")
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def tools_menu(self):
        while True:
            self.print_header("Tools")
            self.print_menu_option(1, "Compare Files")
            self.print_menu_option(2, "Generate Hash")
            self.print_menu_option(3, "Analyze File Entropy")
            self.print_menu_option(4, "Extract Metadata")
            self.print_menu_option(5, "Generate Report")
            self.print_menu_option(0, "Back to Main Menu")
            choice = self.get_user_input("Choose an option:", ["0", "1", "2", "3", "4", "5"])
            if choice == "0":
                break
            elif choice == "1":
                self.compare_files()
            elif choice == "2":
                self.generate_hash()
            elif choice == "3":
                self.analyze_file_entropy()
            elif choice == "4":
                self.extract_metadata()
            elif choice == "5":
                self.generate_report()

    def compare_files(self):
        self.print_header("Compare Files")
        file1 = input(f"{Colors.YELLOW}Enter first file path: {Colors.RESET} ").strip()
        file2 = input(f"{Colors.YELLOW}Enter second file path: {Colors.RESET} ").strip()
        if not file1 or not file2:
            return
        file1 = os.path.expanduser(file1)
        file2 = os.path.expanduser(file2)
        if not os.path.exists(file1):
            print(f"{Colors.RED}File not found: {file1}{Colors.RESET}")
            time.sleep(1)
            return
        if not os.path.exists(file2):
            print(f"{Colors.RED}File not found: {file2}{Colors.RESET}")
            time.sleep(1)
            return
        try:
            with open(file1, "rb") as f:
                data1 = f.read()
            with open(file2, "rb") as f:
                data2 = f.read()
            print(f"\n{Colors.YELLOW}File Comparison:{Colors.RESET}")
            print(f"  {Colors.CYAN}File 1:{Colors.RESET} {file1} ({len(data1)} bytes)")
            print(f"  {Colors.CYAN}File 2:{Colors.RESET} {file2} ({len(data2)} bytes)")
            print(f"  {Colors.CYAN}Size difference:{Colors.RESET} {len(data1) - len(data2)} bytes")
            hash1 = hashlib.md5(data1).hexdigest()
            hash2 = hashlib.md5(data2).hexdigest()
            if hash1 == hash2:
                print(f"  {Colors.GREEN}[+] Files are identical (MD5: {hash1}){Colors.RESET}")
            else:
                print(f"  {Colors.RED}[-] Files differ{Colors.RESET}")
                print(f"    {Colors.CYAN}MD5 File 1:{Colors.RESET} {hash1}")
                print(f"    {Colors.CYAN}MD5 File 2:{Colors.RESET} {hash2}")
                diff_count = sum(1 for a, b in zip(data1, data2) if a != b)
                print(f"    {Colors.CYAN}Byte differences:{Colors.RESET} {diff_count}")
                first_diff = None
                for i, (a, b) in enumerate(zip(data1, data2)):
                    if a != b:
                        first_diff = i
                        break
                if first_diff is not None:
                    print(f"    {Colors.CYAN}First difference at:{Colors.RESET} offset 0x{first_diff:08x}")
        except Exception as e:
            print(f"{Colors.RED}Error comparing files: {e}{Colors.RESET}")
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def generate_hash(self):
        self.print_header("Generate Hash")
        text = input(f"{Colors.YELLOW}Enter text to hash: {Colors.RESET} ").strip()
        if not text:
            return
        print(f"\n{Colors.YELLOW}Hash values for '{text}':{Colors.RESET}\n")
        print(f"  {Colors.CYAN}MD5:    {hashlib.md5(text.encode()).hexdigest()}{Colors.RESET}")
        print(f"  {Colors.CYAN}SHA1:   {hashlib.sha1(text.encode()).hexdigest()}{Colors.RESET}")
        print(f"  {Colors.CYAN}SHA224: {hashlib.sha224(text.encode()).hexdigest()}{Colors.RESET}")
        print(f"  {Colors.CYAN}SHA256: {hashlib.sha256(text.encode()).hexdigest()}{Colors.RESET}")
        print(f"  {Colors.CYAN}SHA384: {hashlib.sha384(text.encode()).hexdigest()}{Colors.RESET}")
        print(f"  {Colors.CYAN}SHA512: {hashlib.sha512(text.encode()).hexdigest()}{Colors.RESET}")
        try:
            ntlm = hashlib.new("md4", text.encode("utf-16le")).hexdigest()
            print(f"  {Colors.CYAN}NTLM:   {ntlm}{Colors.RESET}")
        except Exception:
            pass
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def analyze_file_entropy(self):
        self.print_header("File Entropy Analysis")
        filepath = input(f"{Colors.YELLOW}Enter file path: {Colors.RESET} ").strip()
        if not filepath:
            return
        filepath = os.path.expanduser(filepath)
        if not os.path.exists(filepath):
            print(f"{Colors.RED}File not found: {filepath}{Colors.RESET}")
            time.sleep(1)
            return
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            entropy = calculate_entropy(data)
            print(f"\n{Colors.YELLOW}Entropy Analysis for: {filepath}{Colors.RESET}")
            print(f"  {Colors.CYAN}Size:{Colors.RESET} {len(data)} bytes")
            print(f"  {Colors.CYAN}Entropy:{Colors.RESET} {entropy:.4f} / 8.0000")
            if entropy > 7.5:
                print(f"  {Colors.RED}[!] Very high - likely encrypted or compressed{Colors.RESET}")
            elif entropy > 6.5:
                print(f"  {Colors.YELLOW}[~] High - possibly encoded{Colors.RESET}")
            elif entropy > 4.0:
                print(f"  {Colors.GREEN}[+] Medium - mixed content{Colors.RESET}")
            else:
                print(f"  {Colors.GREEN}[+] Low - structured data or plaintext{Colors.RESET}")
            block_size = 1024
            print(f"\n{Colors.YELLOW}Block Entropy (block size: {block_size}):{Colors.RESET}")
            for i in range(0, len(data), block_size):
                block = data[i:i+block_size]
                if len(block) < 32:
                    continue
                block_entropy = calculate_entropy(block)
                bar = "#" * int(block_entropy / 8 * 20)
                print(f"  0x{i:08x}: {block_entropy:.4f} {bar}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def extract_metadata(self):
        if not self.loaded_data:
            print(f"{Colors.RED}No data loaded.{Colors.RESET}")
            time.sleep(1)
            return
        self.print_header("Metadata Extraction")
        print(f"{Colors.YELLOW}File Metadata:{Colors.RESET}")
        print(f"  {Colors.CYAN}Filename:{Colors.RESET} {os.path.basename(self.loaded_file) if self.loaded_file else 'N/A'}")
        print(f"  {Colors.CYAN}Path:{Colors.RESET} {self.loaded_file or 'N/A'}")
        print(f"  {Colors.CYAN}Size:{Colors.RESET} {len(self.loaded_data)} bytes")
        print(f"  {Colors.CYAN}MD5:{Colors.RESET} {hashlib.md5(self.loaded_data).hexdigest()}")
        print(f"  {Colors.CYAN}SHA1:{Colors.RESET} {hashlib.sha1(self.loaded_data).hexdigest()}")
        print(f"  {Colors.CYAN}SHA256:{Colors.RESET} {hashlib.sha256(self.loaded_data).hexdigest()}")
        print(f"  {Colors.CYAN}Entropy:{Colors.RESET} {calculate_entropy(self.loaded_data):.4f}")
        if self.loaded_file and os.path.exists(self.loaded_file):
            stat = os.stat(self.loaded_file)
            print(f"  {Colors.CYAN}Created:{Colors.RESET} {time.ctime(stat.st_ctime)}")
            print(f"  {Colors.CYAN}Modified:{Colors.RESET} {time.ctime(stat.st_mtime)}")
            print(f"  {Colors.CYAN}Accessed:{Colors.RESET} {time.ctime(stat.st_atime)}")
        print(f"\n{Colors.YELLOW}File Type Detection:{Colors.RESET}")
        detected = False
        for magic, ftype in MAGIC_NUMBERS.items():
            if self.loaded_data[:len(magic)] == magic:
                print(f"  {Colors.GREEN}[+] {ftype}{Colors.RESET}")
                detected = True
        if not detected:
            print(f"  {Colors.YELLOW}[~] Unknown type{Colors.RESET}")
        strings = self.extract_strings(self.loaded_data, min_length=4)
        print(f"\n{Colors.YELLOW}Strings Found:{Colors.RESET} {len(strings)}")
        if strings:
            print(f"  {Colors.CYAN}Sample strings:{Colors.RESET}")
            for s in strings[:10]:
                print(f"    {Colors.WHITE}{s}{Colors.RESET}")
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def generate_report(self):
        if not self.loaded_data:
            print(f"{Colors.RED}No data loaded.{Colors.RESET}")
            time.sleep(1)
            return
        self.print_header("Generate Report")
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("Reverser X Supreme - Analysis Report")
        report_lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 60)
        report_lines.append("")
        report_lines.append("FILE INFORMATION")
        report_lines.append("-" * 40)
        report_lines.append(f"Filename: {os.path.basename(self.loaded_file) if self.loaded_file else 'N/A'}")
        report_lines.append(f"Path: {self.loaded_file or 'N/A'}")
        report_lines.append(f"Size: {len(self.loaded_data)} bytes")
        report_lines.append(f"MD5: {hashlib.md5(self.loaded_data).hexdigest()}")
        report_lines.append(f"SHA256: {hashlib.sha256(self.loaded_data).hexdigest()}")
        report_lines.append(f"Entropy: {calculate_entropy(self.loaded_data):.4f}")
        report_lines.append("")
        report_lines.append("FILE TYPE DETECTION")
        report_lines.append("-" * 40)
        detected = False
        for magic, ftype in MAGIC_NUMBERS.items():
            if self.loaded_data[:len(magic)] == magic:
                report_lines.append(f"Detected: {ftype}")
                detected = True
        if not detected:
            report_lines.append("Type: Unknown")
        report_lines.append("")
        report_lines.append("STRINGS EXTRACTED")
        report_lines.append("-" * 40)
        strings = self.extract_strings(self.loaded_data, min_length=4)
        report_lines.append(f"Total strings found: {len(strings)}")
        for s in strings[:50]:
            report_lines.append(f"  {s}")
        if len(strings) > 50:
            report_lines.append(f"  ... and {len(strings) - 50} more")
        report_lines.append("")
        report_lines.append("PATTERN ANALYSIS")
        report_lines.append("-" * 40)
        patterns = find_repeating_patterns(self.loaded_data)
        report_lines.append(f"Repeating patterns found: {len(patterns)}")
        for pattern, count in patterns[:10]:
            report_lines.append(f"  '{pattern.decode('utf-8', errors='replace')}' x{count}")
        report_lines.append("")
        report_lines.append("=" * 60)
        report_lines.append("End of Report")
        report_lines.append("=" * 60)
        report_text = "\n".join(report_lines)
        report_path = os.path.join(self.output_dir, f"report_{int(time.time())}.txt")
        try:
            with open(report_path, "w") as f:
                f.write(report_text)
            print(f"{Colors.GREEN}[+] Report saved to {report_path}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[-] Failed to save report: {e}{Colors.RESET}")
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def settings_menu(self):
        while True:
            self.print_header("Settings")
            self.print_menu_option(1, f"Output Directory: {self.output_dir}")
            self.print_menu_option(2, f"Verbose Mode: {self.config.get('verbose', True)}")
            self.print_menu_option(3, f"Save Logs: {self.config.get('save_logs', True)}")
            self.print_menu_option(4, f"Entropy Threshold: {self.config.get('entropy_threshold', 7.5)}")
            self.print_menu_option(5, f"XOR Max Key Size: {self.config.get('xor_max_key_size', 50)}")
            self.print_menu_option(0, "Back to Main Menu")
            choice = self.get_user_input("Choose an option:", ["0", "1", "2", "3", "4", "5"])
            if choice == "0":
                break
            elif choice == "1":
                new_dir = input(f"{Colors.YELLOW}Enter new output directory: {Colors.RESET} ").strip()
                if new_dir:
                    self.output_dir = new_dir
                    os.makedirs(self.output_dir, exist_ok=True)
                    print(f"{Colors.GREEN}[+] Output directory set to {self.output_dir}{Colors.RESET}")
            elif choice == "2":
                current = self.config.get("verbose", True)
                self.config["verbose"] = not current
                print(f"{Colors.GREEN}[+] Verbose mode: {self.config['verbose']}{Colors.RESET}")
            elif choice == "3":
                current = self.config.get("save_logs", True)
                self.config["save_logs"] = not current
                print(f"{Colors.GREEN}[+] Save logs: {self.config['save_logs']}{Colors.RESET}")
            elif choice == "4":
                threshold = input(f"{Colors.YELLOW}Enter new entropy threshold (0-8): {Colors.RESET} ").strip()
                try:
                    threshold = float(threshold)
                    if 0 <= threshold <= 8:
                        self.config["entropy_threshold"] = threshold
                        print(f"{Colors.GREEN}[+] Entropy threshold set to {threshold}{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}Value must be between 0 and 8.{Colors.RESET}")
                except ValueError:
                    print(f"{Colors.RED}Invalid value.{Colors.RESET}")
            elif choice == "5":
                key_size = input(f"{Colors.YELLOW}Enter XOR max key size (1-100): {Colors.RESET} ").strip()
                try:
                    key_size = int(key_size)
                    if 1 <= key_size <= 100:
                        self.config["xor_max_key_size"] = key_size
                        print(f"{Colors.GREEN}[+] XOR max key size set to {key_size}{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}Value must be between 1 and 100.{Colors.RESET}")
                except ValueError:
                    print(f"{Colors.RED}Invalid value.{Colors.RESET}")
            time.sleep(1)

    def about_menu(self):
        self.print_header("About")
        print(f"  {Colors.BOLD}Reverser X Supreme{Colors.RESET}")
        print(f"  Version: {Colors.GREEN}{VERSION}{Colors.RESET}")
        print(f"  Description: Advanced reverse engineering toolkit")
        print(f"\n  {Colors.YELLOW}Features:{Colors.RESET}")
        print(f"    - File analysis and identification")
        print(f"    - Entropy analysis")
        print(f"    - String extraction")
        print(f"    - XOR cryptanalysis")
        print(f"    - AES analysis")
        print(f"    - Hash cracking")
        print(f"    - Encoding/decoding")
        print(f"    - Decompression")
        print(f"    - RSA analysis")
        print(f"    - File comparison")
        print(f"    - Report generation")
        print(f"\n  {Colors.YELLOW}Core Modules:{Colors.RESET}")
        print(f"    - ReverserEngine")
        print(f"    - AdvancedAnalyzer")
        print(f"    - CryptoBreaker")
        print(f"    - HashCracker")
        print(f"    - DecompressorEngine")
        print(f"    - EncoderDecoder")
        print(f"    - XORAttackEngine")
        print(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}", end="")
        input()

    def run(self):
        while True:
            self.print_header()
            print(f"  {Colors.CYAN}Loaded:{Colors.RESET} {self.loaded_file or 'No file loaded'}")
            if self.loaded_data:
                print(f"  {Colors.CYAN}Size:{Colors.RESET} {len(self.loaded_data)} bytes")
                print(f"  {Colors.CYAN}Entropy:{Colors.RESET} {calculate_entropy(self.loaded_data):.4f}")
            print()
            self.print_menu_option(1, "Load File")
            self.print_menu_option(2, "Load Example Data")
            self.print_menu_option(3, "Analysis")
            self.print_menu_option(4, "Cryptography")
            self.print_menu_option(5, "Encode/Decode")
            self.print_menu_option(6, "Decompression")
            self.print_menu_option(7, "Tools")
            self.print_menu_option(8, "Settings")
            self.print_menu_option(9, "About")
            self.print_menu_option(0, "Exit", color=Colors.RED)
            print()
            choice = self.get_user_input("Choose an option:", ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
            if choice == "0":
                print(f"\n{Colors.GREEN}[+] Goodbye!{Colors.RESET}")
                break
            elif choice == "1":
                self.load_file_menu()
            elif choice == "2":
                self.load_example_menu()
            elif choice == "3":
                self.analysis_menu()
            elif choice == "4":
                self.crypto_menu()
            elif choice == "5":
                self.decode_menu()
            elif choice == "6":
                self.decompress_menu()
            elif choice == "7":
                self.tools_menu()
            elif choice == "8":
                self.settings_menu()
            elif choice == "9":
                self.about_menu()
