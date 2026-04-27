#!/usr/bin/env python3
"""CryptoBreaker - Cryptographic analysis and attack module"""

import os
import sys
import base64
import hashlib
import struct
from typing import List, Dict, Any, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import Colors, COMMON_KEYS
from utils.helpers import is_printable, calculate_entropy, xor_bytes

try:
    from Crypto.Cipher import AES, DES, DES3
    from Crypto.Util.Padding import unpad
    from Crypto.PublicKey import RSA
    PYCRYPTO_AVAILABLE = True
except ImportError:
    PYCRYPTO_AVAILABLE = False


class CryptoBreaker:
    """Cryptographic analysis and attack engine"""

    AES_KEY_SIZES = [16, 24, 32]
    DES_KEY_SIZE = 8
    DES3_KEY_SIZE = 24
    BLOCK_SIZE = 16

    RSA_PATTERNS = [
        b'-----BEGIN RSA PRIVATE KEY-----',
        b'-----END RSA PRIVATE KEY-----',
        b'-----BEGIN PRIVATE KEY-----',
        b'-----END PRIVATE KEY-----',
        b'-----BEGIN PUBLIC KEY-----',
        b'-----END PUBLIC KEY-----',
        b'-----BEGIN RSA PUBLIC KEY-----',
        b'-----END RSA PUBLIC KEY-----',
        b'-----BEGIN ENCRYPTED PRIVATE KEY-----',
        b'-----END ENCRYPTED PRIVATE KEY-----',
        b'-----BEGIN DSA PRIVATE KEY-----',
        b'-----END DSA PRIVATE KEY-----',
        b'-----BEGIN EC PRIVATE KEY-----',
        b'-----END EC PRIVATE KEY-----',
        b'-----BEGIN OPENSSH PRIVATE KEY-----',
        b'-----END OPENSSH PRIVATE KEY-----',
        b'-----BEGIN PGP PRIVATE KEY BLOCK-----',
        b'-----END PGP PRIVATE KEY BLOCK-----',
        b'-----BEGIN PGP PUBLIC KEY BLOCK-----',
        b'-----END PGP PUBLIC KEY BLOCK-----',
    ]

    SSH_PATTERNS = [
        b'ssh-rsa',
        b'ssh-dss',
        b'ssh-ed25519',
        b'ecdsa-sha2-nistp',
        b'sk-ssh-ed25519',
        b'sk-ecdsa-sha2-nistp',
    ]

    RSA_KEY_INDICATORS = [
        b'\x30\x82',
        b'\x02\x01\x00',
        b'\x02\x81\x81',
        b'\x02\x82\x01',
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.verbose = self.config.get('verbose', True)
        self.timeout = self.config.get('timeout', 30)
        self.results: List[Dict[str, Any]] = []
        self._pycrypto_available = PYCRYPTO_AVAILABLE

    def _log(self, message: str, color: str = Colors.WHITE) -> None:
        if self.verbose:
            print(f"{color}{message}{Colors.RESET}")

    def _add_result(self, attack_type: str, status: str, details: Dict[str, Any],
                    decrypted_data: Optional[bytes] = None) -> Dict[str, Any]:
        result = {
            'attack_type': attack_type,
            'status': status,
            'details': details,
            'timestamp': __import__('time').time(),
        }
        if decrypted_data is not None:
            result['decrypted_data'] = decrypted_data
            result['decrypted_preview'] = decrypted_data[:128]
            result['decrypted_entropy'] = calculate_entropy(decrypted_data)
            result['is_printable'] = is_printable(decrypted_data)
        self.results.append(result)
        return result

    def _prepare_key(self, key_material: bytes, target_size: int) -> bytes:
        if len(key_material) == target_size:
            return key_material
        if len(key_material) > target_size:
            return hashlib.sha256(key_material).digest()[:target_size]
        padded = key_material * (target_size // len(key_material) + 1)
        return padded[:target_size]

    def _try_decrypt_aes_ecb(self, data: bytes, key: bytes) -> Optional[bytes]:
        if not self._pycrypto_available:
            return None
        try:
            cipher = AES.new(key, AES.MODE_ECB)
            if len(data) % AES.block_size != 0:
                return None
            decrypted = cipher.decrypt(data)
            try:
                decrypted = unpad(decrypted, AES.block_size)
            except (ValueError, IndexError):
                pass
            return decrypted
        except Exception:
            return None

    def _try_decrypt_aes_cbc(self, data: bytes, key: bytes) -> Optional[bytes]:
        if not self._pycrypto_available:
            return None
        try:
            if len(data) < AES.block_size:
                return None
            iv = data[:AES.block_size]
            ciphertext = data[AES.block_size:]
            if len(ciphertext) % AES.block_size != 0:
                return None
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ciphertext)
            try:
                decrypted = unpad(decrypted, AES.block_size)
            except (ValueError, IndexError):
                pass
            return decrypted
        except Exception:
            return None

    def _try_decrypt_aes_cfb(self, data: bytes, key: bytes) -> Optional[bytes]:
        if not self._pycrypto_available:
            return None
        try:
            if len(data) < AES.block_size:
                return None
            iv = data[:AES.block_size]
            ciphertext = data[AES.block_size:]
            cipher = AES.new(key, AES.MODE_CFB, iv)
            return cipher.decrypt(ciphertext)
        except Exception:
            return None

    def _try_decrypt_aes_ofb(self, data: bytes, key: bytes) -> Optional[bytes]:
        if not self._pycrypto_available:
            return None
        try:
            if len(data) < AES.block_size:
                return None
            iv = data[:AES.block_size]
            ciphertext = data[AES.block_size:]
            cipher = AES.new(key, AES.MODE_OFB, iv)
            return cipher.decrypt(ciphertext)
        except Exception:
            return None

    def _try_decrypt_des_ecb(self, data: bytes, key: bytes) -> Optional[bytes]:
        if not self._pycrypto_available:
            return None
        try:
            if len(data) % DES.block_size != 0:
                return None
            cipher = DES.new(key, DES.MODE_ECB)
            decrypted = cipher.decrypt(data)
            try:
                decrypted = unpad(decrypted, DES.block_size)
            except (ValueError, IndexError):
                pass
            return decrypted
        except Exception:
            return None

    def _try_decrypt_des3_ecb(self, data: bytes, key: bytes) -> Optional[bytes]:
        if not self._pycrypto_available:
            return None
        try:
            if len(data) % DES3.block_size != 0:
                return None
            cipher = DES3.new(key, DES3.MODE_ECB)
            decrypted = cipher.decrypt(data)
            try:
                decrypted = unpad(decrypted, DES3.block_size)
            except (ValueError, IndexError):
                pass
            return decrypted
        except Exception:
            return None

    def _evaluate_decryption(self, decrypted: bytes) -> Tuple[bool, float]:
        if decrypted is None:
            return False, 0.0
        entropy = calculate_entropy(decrypted)
        printable = is_printable(decrypted)
        null_ratio = decrypted.count(b'\x00') / len(decrypted) if len(decrypted) > 0 else 1.0
        score = 0.0
        if printable:
            score += 3.0
        if entropy < 5.0:
            score += 2.0
        elif entropy < 6.5:
            score += 1.0
        if null_ratio < 0.1:
            score += 1.0
        common_patterns = [b'PK', b'<?xml', b'<!DOCTYPE', b'HTTP/', b'GET ', b'POST ',
                           b'{"', b'["', b'function', b'class ', b'def ', b'import ',
                           b'from ', b'return', b'if ', b'for ', b'while ', b'the ',
                           b'and ', b'is ', b'are ', b'password', b'user', b'admin',
                           b'login', b'token', b'session', b'cookie', b'-----BEGIN',
                           b'#!/', b'#!/bin', b'#!/usr', b'\x7fELF', b'MZ']
        for pattern in common_patterns:
            if pattern in decrypted:
                score += 2.0
                break
        return score >= 3.0, score

    def aes_attack(self, data: bytes) -> List[Dict[str, Any]]:
        """Try AES ECB decryption with common keys for 128/192/256 bit"""
        results = []
        if not self._pycrypto_available:
            self._log("[!] pycryptodome not available - AES attack limited", Colors.YELLOW)
            return self._add_result('AES', 'unavailable',
                                    {'error': 'pycryptodome not installed',
                                     'install': 'pip install pycryptodome'})
        if len(data) < self.BLOCK_SIZE:
            return self._add_result('AES', 'failed',
                                    {'error': 'Data too short for AES block size',
                                     'min_size': self.BLOCK_SIZE,
                                     'data_size': len(data)})
        self._log(f"[*] Starting AES attack on {len(data)} bytes of data", Colors.CYAN)
        keys_to_try = list(COMMON_KEYS)
        for key in keys_to_try:
            key_hex = key.hex()
            if len(key_hex) == 32:
                keys_to_try.append(bytes.fromhex(key_hex))
            if len(key_hex) == 48:
                keys_to_try.append(bytes.fromhex(key_hex))
            if len(key_hex) == 64:
                keys_to_try.append(bytes.fromhex(key_hex))
        derived_keys = []
        for base_key in [b'password', b'key', b'secret', b'master', b'aes', b'crypto']:
            for key_size in self.AES_KEY_SIZES:
                derived_keys.append(self._prepare_key(base_key, key_size))
        all_keys = list(set(keys_to_try + derived_keys))
        success_count = 0
        for key_size in self.AES_KEY_SIZES:
            self._log(f"[*] Trying AES-{key_size * 8} with {len(all_keys)} keys", Colors.CYAN)
            for key in all_keys:
                prepared_key = self._prepare_key(key, key_size)
                decrypted_ecb = self._try_decrypt_aes_ecb(data, prepared_key)
                if decrypted_ecb is not None:
                    is_valid, score = self._evaluate_decryption(decrypted_ecb)
                    if is_valid:
                        result = self._add_result('AES-ECB', 'success',
                                                  {'key': prepared_key.hex(),
                                                   'key_size': key_size * 8,
                                                   'mode': 'ECB',
                                                   'score': score,
                                                   'data_size': len(data),
                                                   'decrypted_size': len(decrypted_ecb)})
                        results.append(result)
                        success_count += 1
                        self._log(f"[+] AES-ECB-{key_size * 8} SUCCESS with key: {prepared_key.hex()}",
                                  Colors.GREEN)
                decrypted_cbc = self._try_decrypt_aes_cbc(data, prepared_key)
                if decrypted_cbc is not None:
                    is_valid, score = self._evaluate_decryption(decrypted_cbc)
                    if is_valid:
                        result = self._add_result('AES-CBC', 'success',
                                                  {'key': prepared_key.hex(),
                                                   'key_size': key_size * 8,
                                                   'mode': 'CBC',
                                                   'score': score,
                                                   'data_size': len(data),
                                                   'decrypted_size': len(decrypted_cbc)})
                        results.append(result)
                        success_count += 1
                        self._log(f"[+] AES-CBC-{key_size * 8} SUCCESS with key: {prepared_key.hex()}",
                                  Colors.GREEN)
                decrypted_cfb = self._try_decrypt_aes_cfb(data, prepared_key)
                if decrypted_cfb is not None:
                    is_valid, score = self._evaluate_decryption(decrypted_cfb)
                    if is_valid:
                        result = self._add_result('AES-CFB', 'success',
                                                  {'key': prepared_key.hex(),
                                                   'key_size': key_size * 8,
                                                   'mode': 'CFB',
                                                   'score': score,
                                                   'data_size': len(data),
                                                   'decrypted_size': len(decrypted_cfb)})
                        results.append(result)
                        success_count += 1
                        self._log(f"[+] AES-CFB-{key_size * 8} SUCCESS with key: {prepared_key.hex()}",
                                  Colors.GREEN)
                decrypted_ofb = self._try_decrypt_aes_ofb(data, prepared_key)
                if decrypted_ofb is not None:
                    is_valid, score = self._evaluate_decryption(decrypted_ofb)
                    if is_valid:
                        result = self._add_result('AES-OFB', 'success',
                                                  {'key': prepared_key.hex(),
                                                   'key_size': key_size * 8,
                                                   'mode': 'OFB',
                                                   'score': score,
                                                   'data_size': len(data),
                                                   'decrypted_size': len(decrypted_ofb)})
                        results.append(result)
                        success_count += 1
                        self._log(f"[+] AES-OFB-{key_size * 8} SUCCESS with key: {prepared_key.hex()}",
                                  Colors.GREEN)
        if success_count == 0:
            results.append(self._add_result('AES', 'failed',
                                            {'keys_tried': len(all_keys),
                                             'key_sizes': self.AES_KEY_SIZES,
                                             'modes': ['ECB', 'CBC', 'CFB', 'OFB']}))
        else:
            self._log(f"[+] Found {success_count} successful AES decryption(s)", Colors.GREEN)
        self.results.extend(results)
        return results

    def rsa_attack(self, data: bytes) -> List[Dict[str, Any]]:
        """Detect RSA key patterns and attempt analysis"""
        results = []
        self._log(f"[*] Starting RSA analysis on {len(data)} bytes", Colors.CYAN)
        text_data = data
        try:
            text_data = data.decode('utf-8', errors='ignore')
        except Exception:
            pass
        detected_keys = []
        for pattern in self.RSA_PATTERNS:
            if pattern in data:
                key_type = pattern.decode('utf-8', errors='ignore')
                detected_keys.append({
                    'type': 'PEM',
                    'pattern': key_type,
                    'offset': data.find(pattern),
                })
                self._log(f"[+] Found RSA PEM pattern: {key_type}", Colors.GREEN)
        for pattern in self.SSH_PATTERNS:
            if pattern in data:
                key_type = pattern.decode('utf-8', errors='ignore')
                detected_keys.append({
                    'type': 'SSH',
                    'pattern': key_type,
                    'offset': data.find(pattern),
                })
                self._log(f"[+] Found SSH key pattern: {key_type}", Colors.GREEN)
        for indicator in self.RSA_KEY_INDICATORS:
            if indicator in data:
                offset = data.find(indicator)
                detected_keys.append({
                    'type': 'DER',
                    'indicator': indicator.hex(),
                    'offset': offset,
                })
                self._log(f"[+] Found RSA DER indicator at offset {offset}", Colors.GREEN)
        if self._pycrypto_available:
            try:
                pem_data = data.decode('utf-8', errors='ignore')
                if '-----BEGIN' in pem_data and '-----END' in pem_data:
                    key = RSA.import_key(pem_data)
                    key_info = {
                        'type': 'RSA',
                        'key_size': key.size_in_bits(),
                        'n': key.n if hasattr(key, 'n') else None,
                        'e': key.e if hasattr(key, 'e') else None,
                        'has_private': key.has_private() if hasattr(key, 'has_private') else False,
                    }
                    result = self._add_result('RSA', 'parsed',
                                              {'key_info': key_info,
                                               'key_size_bits': key.size_in_bits()})
                    results.append(result)
                    self._log(f"[+] Parsed RSA key: {key.size_in_bits()} bits", Colors.GREEN)
            except (ValueError, IndexError, TypeError) as e:
                self._log(f"[-] Could not parse RSA key: {e}", Colors.YELLOW)
        if detected_keys:
            result = self._add_result('RSA', 'detected',
                                      {'detected_keys': detected_keys,
                                       'total_patterns': len(detected_keys),
                                       'data_entropy': calculate_entropy(data)})
            results.append(result)
        if not detected_keys and not results:
            base64_segments = []
            try:
                decoded = base64.b64decode(data, validate=False)
                if len(decoded) > 0:
                    for indicator in self.RSA_KEY_INDICATORS:
                        if indicator in decoded:
                            base64_segments.append({
                                'decoded_size': len(decoded),
                                'indicator': indicator.hex(),
                            })
                            self._log(f"[+] Found RSA indicator in base64-decoded data", Colors.GREEN)
            except Exception:
                pass
            if base64_segments:
                result = self._add_result('RSA', 'base64_detected',
                                          {'segments': base64_segments})
                results.append(result)
            else:
                result = self._add_result('RSA', 'not_detected',
                                          {'data_entropy': calculate_entropy(data),
                                           'data_size': len(data)})
                results.append(result)
        self.results.extend(results)
        return results

    def des_attack(self, data: bytes) -> List[Dict[str, Any]]:
        """Try DES decryption with common keys"""
        results = []
        if not self._pycrypto_available:
            self._log("[!] pycryptodome not available - DES attack limited", Colors.YELLOW)
            return self._add_result('DES', 'unavailable',
                                    {'error': 'pycryptodome not installed',
                                     'install': 'pip install pycryptodome'})
        if len(data) < self.DES_KEY_SIZE:
            return self._add_result('DES', 'failed',
                                    {'error': 'Data too short for DES',
                                     'min_size': self.DES_KEY_SIZE,
                                     'data_size': len(data)})
        self._log(f"[*] Starting DES attack on {len(data)} bytes", Colors.CYAN)
        keys_to_try = list(COMMON_KEYS)
        derived_keys = []
        for base_key in [b'password', b'key', b'secret', b'des', b'crypto']:
            derived_keys.append(self._prepare_key(base_key, self.DES_KEY_SIZE))
        all_keys = list(set(keys_to_try + derived_keys))
        success_count = 0
        self._log(f"[*] Trying DES-ECB with {len(all_keys)} keys", Colors.CYAN)
        for key in all_keys:
            prepared_key = self._prepare_key(key, self.DES_KEY_SIZE)
            try:
                prepared_key = bytes([b & 0xFE for b in prepared_key[:self.DES_KEY_SIZE]])
            except Exception:
                continue
            decrypted = self._try_decrypt_des_ecb(data, prepared_key)
            if decrypted is not None:
                is_valid, score = self._evaluate_decryption(decrypted)
                if is_valid:
                    result = self._add_result('DES-ECB', 'success',
                                              {'key': prepared_key.hex(),
                                               'key_size': self.DES_KEY_SIZE * 8,
                                               'mode': 'ECB',
                                               'score': score,
                                               'data_size': len(data),
                                               'decrypted_size': len(decrypted)})
                    results.append(result)
                    success_count += 1
                    self._log(f"[+] DES-ECB SUCCESS with key: {prepared_key.hex()}", Colors.GREEN)
        self._log(f"[*] Trying 3DES-ECB with {len(all_keys)} keys", Colors.CYAN)
        for key in all_keys:
            prepared_key = self._prepare_key(key, self.DES3_KEY_SIZE)
            decrypted = self._try_decrypt_des3_ecb(data, prepared_key)
            if decrypted is not None:
                is_valid, score = self._evaluate_decryption(decrypted)
                if is_valid:
                    result = self._add_result('3DES-ECB', 'success',
                                              {'key': prepared_key.hex(),
                                               'key_size': self.DES3_KEY_SIZE * 8,
                                               'mode': 'ECB',
                                               'score': score,
                                               'data_size': len(data),
                                               'decrypted_size': len(decrypted)})
                    results.append(result)
                    success_count += 1
                    self._log(f"[+] 3DES-ECB SUCCESS with key: {prepared_key.hex()}", Colors.GREEN)
        if success_count == 0:
            results.append(self._add_result('DES', 'failed',
                                            {'keys_tried': len(all_keys),
                                             'modes': ['DES-ECB', '3DES-ECB']}))
        else:
            self._log(f"[+] Found {success_count} successful DES decryption(s)", Colors.GREEN)
        self.results.extend(results)
        return results

    def detect_cipher_mode(self, data: bytes) -> str:
        """Detect if ECB, CBC, etc based on block patterns"""
        if len(data) < self.BLOCK_SIZE * 2:
            return "unknown_too_short"
        self._log(f"[*] Detecting cipher mode for {len(data)} bytes", Colors.CYAN)
        blocks = []
        for i in range(0, len(data) - self.BLOCK_SIZE + 1, self.BLOCK_SIZE):
            blocks.append(data[i:i + self.BLOCK_SIZE])
        if not blocks:
            return "unknown_no_blocks"
        unique_blocks = set(blocks)
        total_blocks = len(blocks)
        unique_count = len(unique_blocks)
        duplication_ratio = 1.0 - (unique_count / total_blocks) if total_blocks > 0 else 0.0
        block_counts = {}
        for block in blocks:
            block_counts[block] = block_counts.get(block, 0) + 1
        max_repeated = max(block_counts.values()) if block_counts else 0
        most_common_block = max(block_counts, key=block_counts.get) if block_counts else b''
        entropy = calculate_entropy(data)
        first_block_entropy = calculate_entropy(blocks[0]) if blocks else 0.0
        if duplication_ratio > 0.3:
            mode = "ECB"
            confidence = min(duplication_ratio * 2.0, 1.0)
            self._log(f"[+] Likely ECB mode (duplication ratio: {duplication_ratio:.2%})", Colors.GREEN)
        elif first_block_entropy > 7.5 and entropy > 7.5:
            mode = "CBC"
            confidence = 0.6
            self._log(f"[+] Likely CBC mode (high entropy throughout)", Colors.YELLOW)
        elif len(blocks) >= 2 and blocks[0] == most_common_block and max_repeated > 2:
            mode = "ECB"
            confidence = 0.8
            self._log(f"[+] Likely ECB mode (first block repeated {max_repeated} times)", Colors.GREEN)
        else:
            mode = "unknown"
            confidence = 0.3
            self._log(f"[-] Unable to determine cipher mode", Colors.YELLOW)
        analysis = {
            'mode': mode,
            'confidence': confidence,
            'total_blocks': total_blocks,
            'unique_blocks': unique_count,
            'duplication_ratio': duplication_ratio,
            'max_repeated_block': max_repeated,
            'overall_entropy': entropy,
            'first_block_entropy': first_block_entropy,
            'block_size': self.BLOCK_SIZE,
        }
        result = self._add_result('cipher_mode_detection', 'completed', analysis)
        self.results.append(result)
        return mode

    def full_crypto_analysis(self, data: bytes) -> List[Dict[str, Any]]:
        """Run all attacks and return comprehensive results"""
        all_results = []
        self._log(f"\n{'=' * 60}", Colors.CYAN)
        self._log(f"[*] FULL CRYPTO ANALYSIS - {len(data)} bytes", Colors.BOLD + Colors.CYAN)
        self._log(f"{'=' * 60}", Colors.CYAN)
        self._log(f"[*] Data entropy: {calculate_entropy(data):.4f} bits/byte", Colors.WHITE)
        self._log(f"[*] Printable ratio: {is_printable(data)}", Colors.WHITE)
        self._log(f"[*] pycryptodome: {'available' if self._pycrypto_available else 'not available'}",
                  Colors.WHITE)
        self._log(f"\n[*] Phase 1: Cipher Mode Detection", Colors.BOLD + Colors.MAGENTA)
        mode = self.detect_cipher_mode(data)
        all_results.extend(self.results[-1:])
        self._log(f"\n[*] Phase 2: AES Analysis", Colors.BOLD + Colors.MAGENTA)
        aes_results = self.aes_attack(data)
        all_results.extend(aes_results)
        self._log(f"\n[*] Phase 3: DES Analysis", Colors.BOLD + Colors.MAGENTA)
        des_results = self.des_attack(data)
        all_results.extend(des_results)
        self._log(f"\n[*] Phase 4: RSA Analysis", Colors.BOLD + Colors.MAGENTA)
        rsa_results = self.rsa_attack(data)
        all_results.extend(rsa_results)
        self._log(f"\n{'=' * 60}", Colors.CYAN)
        self._log(f"[*] ANALYSIS COMPLETE", Colors.BOLD + Colors.GREEN)
        self._log(f"[*] Total findings: {len(all_results)}", Colors.WHITE)
        successful = [r for r in all_results if r.get('status') == 'success']
        self._log(f"[*] Successful decryptions: {len(successful)}", Colors.GREEN)
        self._log(f"{'=' * 60}\n", Colors.CYAN)
        return all_results

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all analysis results"""
        total = len(self.results)
        successful = len([r for r in self.results if r.get('status') == 'success'])
        failed = len([r for r in self.results if r.get('status') == 'failed'])
        attack_types = {}
        for r in self.results:
            atype = r.get('attack_type', 'unknown')
            if atype not in attack_types:
                attack_types[atype] = {'total': 0, 'success': 0, 'failed': 0}
            attack_types[atype]['total'] += 1
            status = r.get('status', 'unknown')
            if status == 'success':
                attack_types[atype]['success'] += 1
            elif status == 'failed':
                attack_types[atype]['failed'] += 1
        return {
            'total_results': total,
            'successful': successful,
            'failed': failed,
            'attack_types': attack_types,
            'pycrypto_available': self._pycrypto_available,
        }


def crypto_test() -> None:
    """Test the CryptoBreaker functionality"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}")
    print(f"  CryptoBreaker Test Suite")
    print(f"{'=' * 60}{Colors.RESET}\n")
    breaker = CryptoBreaker(config={'verbose': True})
    print(f"{Colors.GREEN}[*] CryptoBreaker initialized{Colors.RESET}")
    print(f"{Colors.GREEN}[*] pycryptodome available: {PYCRYPTO_AVAILABLE}{Colors.RESET}\n")
    test_plaintext = b"This is a secret message for testing purposes only! 12345"
    print(f"{Colors.YELLOW}[*] Test plaintext: {test_plaintext}{Colors.RESET}\n")
    if PYCRYPTO_AVAILABLE:
        test_key = b'0123456789abcdef'
        cipher = AES.new(test_key, AES.MODE_ECB)
        padded = test_plaintext + b'\x00' * (16 - len(test_plaintext) % 16)
        encrypted = cipher.encrypt(padded[:64])
        print(f"{Colors.YELLOW}[*] Encrypted test data ({len(encrypted)} bytes){Colors.RESET}")
        print(f"{Colors.YELLOW}[*] Key: {test_key.hex()}{Colors.RESET}\n")
        print(f"{Colors.BOLD}{Colors.MAGENTA}--- AES Attack Test ---{Colors.RESET}")
        aes_results = breaker.aes_attack(encrypted)
        print(f"{Colors.GREEN}[*] AES results: {len(aes_results)}{Colors.RESET}\n")
        print(f"{Colors.BOLD}{Colors.MAGENTA}--- DES Attack Test ---{Colors.RESET}")
        des_results = breaker.des_attack(encrypted)
        print(f"{Colors.GREEN}[*] DES results: {len(des_results)}{Colors.RESET}\n")
        print(f"{Colors.BOLD}{Colors.MAGENTA}--- Cipher Mode Detection ---{Colors.RESET}")
        mode = breaker.detect_cipher_mode(encrypted)
        print(f"{Colors.GREEN}[*] Detected mode: {mode}{Colors.RESET}\n")
    else:
        print(f"{Colors.YELLOW}[!] pycryptodome not available - running limited tests{Colors.RESET}\n")
        dummy_data = b'A' * 64
        print(f"{Colors.BOLD}{Colors.MAGENTA}--- RSA Pattern Test ---{Colors.RESET}")
        rsa_data = b'-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8PbnGy0AHB7MhgHcTz6sE2I2yPB\n-----END RSA PRIVATE KEY-----'
        rsa_results = breaker.rsa_attack(rsa_data)
        print(f"{Colors.GREEN}[*] RSA results: {len(rsa_results)}{Colors.RESET}\n")
    print(f"{Colors.BOLD}{Colors.MAGENTA}--- Summary ---{Colors.RESET}")
    summary = breaker.get_summary()
    print(f"{Colors.GREEN}[*] Total results: {summary['total_results']}{Colors.RESET}")
    print(f"{Colors.GREEN}[*] Successful: {summary['successful']}{Colors.RESET}")
    print(f"{Colors.GREEN}[*] Failed: {summary['failed']}{Colors.RESET}")
    print(f"{Colors.GREEN}[*] Attack types: {list(summary['attack_types'].keys())}{Colors.RESET}")
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}")
    print(f"  Tests Complete")
    print(f"{'=' * 60}{Colors.RESET}\n")


if __name__ == '__main__':
    crypto_test()
