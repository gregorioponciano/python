import string
from typing import List, Dict, Any, Optional, Tuple

from utils.constants import Colors, XOR_MAX_KEY_SIZE
from utils.helpers import calculate_entropy, xor_bytes


class XORAttackEngine:
    ENGLISH_FREQ = {
        'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253,
        'e': 0.12702, 'f': 0.02228, 'g': 0.02015, 'h': 0.06094,
        'i': 0.06966, 'j': 0.00153, 'k': 0.00772, 'l': 0.04025,
        'm': 0.02406, 'n': 0.06749, 'o': 0.07507, 'p': 0.01929,
        'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056,
        'u': 0.02758, 'v': 0.00978, 'w': 0.02360, 'x': 0.00150,
        'y': 0.01974, 'z': 0.00074,
    }

    def __init__(self, config=None):
        self.config = config or {}
        self.max_key_size = self.config.get('max_key_size', XOR_MAX_KEY_SIZE)
        self.min_printable_ratio = self.config.get('min_printable_ratio', 0.7)

    def single_byte_xor(self, data: bytes) -> List[Dict[str, Any]]:
        results = []
        for key in range(256):
            decrypted = xor_bytes(data, bytes([key]))
            printable_count = sum(1 for b in decrypted if 32 <= b < 127 or b in (9, 10, 13))
            printable_ratio = printable_count / len(data) if data else 0
            score = self._score_english(decrypted)
            entropy = calculate_entropy(decrypted)
            results.append({
                'key': bytes([key]),
                'key_hex': f'0x{key:02x}',
                'decrypted': decrypted,
                'printable_ratio': printable_ratio,
                'score': score,
                'entropy': entropy,
            })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def _score_english(self, data: bytes) -> float:
        if not data:
            return 0.0
        text = data.lower().decode('ascii', errors='ignore')
        total_chars = sum(1 for c in text if c.isalpha())
        if total_chars == 0:
            return 0.0
        chi_square = 0.0
        for letter, expected_freq in self.ENGLISH_FREQ.items():
            observed = text.count(letter)
            expected = expected_freq * total_chars
            chi_square += ((observed - expected) ** 2) / expected if expected > 0 else 0
        printable_ratio = sum(1 for b in data if 32 <= b < 127 or b in (9, 10, 13)) / len(data)
        space_ratio = text.count(' ') / len(text) if text else 0
        space_bonus = 0.0
        if 0.1 <= space_ratio <= 0.25:
            space_bonus = 50.0
        elif 0.05 <= space_ratio <= 0.3:
            space_bonus = 20.0
        common_words = [b'the', b'and', b'is', b'in', b'it', b'of', b'to', b'a', b'for', b'on']
        word_bonus = 0.0
        for word in common_words:
            count = text.count(word.decode())
            word_bonus += count * 10.0
        score = max(0, 1000 - chi_square) + space_bonus + word_bonus
        score *= printable_ratio
        return score

    def multi_byte_xor(self, data: bytes, key_size: int = None) -> List[Dict[str, Any]]:
        results = []
        key_sizes = [key_size] if key_size else range(2, min(self.max_key_size + 1, len(data) // 2 + 1))
        for ks in key_sizes:
            if ks < 2 or ks > len(data) // 2:
                continue
            key = self._break_multi_byte_key(data, ks)
            if key is None:
                continue
            decrypted = xor_bytes(data, key)
            printable_count = sum(1 for b in decrypted if 32 <= b < 127 or b in (9, 10, 13))
            printable_ratio = printable_count / len(data) if data else 0
            score = self._score_english(decrypted)
            entropy = calculate_entropy(decrypted)
            results.append({
                'key': key,
                'key_hex': key.hex(),
                'key_size': ks,
                'decrypted': decrypted,
                'printable_ratio': printable_ratio,
                'score': score,
                'entropy': entropy,
            })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def _break_multi_byte_key(self, data: bytes, key_size: int) -> Optional[bytes]:
        key_bytes = []
        for offset in range(key_size):
            block = data[offset::key_size]
            if not block:
                return None
            best_key_byte = 0
            best_score = float('-inf')
            for k in range(256):
                decrypted = xor_bytes(block, bytes([k]))
                score = self._score_english(decrypted)
                if score > best_score:
                    best_score = score
                    best_key_byte = k
            key_bytes.append(best_key_byte)
        return bytes(key_bytes)

    def rolling_xor(self, data: bytes, key_size: int = None) -> List[Dict[str, Any]]:
        results = []
        key_sizes = [key_size] if key_size else range(2, min(self.max_key_size + 1, len(data) // 2 + 1))
        for ks in key_sizes:
            if ks < 2 or ks > len(data) // 2:
                continue
            best_result = None
            best_score = float('-inf')
            for offset in range(ks):
                block = data[offset::ks]
                block_results = self.single_byte_xor(block)
                if not block_results:
                    continue
                key_byte = block_results[0]['key'][0]
                if best_result is None:
                    best_result = {'key_bytes': [], 'block_scores': []}
                best_result['key_bytes'].append(key_byte)
                best_result['block_scores'].append(block_results[0]['score'])
            if best_result is None:
                continue
            key = bytes(best_result['key_bytes'])
            decrypted = self._apply_rolling_xor(data, key)
            printable_count = sum(1 for b in decrypted if 32 <= b < 127 or b in (9, 10, 13))
            printable_ratio = printable_count / len(data) if data else 0
            score = self._score_english(decrypted)
            entropy = calculate_entropy(decrypted)
            results.append({
                'key': key,
                'key_hex': key.hex(),
                'key_size': ks,
                'decrypted': decrypted,
                'printable_ratio': printable_ratio,
                'score': score,
                'entropy': entropy,
            })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def _apply_rolling_xor(self, data: bytes, key: bytes) -> bytes:
        result = bytearray(len(data))
        key_len = len(key)
        for i in range(len(data)):
            result[i] = data[i] ^ key[i % key_len]
        return bytes(result)

    def hamming_distance(self, data: bytes, key_size: int) -> float:
        if key_size * 2 > len(data):
            return float('inf')
        total_distance = 0
        num_blocks = 0
        for i in range(0, len(data) - key_size * 2, key_size):
            block1 = data[i:i + key_size]
            block2 = data[i + key_size:i + key_size * 2]
            xored = xor_bytes(block1, block2)
            distance = sum(bin(b).count('1') for b in xored)
            total_distance += distance
            num_blocks += 1
        if num_blocks == 0:
            return float('inf')
        return total_distance / num_blocks / key_size

    def guess_key_size(self, data: bytes) -> List[int]:
        max_size = min(self.max_key_size, len(data) // 4)
        if max_size < 2:
            return [1]
        distances = {}
        for ks in range(2, max_size + 1):
            distances[ks] = self.hamming_distance(data, ks)
        sorted_sizes = sorted(distances.keys(), key=lambda k: distances[k])
        return sorted_sizes

    def brute_force_xor(self, data: bytes, charset: str = None, max_key_size: int = 4) -> List[Dict[str, Any]]:
        results = []
        if charset is None:
            charset = string.printable[:62]
        charset_bytes = [ord(c) for c in charset]
        effective_max = min(max_key_size, self.max_key_size, len(data) // 2)
        for ks in range(1, effective_max + 1):
            if ks == 1:
                for k in range(256):
                    key = bytes([k])
                    decrypted = xor_bytes(data, key)
                    printable_ratio = sum(1 for b in decrypted if 32 <= b < 127 or b in (9, 10, 13)) / len(data) if data else 0
                    if printable_ratio < self.min_printable_ratio:
                        continue
                    score = self._score_english(decrypted)
                    entropy = calculate_entropy(decrypted)
                    results.append({
                        'key': key,
                        'key_hex': key.hex(),
                        'key_size': ks,
                        'decrypted': decrypted,
                        'printable_ratio': printable_ratio,
                        'score': score,
                        'entropy': entropy,
                    })
            else:
                from itertools import product
                for key_tuple in product(charset_bytes, repeat=ks):
                    key = bytes(key_tuple)
                    decrypted = xor_bytes(data, key)
                    printable_ratio = sum(1 for b in decrypted if 32 <= b < 127 or b in (9, 10, 13)) / len(data) if data else 0
                    if printable_ratio < self.min_printable_ratio:
                        continue
                    score = self._score_english(decrypted)
                    if score < 50:
                        continue
                    entropy = calculate_entropy(decrypted)
                    results.append({
                        'key': key,
                        'key_hex': key.hex(),
                        'key_size': ks,
                        'decrypted': decrypted,
                        'printable_ratio': printable_ratio,
                        'score': score,
                        'entropy': entropy,
                    })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def known_plaintext_xor(self, ciphertext: bytes, plaintext: bytes) -> Optional[bytes]:
        if len(plaintext) > len(ciphertext):
            return None
        key = xor_bytes(ciphertext[:len(plaintext)], plaintext)
        if len(key) == 0:
            return None
        test_decrypt = xor_bytes(ciphertext, key)
        printable_ratio = sum(1 for b in test_decrypt if 32 <= b < 127 or b in (9, 10, 13)) / len(ciphertext) if ciphertext else 0
        if printable_ratio >= self.min_printable_ratio:
            return key
        return None

    def crib_dragging_xor(self, data: bytes, cribs: List[bytes]) -> List[Dict[str, Any]]:
        results = []
        for crib in cribs:
            if len(crib) > len(data):
                continue
            for offset in range(len(data) - len(crib) + 1):
                key_candidate = xor_bytes(data[offset:offset + len(crib)], crib)
                decrypted = xor_bytes(data, key_candidate)
                printable_ratio = sum(1 for b in decrypted if 32 <= b < 127 or b in (9, 10, 13)) / len(data) if data else 0
                score = self._score_english(decrypted)
                results.append({
                    'crib': crib,
                    'offset': offset,
                    'key': key_candidate,
                    'key_hex': key_candidate.hex(),
                    'decrypted': decrypted,
                    'printable_ratio': printable_ratio,
                    'score': score,
                })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def full_attack(self, data: bytes) -> List[Dict[str, Any]]:
        all_results = []
        single_results = self.single_byte_xor(data)
        for r in single_results[:5]:
            r['attack_type'] = 'single_byte_xor'
            all_results.append(r)
        key_sizes = self.guess_key_size(data)
        for ks in key_sizes[:3]:
            multi_results = self.multi_byte_xor(data, ks)
            for r in multi_results[:3]:
                r['attack_type'] = 'multi_byte_xor'
                all_results.append(r)
        for ks in key_sizes[:3]:
            rolling_results = self.rolling_xor(data, ks)
            for r in rolling_results[:3]:
                r['attack_type'] = 'rolling_xor'
                all_results.append(r)
        bf_results = self.brute_force_xor(data, max_key_size=min(3, self.max_key_size))
        for r in bf_results[:5]:
            r['attack_type'] = 'brute_force_xor'
            all_results.append(r)
        all_results.sort(key=lambda x: x['score'], reverse=True)
        seen = set()
        unique_results = []
        for r in all_results:
            key_hex = r.get('key_hex', '')
            if key_hex not in seen:
                seen.add(key_hex)
                unique_results.append(r)
        return unique_results

    def analyze_xor_pattern(self, data: bytes) -> Dict[str, Any]:
        if not data:
            return {'error': 'Empty data'}
        entropy = calculate_entropy(data)
        repeating_patterns = self._find_repeating_xor_patterns(data)
        key_sizes = self.guess_key_size(data)
        single_results = self.single_byte_xor(data)
        best_single = single_results[0] if single_results else None
        printable_ratio = sum(1 for b in data if 32 <= b < 127 or b in (9, 10, 13)) / len(data) if data else 0
        byte_freq = {}
        for b in data:
            byte_freq[b] = byte_freq.get(b, 0) + 1
        most_common_byte = max(byte_freq, key=byte_freq.get) if byte_freq else None
        most_common_freq = byte_freq.get(most_common_byte, 0) / len(data) if data else 0
        analysis = {
            'data_length': len(data),
            'entropy': entropy,
            'printable_ratio': printable_ratio,
            'most_common_byte': most_common_byte,
            'most_common_byte_hex': f'0x{most_common_byte:02x}' if most_common_byte is not None else None,
            'most_common_byte_frequency': most_common_freq,
            'likely_key_sizes': key_sizes[:5],
            'repeating_patterns': repeating_patterns[:10],
            'has_repeating_pattern': len(repeating_patterns) > 0,
            'best_single_byte_key': best_single['key_hex'] if best_single else None,
            'best_single_byte_score': best_single['score'] if best_single else 0,
            'is_likely_xor_encrypted': (
                entropy > 4.0
                and printable_ratio < 0.5
                and most_common_freq > 0.05
            ),
        }
        return analysis

    def _find_repeating_xor_patterns(self, data: bytes, min_gap: int = 4) -> List[Tuple[int, int]]:
        patterns = []
        max_pattern_len = min(16, len(data) // 3)
        for pattern_len in range(2, max_pattern_len + 1):
            seen = {}
            for i in range(len(data) - pattern_len + 1):
                pattern = data[i:i + pattern_len]
                if pattern in seen:
                    gap = i - seen[pattern]
                    if gap >= min_gap:
                        patterns.append((seen[pattern], i))
                else:
                    seen[pattern] = i
        patterns.sort(key=lambda x: x[1] - x[0])
        return patterns


def xor_test():
    engine = XORAttackEngine()
    test_plaintext = b'This is a secret message that needs to be hidden from prying eyes.'
    test_key = bytes([0x42])
    ciphertext = xor_bytes(test_plaintext, test_key)
    print(f'{Colors.CYAN}=== Single-Byte XOR Test ==={Colors.RESET}')
    results = engine.single_byte_xor(ciphertext)
    for r in results[:3]:
        print(f"  Key: {r['key_hex']}, Score: {r['score']:.2f}, Printable: {r['printable_ratio']:.2%}")
        print(f"  Decrypted: {r['decrypted']}")
    print()
    multi_key = b'KEY'
    multi_ciphertext = xor_bytes(test_plaintext * 10, multi_key)
    print(f'{Colors.CYAN}=== Multi-Byte XOR Test ==={Colors.RESET}')
    multi_results = engine.multi_byte_xor(multi_ciphertext)
    for r in multi_results[:3]:
        print(f"  Key: {r['key_hex']}, Size: {r['key_size']}, Score: {r['score']:.2f}")
        print(f"  Decrypted: {r['decrypted'][:60]}...")
    print()
    print(f'{Colors.CYAN}=== Key Size Guessing Test ==={Colors.RESET}')
    guessed_sizes = engine.guess_key_size(multi_ciphertext)
    print(f"  Guessed key sizes: {guessed_sizes[:5]}")
    print(f"  Actual key size: {len(multi_key)}")
    print()
    print(f'{Colors.CYAN}=== Known Plaintext XOR Test ==={Colors.RESET}')
    recovered_key = engine.known_plaintext_xor(multi_ciphertext, test_plaintext[:3])
    print(f"  Recovered key prefix: {recovered_key.hex() if recovered_key else 'None'}")
    print()
    print(f'{Colors.CYAN}=== Crib Dragging Test ==={Colors.RESET}')
    crib_results = engine.crib_dragging_xor(multi_ciphertext, [b'secret', b'message'])
    for r in crib_results[:3]:
        print(f"  Crib: {r['crib']}, Offset: {r['offset']}, Score: {r['score']:.2f}")
    print()
    print(f'{Colors.CYAN}=== Pattern Analysis Test ==={Colors.RESET}')
    analysis = engine.analyze_xor_pattern(multi_ciphertext)
    print(f"  Entropy: {analysis['entropy']:.4f}")
    print(f"  Likely key sizes: {analysis['likely_key_sizes']}")
    print(f"  Is likely XOR encrypted: {analysis['is_likely_xor_encrypted']}")
    print()
    print(f'{Colors.CYAN}=== Full Attack Test ==={Colors.RESET}')
    full_results = engine.full_attack(multi_ciphertext)
    for r in full_results[:3]:
        print(f"  Attack: {r.get('attack_type', 'unknown')}, Key: {r['key_hex']}, Score: {r['score']:.2f}")
    print()
    print(f'{Colors.GREEN}All XOR attack tests completed.{Colors.RESET}')


if __name__ == '__main__':
    xor_test()
