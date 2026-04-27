import hashlib
import string
import os
from typing import List, Dict, Optional
from itertools import product

from utils.constants import Colors
from utils.helpers import calculate_entropy


HASH_LENGTH_MAP = {
    32: ["md5", "ntlm"],
    40: ["sha1"],
    56: ["sha224"],
    64: ["sha256"],
    96: ["sha384"],
    128: ["sha512"],
}

HASH_ALGORITHMS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
    "ntlm": lambda s: hashlib.new("md4", s.encode("utf-16le")).hexdigest(),
}


class HashCracker:
    def __init__(self, config=None):
        self.config = config or {}
        self.wordlist_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "wordlists"
        )
        self.default_charset = string.ascii_lowercase + string.digits

    def identify_hash(self, hash_str: str) -> List[str]:
        hash_str = hash_str.strip()
        length = len(hash_str)
        possible_types = HASH_LENGTH_MAP.get(length, [])
        if not possible_types:
            return []
        return possible_types

    def _hash_string(self, text: str, algorithm: str) -> str:
        algorithm = algorithm.lower()
        if algorithm not in HASH_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        return HASH_ALGORITHMS[algorithm](text).hexdigest()

    def crack_hash(self, hash_str: str, wordlist_path: str = None) -> Optional[str]:
        hash_str = hash_str.strip().lower()
        possible_types = self.identify_hash(hash_str)
        if not possible_types:
            return None

        if wordlist_path is None:
            for filename in ["common.txt", "common_passwords.txt", "rockyou.txt", "rockyou_sample.txt"]:
                candidate = os.path.join(self.wordlist_dir, filename)
                if os.path.exists(candidate):
                    wordlist_path = candidate
                    break
            if wordlist_path is None or not os.path.exists(wordlist_path):
                print(f"{Colors.RED}No wordlist found in {self.wordlist_dir}{Colors.RESET}")
                return None

        if not os.path.exists(wordlist_path):
            print(f"{Colors.RED}Wordlist not found: {wordlist_path}{Colors.RESET}")
            return None

        print(f"{Colors.YELLOW}Cracking hash: {hash_str[:16]}...{Colors.RESET}")
        print(f"{Colors.YELLOW}Using wordlist: {wordlist_path}{Colors.RESET}")

        total_lines = 0
        with open(wordlist_path, "r", errors="ignore") as f:
            for _ in f:
                total_lines += 1

        print(f"{Colors.CYAN}Loaded {total_lines} words from wordlist{Colors.RESET}")
        entropy = calculate_entropy(hash_str)
        print(f"{Colors.CYAN}Hash entropy: {entropy:.2f} bits{Colors.RESET}")

        with open(wordlist_path, "r", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                candidate = line.strip()
                if not candidate:
                    continue
                for algo in possible_types:
                    try:
                        computed = self._hash_string(candidate, algo)
                        if computed == hash_str:
                            print(f"{Colors.GREEN}[+] Hash cracked!{Colors.RESET}")
                            print(f"{Colors.GREEN}[+] Plaintext: {candidate}{Colors.RESET}")
                            print(f"{Colors.GREEN}[+] Algorithm: {algo}{Colors.RESET}")
                            return candidate
                    except Exception:
                        continue
                if i % 100000 == 0:
                    progress = (i / total_lines) * 100
                    print(f"\r{Colors.YELLOW}Progress: {progress:.1f}% ({i}/{total_lines}){Colors.RESET}", end="")

        print()
        print(f"{Colors.RED}[-] Hash not found in wordlist{Colors.RESET}")
        return None

    def brute_force(self, hash_str: str, max_length: int = 4, charset: str = None) -> Optional[str]:
        hash_str = hash_str.strip().lower()
        possible_types = self.identify_hash(hash_str)
        if not possible_types:
            return None

        if charset is None:
            charset = self.default_charset

        print(f"{Colors.YELLOW}Brute forcing hash: {hash_str[:16]}...{Colors.RESET}")
        print(f"{Colors.YELLOW}Max length: {max_length}, Charset size: {len(charset)}{Colors.RESET}")

        total_combinations = sum(len(charset) ** i for i in range(1, max_length + 1))
        print(f"{Colors.CYAN}Total combinations to try: {total_combinations}{Colors.RESET}")

        attempts = 0
        for length in range(1, max_length + 1):
            for combo in product(charset, repeat=length):
                attempts += 1
                candidate = "".join(combo)
                for algo in possible_types:
                    try:
                        computed = self._hash_string(candidate, algo)
                        if computed == hash_str:
                            print(f"{Colors.GREEN}[+] Hash cracked!{Colors.RESET}")
                            print(f"{Colors.GREEN}[+] Plaintext: {candidate}{Colors.RESET}")
                            print(f"{Colors.GREEN}[+] Algorithm: {algo}{Colors.RESET}")
                            print(f"{Colors.GREEN}[+] Attempts: {attempts}{Colors.RESET}")
                            return candidate
                    except Exception:
                        continue
                if attempts % 100000 == 0:
                    progress = (attempts / total_combinations) * 100
                    print(f"\r{Colors.YELLOW}Progress: {progress:.1f}% ({attempts}/{total_combinations}){Colors.RESET}", end="")

        print()
        print(f"{Colors.RED}[-] Hash not found with brute force{Colors.RESET}")
        return None

    def crack_multiple_hashes(self, hash_list: List[str]) -> Dict[str, str]:
        results = {}
        total = len(hash_list)
        print(f"{Colors.YELLOW}Cracking {total} hashes...{Colors.RESET}")

        for i, hash_str in enumerate(hash_list, 1):
            hash_str = hash_str.strip()
            if not hash_str:
                continue
            print(f"\n{Colors.CYAN}[{i}/{total}] Processing: {hash_str[:16]}...{Colors.RESET}")
            plaintext = self.crack_hash(hash_str)
            if plaintext:
                results[hash_str] = plaintext
            else:
                results[hash_str] = None

        cracked = sum(1 for v in results.values() if v is not None)
        print(f"\n{Colors.GREEN}[+] Cracked {cracked}/{total} hashes{Colors.RESET}")
        return results

    def hash_file(self, filepath: str, algorithm: str = "md5") -> str:
        algorithm = algorithm.lower()
        if algorithm not in HASH_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        hasher = HASH_ALGORITHMS[algorithm]
        with open(filepath, "rb") as f:
            if algorithm == "ntlm":
                content = f.read()
                return hasher(content.decode("utf-8", errors="ignore")).hexdigest()
            h = hasher()
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                h.update(chunk)
            return h.hexdigest()


def hash_test():
    print(f"{Colors.CYAN}=== Hash Cracker Tests ==={Colors.RESET}\n")

    cracker = HashCracker()

    test_hashes = {
        "5d41402abc4b2a76b9719d911017c592": "md5",
        "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d": "sha1",
        "65e84be33532fb784c48129675f9eff3a682b27168c0ea744b2cf58ee02337c5": "sha256",
        "b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86": "sha512",
    }

    print(f"{Colors.YELLOW}Testing hash identification...{Colors.RESET}")
    for hash_str, expected_algo in test_hashes.items():
        identified = cracker.identify_hash(hash_str)
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if expected_algo in identified else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {hash_str[:16]}... -> {identified} [{status}]")

    print(f"\n{Colors.YELLOW}Testing hash computation...{Colors.RESET}")
    test_string = "hello"
    for algo in ["md5", "sha1", "sha256", "sha512"]:
        computed = cracker._hash_string(test_string, algo)
        expected = test_hashes.get(computed)
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if expected == algo else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {algo}: {computed[:32]}... [{status}]")

    print(f"\n{Colors.YELLOW}Testing NTLM hash...{Colors.RESET}")
    ntlm_hash = cracker._hash_string("hello", "ntlm")
    print(f"  NTLM('hello'): {ntlm_hash}")

    print(f"\n{Colors.YELLOW}Testing identify_hash with unknown length...{Colors.RESET}")
    unknown = cracker.identify_hash("abc123")
    status = f"{Colors.GREEN}PASS{Colors.RESET}" if unknown == [] else f"{Colors.RED}FAIL{Colors.RESET}"
    print(f"  Result: {unknown} [{status}]")

    print(f"\n{Colors.YELLOW}Testing brute_force with short hash...{Colors.RESET}")
    test_md5 = cracker._hash_string("ab", "md5")
    result = cracker.brute_force(test_md5, max_length=2, charset="abcdefghijklmnopqrstuvwxyz")
    status = f"{Colors.GREEN}PASS{Colors.RESET}" if result == "ab" else f"{Colors.RED}FAIL{Colors.RESET}"
    print(f"  Brute force result: {result} [{status}]")

    print(f"\n{Colors.YELLOW}Testing crack_multiple_hashes...{Colors.RESET}")
    hashes_to_crack = [
        cracker._hash_string("test", "md5"),
        cracker._hash_string("demo", "md5"),
    ]
    results = cracker.crack_multiple_hashes(hashes_to_crack)
    for h, p in results.items():
        print(f"  {h[:16]}... -> {p}")

    print(f"\n{Colors.GREEN}=== Tests Complete ==={Colors.RESET}")
