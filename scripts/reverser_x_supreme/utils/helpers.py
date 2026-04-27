import logging
import os
import hashlib
import base64
import string
import time
import math
from typing import Dict, Tuple, Generator, List, Optional, Any
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from utils.constants import Colors, PRINTABLE, SUPPORTED_ENCODINGS


def setup_logger(name: str, log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def is_printable(data: bytes, threshold: float = 0.7) -> bool:
    if not data:
        return False
    printable_count = sum(1 for byte in data if byte in PRINTABLE)
    return (printable_count / len(data)) >= threshold


def is_base64(data: bytes) -> bool:
    try:
        text = data.decode('ascii').strip()
        if len(text) % 4 != 0:
            text += '=' * (4 - len(text) % 4)
        decoded = base64.b64decode(text, validate=True)
        return len(decoded) > 0
    except Exception:
        return False


def is_hex(data: bytes) -> bool:
    try:
        text = data.decode('ascii').strip()
        if len(text) % 2 != 0:
            return False
        int(text, 16)
        return True
    except (ValueError, UnicodeDecodeError):
        return False


def is_hash(data: bytes) -> Tuple[bool, str]:
    try:
        text = data.decode('ascii').strip()
    except UnicodeDecodeError:
        return False, ''
    hash_types = {
        'md5': 32,
        'sha1': 40,
        'sha224': 56,
        'sha256': 64,
        'sha384': 96,
        'sha512': 128,
    }
    for hash_type, length in hash_types.items():
        if len(text) == length:
            try:
                int(text, 16)
                return True, hash_type
            except ValueError:
                continue
    return False, ''


def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counter = Counter(data)
    length = len(data)
    entropy = 0.0
    for count in counter.values():
        probability = count / length
        if probability > 0:
            entropy -= probability * math.log2(probability)
    return entropy


def frequency_analysis(data: bytes) -> Dict[int, int]:
    return dict(Counter(data))


def find_repeating_patterns(data: bytes, min_length: int = 4) -> Dict[bytes, int]:
    patterns: Dict[bytes, int] = {}
    max_length = min(len(data) // 2, 64)
    for length in range(min_length, max_length + 1):
        for i in range(len(data) - length + 1):
            pattern = data[i:i + length]
            count = 0
            start = 0
            while True:
                idx = data.find(pattern, start)
                if idx == -1:
                    break
                count += 1
                start = idx + 1
            if count > 1:
                patterns[pattern] = count
    filtered = {k: v for k, v in sorted(patterns.items(), key=lambda x: x[1], reverse=True) if v > 1}
    result: Dict[bytes, int] = {}
    seen: List[bytes] = []
    for pattern, count in filtered.items():
        is_subpattern = False
        for longer in seen:
            if pattern in longer:
                is_subpattern = True
                break
        if not is_subpattern:
            result[pattern] = count
            seen.append(pattern)
    return result


def detect_language(data: bytes) -> str:
    try:
        text = data.decode('utf-8', errors='ignore').lower()
    except Exception:
        return 'unknown'
    language_markers = {
        'english': ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with'],
        'spanish': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'ser', 'se', 'no'],
        'french': ['le', 'de', 'et', 'les', 'des', 'un', 'une', 'en', 'que', 'est'],
        'german': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
        'portuguese': ['o', 'de', 'e', 'em', 'um', 'que', 'a', 'do', 'da', 'se'],
        'italian': ['il', 'di', 'che', 'e', 'la', 'un', 'in', 'del', 'si', 'le'],
        'russian': ['в', 'и', 'не', 'на', 'я', 'быть', 'он', 'с', 'как', 'а'],
    }
    scores: Dict[str, int] = {}
    words = text.split()
    for language, markers in language_markers.items():
        score = sum(1 for marker in markers if marker in words)
        scores[language] = score
    if not scores or max(scores.values()) == 0:
        return 'unknown'
    return max(scores, key=scores.get)


def bytes_to_hex(data: bytes, separator: str = '') -> str:
    return separator.join(f'{byte:02x}' for byte in data)


def hex_to_bytes(hex_string: str) -> bytes:
    cleaned = hex_string.replace(' ', '').replace(':', '').replace('-', '')
    if len(cleaned) % 2 != 0:
        cleaned = '0' + cleaned
    return bytes.fromhex(cleaned)


def bytes_to_binary(data: bytes, separator: str = '') -> str:
    return separator.join(f'{byte:08b}' for byte in data)


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def rolling_xor(data: bytes, key: bytes) -> bytes:
    if not key:
        return data
    key_len = len(key)
    return bytes(b ^ key[i % key_len] for i, b in enumerate(data))


class TimeoutError(Exception):
    pass


def run_with_timeout(func, timeout_seconds: int, *args, **kwargs):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout_seconds)
        except FuturesTimeoutError:
            raise TimeoutError(f"Function '{func.__name__}' timed out after {timeout_seconds} seconds")


def read_file_chunks(filepath: str, chunk_size: int = 8192) -> Generator[bytes, None, None]:
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


def get_file_hash(filepath: str, algorithm: str = 'sha256') -> str:
    if algorithm not in SUPPORTED_ENCODINGS and algorithm not in ('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'):
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    hasher = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def safe_file_write(filepath: str, data: bytes, backup: bool = True) -> bool:
    try:
        if backup and os.path.exists(filepath):
            backup_path = filepath + '.bak'
            with open(filepath, 'rb') as src:
                with open(backup_path, 'wb') as dst:
                    dst.write(src.read())
        temp_path = filepath + '.tmp'
        with open(temp_path, 'wb') as f:
            f.write(data)
        os.replace(temp_path, filepath)
        return True
    except Exception:
        if os.path.exists(filepath + '.tmp'):
            try:
                os.remove(filepath + '.tmp')
            except OSError:
                pass
        return False


class ProgressBar:
    def __init__(self, total: int, prefix: str = '', suffix: str = '', decimals: int = 1, length: int = 50, fill: str = '#'):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.current = 0
        self.start_time = time.time()

    def update(self, n: int = 1) -> None:
        self.current += n
        self._print()

    def _print(self) -> None:
        if self.total == 0:
            percent = 100.0
        else:
            percent = (self.current / self.total) * 100
        filled = int(self.length * self.current // self.total) if self.total > 0 else self.length
        bar = self.fill * filled + '-' * (self.length - filled)
        elapsed = time.time() - self.start_time
        if self.current > 0 and elapsed > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
        else:
            eta = 0
        print(f'\r{self.prefix} |{bar}| {percent:.{self.decimals}f}% [{self.current}/{self.total}] ETA: {eta:.1f}s {self.suffix}', end='', flush=True)

    def finish(self) -> None:
        self.current = self.total
        self._print()
        print()


def hexdump(data: bytes, offset: int = 0, length: int = 256, width: int = 16) -> str:
    result_lines: List[str] = []
    end = min(offset + length, len(data))
    for i in range(offset, end, width):
        chunk = data[i:i + width]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if b in PRINTABLE else '.' for b in chunk)
        addr = f'{i:08x}'
        hex_part = hex_part.ljust(width * 3 - 1)
        result_lines.append(f'{addr}  {hex_part}  |{ascii_part}|')
    return '\n'.join(result_lines)


def print_analysis(data: bytes, title: str = "Análise de Dados") -> None:
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")
    print(f"{Colors.YELLOW}Tamanho:{Colors.RESET} {len(data)} bytes")
    entropy = calculate_entropy(data)
    print(f"{Colors.YELLOW}Entropia:{Colors.RESET} {entropy:.4f} bits/byte")
    if entropy > 7.5:
        entropy_status = f"{Colors.RED}Muito alta (possivelmente criptografado/comprimido){Colors.RESET}"
    elif entropy > 6.0:
        entropy_status = f"{Colors.YELLOW}Alta (possivelmente codificado){Colors.RESET}"
    elif entropy > 4.0:
        entropy_status = f"{Colors.GREEN}Média (texto estruturado){Colors.RESET}"
    else:
        entropy_status = f"{Colors.GREEN}Baixa (texto simples/repetitivo){Colors.RESET}"
    print(f"{Colors.YELLOW}Status da entropia:{Colors.RESET} {entropy_status}")
    printable_pct = (sum(1 for b in data if b in PRINTABLE) / len(data) * 100) if data else 0
    print(f"{Colors.YELLOW}Imprimível:{Colors.RESET} {printable_pct:.1f}%")
    is_b64 = is_base64(data)
    print(f"{Colors.YELLOW}Base64:{Colors.RESET} {'Sim' if is_b64 else 'Não'}")
    is_hex_str = is_hex(data)
    print(f"{Colors.YELLOW}Hexadecimal:{Colors.RESET} {'Sim' if is_hex_str else 'Não'}")
    is_hash_result, hash_type = is_hash(data)
    print(f"{Colors.YELLOW}Hash:{Colors.RESET} {'Sim' if is_hash_result else 'Não'}{' (' + hash_type.upper() + ')' if is_hash_result else ''}")
    freq = frequency_analysis(data)
    if freq:
        most_common = Counter(freq).most_common(5)
        print(f"\n{Colors.YELLOW}Bytes mais frequentes:{Colors.RESET}")
        for byte_val, count in most_common:
            char_repr = chr(byte_val) if byte_val in PRINTABLE else '.'
            print(f"  0x{byte_val:02x} ({char_repr}): {count} ocorrências ({count / len(data) * 100:.1f}%)")
    patterns = find_repeating_patterns(data, min_length=4)
    if patterns:
        print(f"\n{Colors.YELLOW}Padrões repetitivos encontrados:{Colors.RESET} {len(patterns)}")
        for pattern, count in list(patterns.items())[:5]:
            pattern_hex = bytes_to_hex(pattern, ' ')
            print(f"  {pattern_hex} (x{count})")
    lang = detect_language(data)
    if lang != 'unknown':
        print(f"\n{Colors.YELLOW}Idioma detectado:{Colors.RESET} {lang}")
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")
