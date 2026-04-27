#!/usr/bin/env python3
"""Constantes, configuracoes e cores do sistema"""

VERSION = "3.0.0"

# ========================= CORES ANSI =========================
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

# ========================= MENSAGENS =========================
class Messages:
    INIT = "[*] Inicializando sistema..."
    SUCCESS = "[+] Operacao concluida com sucesso"
    ERROR = "[-] Erro na operacao"
    WARNING = "[!] Aviso"
    INFO = "[i] Informacao"
    LOADING = "[*] Carregando..."
    SAVING = "[*] Salvando..."
    DONE = "[+] Concluido"

# ========================= CONSTANTES DE ANALISE =========================
MAX_DEPTH = 10
TIMEOUT_SECONDS = 30
ENTROPY_THRESHOLD = 7.5
MIN_PRINTABLE_RATIO = 0.7

# ========================= XOR =========================
XOR_MAX_KEY_SIZE = 50
XOR_MIN_KEY_SIZE = 1

# ========================= MAGIC NUMBERS =========================
MAGIC_NUMBERS = {
    b'\x7fELF': 'ELF Executable',
    b'MZ': 'PE Executable (Windows)',
    b'PK\x03\x04': 'ZIP Archive',
    b'PK\x05\x06': 'ZIP Archive (empty)',
    b'PK\x07\x08': 'ZIP Archive (spanned)',
    b'\x1f\x8b': 'GZIP Compressed',
    b'BZ': 'BZIP2 Compressed',
    b'\xfd7zXZ\x00': 'XZ Compressed',
    b'\x89PNG\r\n\x1a\n': 'PNG Image',
    b'\xff\xd8\xff': 'JPEG Image',
    b'GIF87a': 'GIF 87a Image',
    b'GIF89a': 'GIF 89a Image',
    b'%PDF': 'PDF Document',
    b'Rar!\x1a\x07': 'RAR Archive',
    b'\x50\x4b\x03\x04': 'ZIP File',
    b'\x00\x00\x01\x00': 'ICO File',
    b'\x00\x00\x02\x00': 'CUR File',
    b'BM': 'BMP Image',
    b'II\x2a\x00': 'TIFF Image (Little Endian)',
    b'MM\x00\x2a': 'TIFF Image (Big Endian)',
    b'ID3': 'MP3 Audio (with ID3)',
    b'\xff\xfb': 'MP3 Audio',
    b'OggS': 'OGG Audio',
    b'FLAC': 'FLAC Audio',
    b'RIFF': 'RIFF Container (WAV/AVI)',
    b'\x00\x00\x00\x18ftyp': 'MP4 Video',
    b'\x00\x00\x00\x1cftyp': 'MP4 Video',
    b'fLaC': 'FLAC Audio',
    b'\x30\x26\xB2\x75': 'ASF/WMV Container',
    b'\x1a\x45\xdf\xa3': 'MKV/MKA Container',
    b'#!AMR': 'AMR Audio',
    b'#!AMR-WB': 'AMR-WB Audio',
    b'\x00\x00\x00\x20ftypmp42': 'MP4v2 Video',
    b'\xfe\xed\xfa\xce': 'Mach-O Binary (32-bit)',
    b'\xfe\xed\xfa\xcf': 'Mach-O Binary (64-bit)',
    b'\xca\xfe\xba\xbe': 'Java Class / Mach-O Fat',
    b'\xd0\xcf\x11\xe0': 'MS Office Document (OLE2)',
    b'50 4b 03 04': 'ZIP-based (docx/xlsx/pptx)',
    b'\x03\x00\x00\x00\x00\x00\x00\x00': 'Windows Shortcut (LNK)',
    b'ER': 'Windows Registry (REGF)',
    b'SQLite format 3': 'SQLite Database',
    b'\x57\x53': 'Windows Registry (WS)',
}

# ========================= CHAVES COMUNS =========================
COMMON_KEYS = [
    b'password', b'admin', b'root', b'toor', b'letmein',
    b'qwerty', b'abc123', b'master', b'dragon', b'shadow',
    b'key', b'secret', b'default', b'guest', b'test',
    b'1234567890123456', b'0000000000000000', b'ffffffffffffffff',
    b'AAAAAAAAAAAAAAAA', b'abcdefghijklmnop',
    b'0123456789abcdef', b'fedcba9876543210',
    b'encryptionkey', b'aeskey', b'cryptokey', b'masterkey',
    b'supersecret', b'mysecretkey', b'privatekey',
]

# ========================= ENCODINGS SUPORTADOS =========================
SUPPORTED_ENCODINGS = [
    'base64', 'base32', 'base16', 'hex', 'url',
    'rot13', 'utf-8', 'latin-1', 'ascii', 'cp1252',
    'utf-16', 'utf-16-le', 'utf-16-be',
]

# ========================= PRINTABLE =========================
PRINTABLE = set(range(32, 127)) | {9, 10, 13}

# ========================= CONFIGURACOES PADRAO =========================
DEFAULT_CONFIG = {
    'version': VERSION,
    'max_depth': MAX_DEPTH,
    'timeout': TIMEOUT_SECONDS,
    'brute_force_limit': 1_000_000,
    'entropy_threshold': ENTROPY_THRESHOLD,
    'min_printable_ratio': MIN_PRINTABLE_RATIO,
    'xor_max_key_size': XOR_MAX_KEY_SIZE,
    'auto_export': True,
    'verbose': True,
    'save_logs': True,
    'output_dir': 'output',
    'wordlist_dir': 'wordlists',
    'temp_dir': 'temp',
    'log_dir': 'logs',
}

# ========================= FUNCOES DE CARGA =========================
import json
import os

def load_config(config_path: str = None) -> dict:
    """Carrega configuracoes de arquivo JSON ou retorna padrao"""
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config', 'settings.json'
        )
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)
