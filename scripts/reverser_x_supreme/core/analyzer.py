#!/usr/bin/env python3
"""Advanced binary file analyzer with pattern detection and statistical analysis"""

import re
import struct
import math
import zipfile
import io
from dataclasses import dataclass
from typing import List, Dict, Any
from collections import Counter

from utils.constants import Colors, MAGIC_NUMBERS
from utils.helpers import calculate_entropy, is_printable, find_repeating_patterns


@dataclass
class DetectedString:
    """Represents a detected string in binary data"""
    value: str
    offset: int
    length: int
    encoding: str
    entropy: float


@dataclass
class DetectedPattern:
    """Represents a detected pattern in binary data"""
    pattern_type: str
    offset: int
    length: int
    confidence: float
    description: str
    raw_data: bytes = b''


class AdvancedAnalyzer:
    """Advanced binary file analyzer with comprehensive pattern detection"""

    def __init__(self, data: bytes, filename: str = ''):
        self.data = data
        self.filename = filename
        self.file_size = len(data)
        self.detected_strings: List[DetectedString] = []
        self.detected_patterns: List[DetectedPattern] = []
        self.metadata: Dict[str, Any] = {}
        self.anomalies: List[str] = []
        self.file_type: str = 'Unknown'
        self._init_patterns()

    def _init_patterns(self):
        """Initialize pattern signatures for detection"""
        self.string_patterns = [
            re.compile(rb'[\x20-\x7e]{4,}'),
            re.compile(rb'(?:https?://[^\x00-\x1f\x22\x27\x3c\x3e\s]{4,})'),
            re.compile(rb'(?:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'),
            re.compile(rb'(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'),
            re.compile(rb'(?:[0-9a-fA-F]{32})'),
            re.compile(rb'(?:[0-9a-fA-F]{40})'),
            re.compile(rb'(?:BEGIN\s+(?:RSA\s+)?(?:PUBLIC|PRIVATE)\s+KEY)'),
            re.compile(rb'(?:AKIA[0-9A-Z]{16})'),
        ]
        self.interesting_strings = [
            b'password', b'passwd', b'secret', b'api_key', b'api_secret',
            b'token', b'auth', b'login', b'username', b'admin', b'root',
            b'key', b'certificate', b'private', b'encrypt', b'decrypt',
            b'cipher', b'hash', b'md5', b'sha1', b'sha256', b'aes', b'rsa',
            b'HTTP/', b'User-Agent', b'Content-Type', b'POST', b'GET',
            b'cmd.exe', b'powershell', b'/bin/sh', b'/bin/bash',
            b'eval(', b'exec(', b'system(', b'CreateProcess',
        ]

    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive analysis of binary data"""
        result = {
            'filename': self.filename,
            'basic_info': self._basic_info(),
            'entropy_analysis': self._entropy_analysis(),
            'magic_numbers': self._detect_magic_numbers(),
            'strings': self._extract_strings(),
            'patterns': self._find_patterns(),
            'structures': self._detect_structures(),
            'statistical': self._statistical_analysis(),
            'metadata': self._extract_metadata(),
            'anomalies': self._detect_anomalies(),
        }
        if result['magic_numbers']:
            self.file_type = result['magic_numbers'][0].get('type', 'Unknown')
        if self.file_type.startswith('PE'):
            result['pe_analysis'] = self._analyze_pe()
        elif self.file_type.startswith('ELF'):
            result['elf_analysis'] = self._analyze_elf()
        elif 'ZIP' in self.file_type:
            result['zip_analysis'] = self._analyze_zip()
        elif self.file_type.startswith('PDF'):
            result['pdf_analysis'] = self._analyze_pdf()
        return result

    def _basic_info(self) -> Dict[str, Any]:
        """Extract basic file information"""
        byte_freq = Counter(self.data)
        unique_bytes = len(byte_freq)
        most_common = byte_freq.most_common(5)
        null_count = byte_freq.get(0, 0)
        null_ratio = null_count / self.file_size if self.file_size > 0 else 0
        return {
            'file_size': self.file_size,
            'formatted_size': self._format_size(self.file_size),
            'unique_bytes': unique_bytes,
            'byte_diversity': unique_bytes / 256.0,
            'null_bytes': null_count,
            'null_ratio': null_ratio,
            'most_common_bytes': [{'byte': f'0x{b:02x}', 'count': c} for b, c in most_common],
            'is_empty': self.file_size == 0,
        }

    def _format_size(self, size: int) -> str:
        """Format file size to human readable string"""
        if size < 1024:
            return f'{size} B'
        elif size < 1024 ** 2:
            return f'{size / 1024:.2f} KB'
        elif size < 1024 ** 3:
            return f'{size / (1024 ** 2):.2f} MB'
        return f'{size / (1024 ** 3):.2f} GB'

    def _entropy_analysis(self) -> Dict[str, Any]:
        """Perform entropy analysis on the file"""
        total_entropy = calculate_entropy(self.data)
        chunk_size = 256
        chunk_entropies = []
        for i in range(0, len(self.data), chunk_size):
            chunk = self.data[i:i + chunk_size]
            if len(chunk) >= 16:
                chunk_entropies.append(calculate_entropy(chunk))
        high_entropy_regions = []
        if chunk_entropies:
            for idx, ent in enumerate(chunk_entropies):
                if ent > 7.0:
                    high_entropy_regions.append({
                        'offset': idx * chunk_size,
                        'entropy': round(ent, 4),
                        'size': chunk_size,
                    })
        sections = []
        if len(self.data) >= 4096:
            num_sections = min(8, max(2, len(self.data) // 4096))
            section_size = len(self.data) // num_sections
            for i in range(num_sections):
                start = i * section_size
                end = start + section_size if i < num_sections - 1 else len(self.data)
                section_data = self.data[start:end]
                sections.append({
                    'name': f'section_{i}',
                    'offset': start,
                    'size': len(section_data),
                    'entropy': round(calculate_entropy(section_data), 4),
                })
        return {
            'total_entropy': round(total_entropy, 4),
            'avg_chunk_entropy': round(sum(chunk_entropies) / len(chunk_entropies), 4) if chunk_entropies else 0,
            'max_chunk_entropy': round(max(chunk_entropies), 4) if chunk_entropies else 0,
            'min_chunk_entropy': round(min(chunk_entropies), 4) if chunk_entropies else 0,
            'high_entropy_regions': high_entropy_regions[:20],
            'sections': sections,
            'is_packed': total_entropy > 7.5,
            'is_encrypted': total_entropy > 7.8,
            'is_compressed': total_entropy > 7.0,
        }

    def _detect_magic_numbers(self) -> List[Dict[str, Any]]:
        """Detect magic numbers at the beginning of the file"""
        results = []
        for magic, file_type in MAGIC_NUMBERS.items():
            if isinstance(magic, str):
                magic = magic.encode('latin-1')
            if self.data[:len(magic)] == magic:
                results.append({'magic': magic.hex(), 'type': file_type, 'offset': 0, 'confidence': 1.0})
                break
        for magic, file_type in MAGIC_NUMBERS.items():
            if isinstance(magic, str):
                magic = magic.encode('latin-1')
            if len(magic) < 4:
                continue
            offset = self.data.find(magic, 4)
            if offset != -1:
                results.append({'magic': magic.hex(), 'type': file_type, 'offset': offset, 'confidence': 0.7})
        return results

    def _extract_strings(self, min_length: int = 4) -> List[Dict[str, Any]]:
        """Extract printable strings from binary data"""
        self.detected_strings = []
        ascii_pattern = re.compile(rb'[\x20-\x7e]{' + str(min_length).encode() + rb',}')
        unicode_pattern = re.compile(rb'(?:[\x20-\x7e]\x00){' + str(min_length).encode() + rb',}')
        for match in ascii_pattern.finditer(self.data):
            value = match.group().decode('ascii', errors='replace')
            entropy = calculate_entropy(match.group())
            self.detected_strings.append(DetectedString(
                value=value, offset=match.start(), length=len(match.group()),
                encoding='ascii', entropy=round(entropy, 4),
            ))
        for match in unicode_pattern.finditer(self.data):
            try:
                value = match.group().decode('utf-16-le', errors='replace').rstrip('\x00')
                if len(value) >= min_length:
                    entropy = calculate_entropy(match.group())
                    self.detected_strings.append(DetectedString(
                        value=value, offset=match.start(), length=len(match.group()),
                        encoding='utf-16-le', entropy=round(entropy, 4),
                    ))
            except (UnicodeDecodeError, ValueError):
                continue
        self.detected_strings.sort(key=lambda s: s.offset)
        return [{'value': s.value, 'offset': s.offset, 'length': s.length,
                 'encoding': s.encoding, 'entropy': s.entropy} for s in self.detected_strings[:500]]

    def _find_patterns(self) -> List[Dict[str, Any]]:
        """Find interesting patterns in the binary data"""
        self.detected_patterns = []
        for pattern in self.string_patterns:
            for match in pattern.finditer(self.data):
                matched = match.group()
                if b'http' in matched.lower():
                    pattern_type = 'url'
                elif b'@' in matched:
                    pattern_type = 'email'
                elif re.match(rb'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', matched):
                    pattern_type = 'ip_address'
                elif re.match(rb'[0-9a-fA-F]{32}$', matched):
                    pattern_type = 'hash_md5'
                elif re.match(rb'[0-9a-fA-F]{40}$', matched):
                    pattern_type = 'hash_sha1'
                elif re.match(rb'[A-Za-z0-9+/=]{20,}$', matched):
                    pattern_type = 'base64'
                elif b'BEGIN' in matched:
                    pattern_type = 'key_material'
                elif matched.startswith(b'AKIA') or matched.startswith(b'sk-'):
                    pattern_type = 'api_key'
                else:
                    pattern_type = 'string'
                confidence = 0.9 if pattern_type in ('url', 'email', 'hash_md5', 'hash_sha1') else 0.6
                self.detected_patterns.append(DetectedPattern(
                    pattern_type=pattern_type, offset=match.start(), length=len(matched),
                    confidence=confidence, description=f'Detected {pattern_type} pattern',
                    raw_data=matched[:64],
                ))
        for interesting in self.interesting_strings:
            offset = 0
            while True:
                offset = self.data.find(interesting, offset)
                if offset == -1:
                    break
                self.detected_patterns.append(DetectedPattern(
                    pattern_type='interesting_string', offset=offset, length=len(interesting),
                    confidence=0.8, description=f'Found interesting string: {interesting.decode("ascii", errors="replace")}',
                    raw_data=interesting,
                ))
                offset += 1
        repeating = find_repeating_patterns(self.data)
        for pattern, count in list(repeating.items())[:50]:
            self.detected_patterns.append(DetectedPattern(
                pattern_type='repeating_sequence', offset=self.data.find(pattern),
                length=len(pattern), confidence=min(0.5 + count * 0.1, 1.0),
                description=f'Repeating pattern: {pattern[:16].hex()} (x{count})',
                raw_data=pattern[:32],
            ))
        self.detected_patterns.sort(key=lambda p: p.offset)
        return [{'type': p.pattern_type, 'offset': p.offset, 'length': p.length,
                 'confidence': p.confidence, 'description': p.description} for p in self.detected_patterns[:200]]

    def _detect_structures(self) -> Dict[str, Any]:
        """Detect known data structures in the binary"""
        structures = {'headers': [], 'tables': [], 'compressed_blocks': [], 'encrypted_blocks': []}
        for magic, file_type in MAGIC_NUMBERS.items():
            if isinstance(magic, str):
                magic = magic.encode('latin-1')
            offset = 0
            while True:
                offset = self.data.find(magic, offset)
                if offset == -1:
                    break
                structures['headers'].append({'type': file_type, 'offset': offset, 'magic': magic.hex()})
                offset += 1
        chunk_size = 512
        for i in range(0, len(self.data), chunk_size):
            chunk = self.data[i:i + chunk_size]
            if len(chunk) < 64:
                continue
            ent = calculate_entropy(chunk)
            if ent > 7.8:
                structures['encrypted_blocks'].append({'offset': i, 'size': len(chunk), 'entropy': round(ent, 4)})
            elif ent > 7.0:
                structures['compressed_blocks'].append({'offset': i, 'size': len(chunk), 'entropy': round(ent, 4)})
        return structures

    def _analyze_pe(self) -> Dict[str, Any]:
        """Analyze PE (Portable Executable) file structure"""
        result = {'valid': False, 'dos_header': {}, 'nt_headers': {}, 'sections': [], 'imports': [], 'exports': [], 'warnings': []}
        if len(self.data) < 64:
            result['warnings'].append('File too small for PE header')
            return result
        if self.data[:2] != b'MZ':
            result['warnings'].append('Missing MZ signature')
            return result
        try:
            e_lfanew = struct.unpack_from('<I', self.data, 0x3C)[0]
            result['dos_header'] = {'signature': 'MZ', 'e_lfanew': e_lfanew}
        except struct.error:
            result['warnings'].append('Failed to read e_lfanew')
            return result
        if e_lfanew >= len(self.data) or e_lfanew < 64:
            result['warnings'].append(f'Invalid e_lfanew: {e_lfanew}')
            return result
        try:
            pe_sig = self.data[e_lfanew:e_lfanew + 4]
            if pe_sig != b'PE\x00\x00':
                result['warnings'].append(f'Invalid PE signature: {pe_sig.hex()}')
                return result
            result['valid'] = True
            coff_offset = e_lfanew + 4
            machine, num_sections, timestamp, _, _, opt_header_size, characteristics = \
                struct.unpack_from('<HHIIIHH', self.data, coff_offset)
            machine_names = {0x14c: 'x86', 0x8664: 'x64', 0x1c0: 'ARM', 0xaa64: 'ARM64'}
            result['nt_headers'] = {
                'machine': machine_names.get(machine, f'Unknown(0x{machine:x})'),
                'num_sections': num_sections, 'timestamp': timestamp,
                'characteristics': characteristics, 'is_dll': bool(characteristics & 0x2000),
                'is_32bit': opt_header_size == 224, 'is_64bit': opt_header_size == 240,
            }
            opt_header_offset = coff_offset + 20
            if opt_header_size >= 16:
                magic = struct.unpack_from('<H', self.data, opt_header_offset)[0]
                if magic == 0x10b:
                    entry_point = struct.unpack_from('<I', self.data, opt_header_offset + 16)[0]
                    image_base = struct.unpack_from('<I', self.data, opt_header_offset + 28)[0]
                elif magic == 0x20b:
                    entry_point = struct.unpack_from('<I', self.data, opt_header_offset + 16)[0]
                    image_base = struct.unpack_from('<Q', self.data, opt_header_offset + 24)[0]
                else:
                    entry_point = 0
                    image_base = 0
                result['nt_headers']['entry_point'] = f'0x{entry_point:x}'
                result['nt_headers']['image_base'] = f'0x{image_base:x}'
            section_offset = opt_header_offset + opt_header_size
            for i in range(min(num_sections, 96)):
                sec_data = self.data[section_offset + i * 40: section_offset + (i + 1) * 40]
                if len(sec_data) < 40:
                    break
                name = sec_data[:8].rstrip(b'\x00').decode('ascii', errors='replace')
                virt_size, virt_addr, raw_size, raw_ptr, _, _, _, _, chars = \
                    struct.unpack_from('<IIIIIIHHI', sec_data, 8)
                section_entropy = 0.0
                if raw_size > 0 and raw_ptr + raw_size <= len(self.data):
                    section_data = self.data[raw_ptr:raw_ptr + raw_size]
                    section_entropy = calculate_entropy(section_data)
                result['sections'].append({
                    'name': name, 'virtual_size': virt_size, 'virtual_address': f'0x{virt_addr:x}',
                    'raw_size': raw_size, 'raw_pointer': raw_ptr, 'entropy': round(section_entropy, 4),
                    'is_executable': bool(chars & 0x20000000), 'is_writable': bool(chars & 0x80000000),
                    'is_readable': bool(chars & 0x40000000),
                })
                if section_entropy > 7.5:
                    result['warnings'].append(f'Section {name} has high entropy ({section_entropy:.2f}) - possibly packed')
        except struct.error as e:
            result['warnings'].append(f'Error parsing PE headers: {e}')
        return result

    def _analyze_elf(self) -> Dict[str, Any]:
        """Analyze ELF (Executable and Linkable Format) file structure"""
        result = {'valid': False, 'header': {}, 'sections': [], 'warnings': []}
        if len(self.data) < 16:
            result['warnings'].append('File too small for ELF header')
            return result
        if self.data[:4] != b'\x7fELF':
            result['warnings'].append('Missing ELF magic number')
            return result
        try:
            ei_class = self.data[4]
            ei_data = self.data[5]
            is_64 = ei_class == 2
            is_le = ei_data == 1
            if is_64:
                if len(self.data) < 64:
                    result['warnings'].append('File too small for ELF64 header')
                    return result
                e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = \
                    struct.unpack_from('<HHIQQQIHHHHHH', self.data, 16)
            else:
                if len(self.data) < 52:
                    result['warnings'].append('File too small for ELF32 header')
                    return result
                e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = \
                    struct.unpack_from('<HHIIIIIHHHHHH', self.data, 16)
            type_names = {1: 'REL', 2: 'EXEC', 3: 'DYN', 4: 'CORE'}
            machine_names = {3: 'x86', 0x3e: 'x64', 0x28: 'ARM', 0xb7: 'AARCH64', 0x8: 'MIPS'}
            result['valid'] = True
            result['header'] = {
                'class': 'ELF64' if is_64 else 'ELF32', 'endian': 'Little' if is_le else 'Big',
                'type': type_names.get(e_type, f'Unknown(0x{e_type:x})'),
                'machine': machine_names.get(e_machine, f'Unknown(0x{e_machine:x})'),
                'entry_point': f'0x{e_entry:x}', 'program_headers': e_phnum,
                'section_headers': e_shnum, 'flags': e_flags,
            }
        except struct.error as e:
            result['warnings'].append(f'Error parsing ELF header: {e}')
        return result

    def _analyze_zip(self) -> Dict[str, Any]:
        """Analyze ZIP archive contents"""
        result = {'valid': False, 'files': [], 'total_files': 0, 'total_size': 0, 'compressed_size': 0, 'warnings': []}
        try:
            with zipfile.ZipFile(io.BytesIO(self.data)) as zf:
                result['valid'] = True
                bad_files = zf.testzip()
                if bad_files:
                    result['warnings'].append(f'Corrupted file in archive: {bad_files}')
                for info in zf.infolist():
                    result['files'].append({
                        'filename': info.filename, 'compressed_size': info.compress_size,
                        'uncompressed_size': info.file_size, 'compress_type': info.compress_type,
                        'crc': f'{info.CRC:08x}', 'is_dir': info.is_dir(),
                    })
                    result['total_size'] += info.file_size
                    result['compressed_size'] += info.compress_size
                result['total_files'] = len(zf.infolist())
        except zipfile.BadZipFile:
            result['warnings'].append('Invalid or corrupted ZIP file')
        except Exception as e:
            result['warnings'].append(f'Error reading ZIP: {e}')
        return result

    def _analyze_pdf(self) -> Dict[str, Any]:
        """Analyze PDF document structure"""
        result = {'valid': False, 'version': '', 'pages': 0, 'objects': 0,
                  'has_javascript': False, 'has_embedded_files': False, 'has_forms': False, 'warnings': []}
        try:
            header_match = re.match(rb'%PDF-(\d\.\d)', self.data[:20])
            if not header_match:
                result['warnings'].append('Invalid PDF header')
                return result
            result['valid'] = True
            result['version'] = header_match.group(1).decode('ascii')
            result['objects'] = len(re.findall(rb'\d+\s+\d+\s+obj', self.data))
            if b'/Count' in self.data:
                count_matches = re.findall(rb'/Count\s+(\d+)', self.data)
                if count_matches:
                    result['pages'] = int(count_matches[-1])
            if b'/JavaScript' in self.data or b'/JS ' in self.data:
                result['has_javascript'] = True
                result['warnings'].append('PDF contains JavaScript')
            if b'/EmbeddedFile' in self.data:
                result['has_embedded_files'] = True
                result['warnings'].append('PDF contains embedded files')
            if b'/AcroForm' in self.data:
                result['has_forms'] = True
        except Exception as e:
            result['warnings'].append(f'Error analyzing PDF: {e}')
        return result

    def _statistical_analysis(self) -> Dict[str, Any]:
        """Perform statistical analysis on the binary data"""
        if self.file_size == 0:
            return {'error': 'Empty file'}
        byte_counts = Counter(self.data)
        chi_squared = 0.0
        expected = self.file_size / 256.0
        for b in range(256):
            observed = byte_counts.get(b, 0)
            chi_squared += (observed - expected) ** 2 / expected if expected > 0 else 0
        mean_val = sum(b * byte_counts.get(b, 0) for b in range(256)) / self.file_size
        variance = sum((b - mean_val) ** 2 * byte_counts.get(b, 0) for b in range(256)) / self.file_size
        std_dev = math.sqrt(variance) if variance > 0 else 0
        printable_count = sum(1 for b in self.data if 32 <= b <= 126 or b in (9, 10, 13))
        printable_ratio = printable_count / self.file_size
        ascii_count = sum(1 for b in self.data if 32 <= b <= 126)
        control_count = sum(1 for b in self.data if 0 <= b < 32 and b not in (9, 10, 13))
        high_bit_count = sum(1 for b in self.data if b >= 128)
        transitions = sum(1 for i in range(1, len(self.data)) if self.data[i] != self.data[i - 1])
        transition_ratio = transitions / (len(self.data) - 1) if len(self.data) > 1 else 0
        return {
            'chi_squared': round(chi_squared, 4),
            'chi_squared_normalized': round(chi_squared / self.file_size, 6),
            'mean': round(mean_val, 4), 'std_dev': round(std_dev, 4),
            'printable_ratio': round(printable_ratio, 4),
            'ascii_ratio': round(ascii_count / self.file_size, 4),
            'control_chars_ratio': round(control_count / self.file_size, 4),
            'high_bit_ratio': round(high_bit_count / self.file_size, 4),
            'transition_ratio': round(transition_ratio, 4),
            'is_random_like': chi_squared / self.file_size < 0.01,
            'is_text_like': printable_ratio > 0.8,
            'is_binary_like': printable_ratio < 0.3,
        }

    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract metadata from the binary data"""
        metadata = {
            'file_size': self.file_size, 'file_type': self.file_type,
            'timestamp': None, 'compiler': None, 'architecture': None,
            'os_target': None, 'languages': [], 'frameworks': [],
        }
        strings_text = ' '.join(s.value for s in self.detected_strings[:1000])
        for name, pattern in [
            ('GCC', r'GCC:?\s*\(?[\d.]+\)?'), ('Clang', r'(?:clang|LLVM)[\s-]?[\d.]*'),
            ('MSVC', r'Microsoft\s+\(R\)\s+(?:Incremental\s+)?Linker'), ('MinGW', r'MinGW'),
        ]:
            if re.search(pattern, strings_text, re.IGNORECASE):
                metadata['compiler'] = name
                break
        for name, pattern in [
            ('x86', r'(?i)(?:i[3-6]86|x86|i486|i586)'), ('x86_64', r'(?i)(?:x86[-_]?64|x64|amd64)'),
            ('ARM', r'(?i)(?:armv?\d+)'), ('AARCH64', r'(?i)(?:aarch64|arm64)'),
        ]:
            if re.search(pattern, strings_text):
                metadata['architecture'] = name
                break
        for name, pattern in [
            ('Windows', r'(?i)(?:windows|win32|win64|\.dll|\.exe|kernel32|msvcrt)'),
            ('Linux', r'(?i)(?:linux|libc\.so|libm\.so|/usr/)'),
            ('macOS', r'(?i)(?:darwin|macos|\.dylib|\.framework)'),
        ]:
            if re.search(pattern, strings_text):
                metadata['os_target'] = name
                break
        for name, pattern in [
            ('C', r'(?i)(?:printf|scanf|malloc|free|strcpy|strlen)'),
            ('C++', r'(?i)(?:std::|cout|cin|new\s|delete\s|namespace\s)'),
            ('Python', r'(?i)(?:\.pyc|Py_Initialize|PyRun_)'),
            ('Java', r'(?i)(?:Ljava/lang/|\.class|public\s+class\s+)'),
            ('Go', r'(?i)(?:runtime\.|main\.main|go\.)'),
            ('Rust', r'(?i)(?:rust_begin_unwind|std::panicking)'),
        ]:
            if re.search(pattern, strings_text):
                metadata['languages'].append(name)
        for name, pattern in [
            ('Qt', r'(?i)(?:Qt[A-Z]|QWidget|QMainWindow)'), ('OpenSSL', r'(?i)(?:OpenSSL|SSL_CTX|EVP_)'),
            ('zlib', r'(?i)(?:zlib|deflate|inflate)'), ('SQLite', r'(?i)(?:sqlite3_)'),
        ]:
            if re.search(pattern, strings_text):
                metadata['frameworks'].append(name)
        self.metadata = metadata
        return metadata

    def _detect_anomalies(self) -> List[str]:
        """Detect anomalies in the binary data"""
        anomalies = []
        if self.file_size == 0:
            anomalies.append('File is empty')
            return anomalies
        entropy = calculate_entropy(self.data)
        if entropy > 7.8:
            anomalies.append(f'Very high entropy ({entropy:.2f}) - likely encrypted or compressed')
        elif entropy < 1.0 and self.file_size > 100:
            anomalies.append(f'Very low entropy ({entropy:.2f}) - possibly all zeros or repeating data')
        byte_counts = Counter(self.data)
        null_ratio = byte_counts.get(0, 0) / self.file_size
        if null_ratio > 0.9:
            anomalies.append(f'File is {null_ratio * 100:.1f}% null bytes')
        if self.data[:2] == b'MZ':
            try:
                e_lfanew = struct.unpack_from('<I', self.data, 0x3C)[0]
                if e_lfanew > self.file_size:
                    anomalies.append(f'PE e_lfanew ({e_lfanew}) exceeds file size')
                elif e_lfanew < 64:
                    anomalies.append(f'Unusually small e_lfanew ({e_lfanew})')
            except struct.error:
                anomalies.append('Failed to read PE header offset')
        if self.file_size > 1024:
            first_kb_entropy = calculate_entropy(self.data[:1024])
            last_kb_entropy = calculate_entropy(self.data[-1024:])
            if abs(first_kb_entropy - last_kb_entropy) > 2.0:
                anomalies.append(f'Significant entropy difference between start ({first_kb_entropy:.2f}) and end ({last_kb_entropy:.2f})')
        repeating = find_repeating_patterns(self.data)
        if len(repeating) > 10:
            anomalies.append(f'Found {len(repeating)} repeating patterns - possible padding or obfuscation')
        printable_count = sum(1 for b in self.data if 32 <= b <= 126 or b in (9, 10, 13))
        printable_ratio = printable_count / self.file_size
        if 0.3 < printable_ratio < 0.5 and entropy > 6.0:
            anomalies.append('Mixed binary/text content - possible shell script or packed payload')
        self.anomalies = anomalies
        return anomalies

    def quick_scan(self) -> Dict[str, Any]:
        """Perform a quick scan with minimal analysis"""
        magic = self._detect_magic_numbers()
        file_type = magic[0]['type'] if magic else 'Unknown'
        entropy = calculate_entropy(self.data)
        strings = self._extract_strings(min_length=6)
        return {
            'filename': self.filename, 'size': self.file_size,
            'formatted_size': self._format_size(self.file_size),
            'type': file_type, 'entropy': round(entropy, 4),
            'is_packed': entropy > 7.5, 'string_count': len(strings),
            'top_strings': [s['value'][:80] for s in strings[:10]],
            'has_anomalies': len(self._detect_anomalies()) > 0,
        }


def test_analyzer():
    """Test the AdvancedAnalyzer with sample data"""
    print(f'{Colors.BOLD}=== AdvancedAnalyzer Test ==={Colors.RESET}\n')
    pe_data = b'MZ' + b'\x00' * 56 + struct.pack('<I', 128) + b'\x00' * 60 + b'PE\x00\x00' + b'\x00' * 200
    analyzer = AdvancedAnalyzer(pe_data, 'test.exe')
    result = analyzer.analyze()
    print(f'{Colors.CYAN}File: {result["filename"]}{Colors.RESET}')
    print(f'{Colors.CYAN}Size: {result["basic_info"]["formatted_size"]}{Colors.RESET}')
    print(f'{Colors.CYAN}Type: {result["basic_info"]["formatted_size"]}{Colors.RESET}')
    print(f'{Colors.YELLOW}Entropy: {result["entropy_analysis"]["total_entropy"]}{Colors.RESET}')
    print(f'{Colors.YELLOW}Magic Numbers: {len(result["magic_numbers"])}{Colors.RESET}')
    print(f'{Colors.YELLOW}Strings Found: {len(result["strings"])}{Colors.RESET}')
    print(f'{Colors.YELLOW}Patterns Found: {len(result["patterns"])}{Colors.RESET}')
    print(f'{Colors.YELLOW}Anomalies: {len(result["anomalies"])}{Colors.RESET}')
    if result.get('pe_analysis'):
        pe = result['pe_analysis']
        print(f'\n{Colors.GREEN}PE Analysis:{Colors.RESET}')
        print(f'  Valid: {pe["valid"]}')
        print(f'  Sections: {len(pe["sections"])}')
        print(f'  Warnings: {len(pe["warnings"])}')
    print(f'\n{Colors.GREEN}Quick Scan:{Colors.RESET}')
    quick = analyzer.quick_scan()
    for key, value in quick.items():
        print(f'  {key}: {value}')
    print(f'\n{Colors.BOLD}=== Test Complete ==={Colors.RESET}')


if __name__ == '__main__':
    test_analyzer()
