#!/usr/bin/env python3
"""Reverser X Supreme - Core Engine Implementation"""

import hashlib
import json
import logging
import os
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from utils.constants import Colors, VERSION, MAX_DEPTH, TIMEOUT_SECONDS, ENTROPY_THRESHOLD, MIN_PRINTABLE_RATIO
from utils.helpers import is_printable, calculate_entropy, run_with_timeout, safe_file_write, setup_logger, print_analysis

from core.analyzer import AdvancedAnalyzer
from core.crypto_breaker import CryptoBreaker
from core.hash_cracker import HashCracker
from core.decompressor import DecompressorEngine
from core.encoder_decoder import EncoderDecoder
from core.xor_attacks import XORAttackEngine


@dataclass
class AnalysisResult:
    """Stores a single analysis result"""
    result_id: str
    task_id: str
    engine: str
    method: str
    data: bytes
    decoded_data: bytes
    score: float
    entropy: float
    printable_ratio: float
    metadata: Dict[str, Any]
    timestamp: float
    success: bool
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'result_id': self.result_id,
            'task_id': self.task_id,
            'engine': self.engine,
            'method': self.method,
            'data_hex': self.data.hex() if self.data else '',
            'decoded_data_hex': self.decoded_data.hex() if self.decoded_data else '',
            'score': self.score,
            'entropy': self.entropy,
            'printable_ratio': self.printable_ratio,
            'metadata': self.metadata,
            'timestamp': self.timestamp,
            'success': self.success,
            'error': self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        return cls(
            result_id=data['result_id'],
            task_id=data['task_id'],
            engine=data['engine'],
            method=data['method'],
            data=bytes.fromhex(data['data_hex']) if data.get('data_hex') else b'',
            decoded_data=bytes.fromhex(data['decoded_data_hex']) if data.get('decoded_data_hex') else b'',
            score=data.get('score', 0.0),
            entropy=data.get('entropy', 0.0),
            printable_ratio=data.get('printable_ratio', 0.0),
            metadata=data.get('metadata', {}),
            timestamp=data.get('timestamp', 0.0),
            success=data.get('success', False),
            error=data.get('error'),
        )


@dataclass
class AnalysisTask:
    """Represents a single analysis task"""
    task_id: str
    data: bytes
    source: str
    depth: int
    priority: int
    methods: List[str]
    created_at: float
    status: str = 'pending'
    result_count: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'data_hex': self.data.hex() if self.data else '',
            'source': self.source,
            'depth': self.depth,
            'priority': self.priority,
            'methods': self.methods,
            'created_at': self.created_at,
            'status': self.status,
            'result_count': self.result_count,
            'error': self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisTask':
        return cls(
            task_id=data['task_id'],
            data=bytes.fromhex(data['data_hex']) if data.get('data_hex') else b'',
            source=data.get('source', 'unknown'),
            depth=data.get('depth', 0),
            priority=data.get('priority', 0),
            methods=data.get('methods', []),
            created_at=data.get('created_at', 0.0),
            status=data.get('status', 'pending'),
            result_count=data.get('result_count', 0),
            error=data.get('error'),
        )


class ReverserEngine:
    """Main engine orchestrating all analysis pipelines"""

    def __init__(
        self,
        max_depth: int = MAX_DEPTH,
        timeout: int = TIMEOUT_SECONDS,
        entropy_threshold: float = ENTROPY_THRESHOLD,
        min_printable_ratio: float = MIN_PRINTABLE_RATIO,
        verbose: bool = True,
        output_dir: str = 'output',
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.max_depth = max_depth
        self.timeout = timeout
        self.entropy_threshold = entropy_threshold
        self.min_printable_ratio = min_printable_ratio
        self.verbose = verbose
        self.output_dir = output_dir
        self.config = config or {}

        if logger:
            self.logger = logger
        else:
            self.logger = setup_logger('ReverserEngine')

        self.task_queue = deque()
        self.results: List[AnalysisResult] = []
        self.processed_hashes: Set[str] = set()
        self.processed_tasks: Set[str] = set()
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.total_tasks: int = 0
        self.completed_tasks: int = 0
        self.failed_tasks: int = 0

        self.analyzer = AdvancedAnalyzer(b'')
        self.crypto_breaker = CryptoBreaker()
        self.hash_cracker = HashCracker()
        self.decompressor = DecompressorEngine()
        self.encoder_decoder = EncoderDecoder()
        self.xor_engine = XORAttackEngine()

        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)

    def _generate_id(self) -> str:
        return uuid.uuid4().hex[:12]

    def _should_process(self, data: bytes) -> bool:
        if not data or len(data) == 0:
            return False
        data_hash = hashlib.md5(data).hexdigest()
        if data_hash in self.processed_hashes:
            return False
        return True

    def _add_result(self, result: AnalysisResult) -> None:
        self.results.append(result)
        if result.decoded_data:
            self.processed_hashes.add(hashlib.md5(result.decoded_data).hexdigest())
        if self.verbose and result.success:
            self.logger.info(
                f"{Colors.GREEN}[RESULT]{Colors.RESET} {result.engine}/{result.method} "
                f"score={result.score:.2f} entropy={result.entropy:.2f}"
            )

    def _add_task(
        self,
        data: bytes,
        source: str = 'manual',
        depth: int = 0,
        priority: int = 0,
        methods: Optional[List[str]] = None,
    ) -> str:
        if not self._should_process(data):
            return ''
        task_id = self._generate_id()
        task = AnalysisTask(
            task_id=task_id,
            data=data,
            source=source,
            depth=depth,
            priority=priority,
            methods=methods or ['all'],
            created_at=time.time(),
        )
        self.task_queue.append(task)
        self.total_tasks += 1
        self.processed_hashes.add(hashlib.md5(data).hexdigest())
        self.logger.debug(f"Added task {task_id} from {source} at depth {depth}")
        return task_id

    def _analyze_data(self, data: bytes) -> Dict[str, Any]:
        analysis = {}
        analysis['length'] = len(data)
        analysis['entropy'] = calculate_entropy(data)
        printable_count = sum(1 for b in data if 32 <= b < 127 or b in (9, 10, 13))
        analysis['printable_ratio'] = printable_count / max(len(data), 1)
        analysis['is_text'] = analysis['printable_ratio'] >= self.min_printable_ratio
        analysis['high_entropy'] = analysis['entropy'] >= self.entropy_threshold
        analysis['md5'] = hashlib.md5(data).hexdigest()
        analysis['sha1'] = hashlib.sha1(data).hexdigest()
        analysis['sha256'] = hashlib.sha256(data).hexdigest()
        return analysis

    def _calculate_score(self, data: bytes, entropy: float, printable_ratio: float) -> float:
        score = 0.0
        if printable_ratio >= 0.9:
            score += 40.0
        elif printable_ratio >= 0.7:
            score += 25.0
        elif printable_ratio >= 0.5:
            score += 10.0

        if entropy < 4.0:
            score += 30.0
        elif entropy < 6.0:
            score += 20.0
        elif entropy < 7.5:
            score += 10.0

        if len(data) > 0:
            score += min(20.0, len(data) / 10.0)

        lower = data.lower()
        for kw in [b'password', b'key', b'secret', b'token', b'flag', b'admin']:
            if kw in lower:
                score += 10.0
                break

        return min(100.0, score)

    def _process_encodings(self, task: AnalysisTask) -> List[AnalysisResult]:
        results = []
        analysis = self._analyze_data(task.data)

        if analysis['is_text']:
            try:
                text = task.data.decode('utf-8', errors='ignore').strip()
            except Exception:
                text = ''

            if text:
                encoded_results = self.encoder_decoder.decode_all(task.data)

                for method, decoded in encoded_results:
                    if decoded and decoded != task.data:
                        decoded_entropy = calculate_entropy(decoded)
                        printable_count = sum(1 for b in decoded if 32 <= b < 127 or b in (9, 10, 13))
                        printable = printable_count / max(len(decoded), 1)
                        score = self._calculate_score(decoded, decoded_entropy, printable)

                        result = AnalysisResult(
                            result_id=self._generate_id(),
                            task_id=task.task_id,
                            engine='EncoderDecoder',
                            method=method,
                            data=task.data,
                            decoded_data=decoded,
                            score=score,
                            entropy=decoded_entropy,
                            printable_ratio=printable,
                            metadata={'method': method},
                            timestamp=time.time(),
                            success=True,
                        )
                        results.append(result)

                        if decoded_entropy < self.entropy_threshold and printable >= self.min_printable_ratio:
                            if task.depth < self.max_depth:
                                self._add_task(
                                    data=decoded,
                                    source=f"encoding:{method}",
                                    depth=task.depth + 1,
                                    priority=task.priority + 1,
                                    methods=task.methods,
                                )
        return results

    def _process_decompression(self, task: AnalysisTask) -> List[AnalysisResult]:
        results = []

        decompression_results = self.decompressor.decompress_all(task.data)

        for method, decompressed in decompression_results:
            if decompressed and len(decompressed) > 0:
                entropy = calculate_entropy(decompressed)
                printable_count = sum(1 for b in decompressed if 32 <= b < 127 or b in (9, 10, 13))
                printable = printable_count / max(len(decompressed), 1)
                score = self._calculate_score(decompressed, entropy, printable)

                result = AnalysisResult(
                    result_id=self._generate_id(),
                    task_id=task.task_id,
                    engine='DecompressorEngine',
                    method=method,
                    data=task.data,
                    decoded_data=decompressed,
                    score=score,
                    entropy=entropy,
                    printable_ratio=printable,
                    metadata={'method': method},
                    timestamp=time.time(),
                    success=True,
                )
                results.append(result)

                if task.depth < self.max_depth:
                    self._add_task(
                        data=decompressed,
                        source=f"decompress:{method}",
                        depth=task.depth + 1,
                        priority=task.priority + 1,
                        methods=task.methods,
                    )
        return results

    def _process_xor_attacks(self, task: AnalysisTask) -> List[AnalysisResult]:
        results = []

        xor_results = self.xor_engine.single_byte_xor(task.data)

        for xor_result in xor_results[:10]:
            key = xor_result.get('key', b'')
            decrypted = xor_result.get('decrypted', b'')

            if decrypted and len(decrypted) > 0:
                entropy = calculate_entropy(decrypted)
                printable = xor_result.get('printable_ratio', 0.0)
                score = xor_result.get('score', 0.0)

                result = AnalysisResult(
                    result_id=self._generate_id(),
                    task_id=task.task_id,
                    engine='XORAttackEngine',
                    method='xor_single_byte',
                    data=task.data,
                    decoded_data=decrypted,
                    score=score,
                    entropy=entropy,
                    printable_ratio=printable,
                    metadata={
                        'key': key.hex() if isinstance(key, bytes) else str(key),
                        'key_hex': xor_result.get('key_hex', ''),
                    },
                    timestamp=time.time(),
                    success=printable >= self.min_printable_ratio,
                )
                results.append(result)

                if printable >= self.min_printable_ratio and task.depth < self.max_depth:
                    self._add_task(
                        data=decrypted,
                        source='xor_decrypt',
                        depth=task.depth + 1,
                        priority=task.priority + 1,
                        methods=task.methods,
                    )
        return results

    def _process_crypto(self, task: AnalysisTask) -> List[AnalysisResult]:
        results = []

        if len(task.data) % 16 == 0:
            aes_results = self.crypto_breaker.aes_attack(task.data)
            if isinstance(aes_results, dict):
                aes_results = [aes_results]
            for aes_result in aes_results:
                if not isinstance(aes_result, dict):
                    continue
                if aes_result.get('error'):
                    continue
                decrypted = aes_result.get('data', b'')
                if decrypted:
                    entropy = calculate_entropy(decrypted)
                    printable_count = sum(1 for b in decrypted if 32 <= b < 127 or b in (9, 10, 13))
                    printable = printable_count / max(len(decrypted), 1)
                    score = self._calculate_score(decrypted, entropy, printable)

                    result = AnalysisResult(
                        result_id=self._generate_id(),
                        task_id=task.task_id,
                        engine='CryptoBreaker',
                        method=f"aes_{aes_result.get('mode', 'unknown')}",
                        data=task.data,
                        decoded_data=decrypted,
                        score=score,
                        entropy=entropy,
                        printable_ratio=printable,
                        metadata={
                            'cipher': 'AES',
                            'mode': aes_result.get('mode', 'unknown'),
                            'key': aes_result.get('key', ''),
                        },
                        timestamp=time.time(),
                        success=True,
                    )
                    results.append(result)

        rsa_results = self.crypto_breaker.rsa_attack(task.data)
        for rsa_result in rsa_results:
            status = rsa_result.get('status', '')
            is_success = status in ('detected', 'parsed', 'base64_detected')
            result = AnalysisResult(
                result_id=self._generate_id(),
                task_id=task.task_id,
                engine='CryptoBreaker',
                method='rsa_detection',
                data=task.data,
                decoded_data=task.data if is_success else b'',
                score=0.8 if is_success else 0.0,
                entropy=calculate_entropy(task.data),
                printable_ratio=0.0,
                metadata=rsa_result,
                timestamp=time.time(),
                success=is_success,
            )
            results.append(result)

        return results

    def _process_hash_detection(self, task: AnalysisTask) -> List[AnalysisResult]:
        results = []
        try:
            text = task.data.decode('ascii', errors='ignore').strip()
            text = ''.join(text.split())
        except Exception:
            return results

        if not text:
            return results

        if not all(c in '0123456789abcdefABCDEF' for c in text):
            return results

        if len(text) not in (32, 40, 56, 64, 96, 128):
            return results

        hash_types = self.hash_cracker.identify_hash(text)

        for hash_type in hash_types:
            cracked = self.hash_cracker.crack_hash(text)

            if cracked:
                decoded_bytes = cracked.encode('utf-8')
                entropy = calculate_entropy(decoded_bytes)
                printable_count = sum(1 for b in decoded_bytes if 32 <= b < 127 or b in (9, 10, 13))
                printable = printable_count / max(len(decoded_bytes), 1)
                score = 100.0

                result = AnalysisResult(
                    result_id=self._generate_id(),
                    task_id=task.task_id,
                    engine='HashCracker',
                    method=f'hash_{hash_type}',
                    data=task.data,
                    decoded_data=decoded_bytes,
                    score=score,
                    entropy=entropy,
                    printable_ratio=printable,
                    metadata={
                        'hash_type': hash_type,
                        'hash_value': text,
                        'plaintext': cracked,
                    },
                    timestamp=time.time(),
                    success=True,
                )
                results.append(result)
            else:
                result = AnalysisResult(
                    result_id=self._generate_id(),
                    task_id=task.task_id,
                    engine='HashCracker',
                    method=f'hash_{hash_type}',
                    data=task.data,
                    decoded_data=b'',
                    score=0.0,
                    entropy=0.0,
                    printable_ratio=0.0,
                    metadata={
                        'hash_type': hash_type,
                        'hash_value': text,
                        'cracked': False,
                    },
                    timestamp=time.time(),
                    success=False,
                    error='Hash not cracked',
                )
                results.append(result)

        return results

    def _process_text_extraction(self, task: AnalysisTask) -> List[AnalysisResult]:
        results = []

        analyzer = AdvancedAnalyzer(task.data)
        strings = analyzer._extract_strings(min_length=4)

        if strings:
            combined = '\n'.join(s['value'] if isinstance(s, dict) else s.value for s in strings)
            decoded_bytes = combined.encode('utf-8')
            entropy = calculate_entropy(decoded_bytes)
            printable = 1.0
            score = self._calculate_score(decoded_bytes, entropy, printable)

            result = AnalysisResult(
                result_id=self._generate_id(),
                task_id=task.task_id,
                engine='AdvancedAnalyzer',
                method='string_extraction',
                data=task.data,
                decoded_data=decoded_bytes,
                score=score,
                entropy=entropy,
                printable_ratio=printable,
                metadata={
                    'string_count': len(strings),
                    'strings': [s['value'] if isinstance(s, dict) else s.value for s in strings[:50]],
                },
                timestamp=time.time(),
                success=True,
            )
            results.append(result)

        language = self._detect_language(task.data)
        if language:
            result = AnalysisResult(
                result_id=self._generate_id(),
                task_id=task.task_id,
                engine='AdvancedAnalyzer',
                method='language_detection',
                data=task.data,
                decoded_data=task.data,
                score=0.5,
                entropy=calculate_entropy(task.data),
                printable_ratio=sum(1 for b in task.data if 32 <= b < 127 or b in (9, 10, 13)) / max(len(task.data), 1),
                metadata={'language': language},
                timestamp=time.time(),
                success=True,
            )
            results.append(result)

        structure = analyzer._detect_structures()
        if structure:
            result = AnalysisResult(
                result_id=self._generate_id(),
                task_id=task.task_id,
                engine='AdvancedAnalyzer',
                method='structure_detection',
                data=task.data,
                decoded_data=task.data,
                score=0.6,
                entropy=calculate_entropy(task.data),
                printable_ratio=sum(1 for b in task.data if 32 <= b < 127 or b in (9, 10, 13)) / max(len(task.data), 1),
                metadata={'structure': structure},
                timestamp=time.time(),
                success=True,
            )
            results.append(result)

        return results

    def _detect_language(self, data: bytes) -> Optional[str]:
        try:
            text = data.decode('utf-8', errors='ignore').lower()
        except Exception:
            return None

        if not text or len(text) < 10:
            return None

        lang_patterns = {
            'english': ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had'],
            'portuguese': ['para', 'com', 'nao', 'uma', 'dos', 'por', 'mais', 'seu', 'sua', 'como'],
            'spanish': ['para', 'con', 'que', 'del', 'por', 'sus', 'como', 'mas', 'son', 'muy'],
            'french': ['pour', 'avec', 'que', 'des', 'pas', 'dans', 'sur', 'plus', 'nous', 'vous'],
            'german': ['und', 'der', 'die', 'das', 'von', 'den', 'dem', 'des', 'ein', 'eine'],
        }

        best_lang = None
        best_score = 0.0

        for lang, patterns in lang_patterns.items():
            score = sum(1 for p in patterns if f' {p} ' in f' {text} ') / len(patterns)
            if score > best_score:
                best_score = score
                best_lang = lang

        return best_lang if best_score > 0.1 else None

    def _process_task(self, task: AnalysisTask) -> List[AnalysisResult]:
        task.status = 'running'
        results = []
        methods = task.methods

        should_run = lambda m: 'all' in methods or m in methods

        try:
            if should_run('encoding'):
                results.extend(self._process_encodings(task))

            if should_run('decompression'):
                results.extend(self._process_decompression(task))

            if should_run('xor'):
                results.extend(self._process_xor_attacks(task))

            if should_run('crypto'):
                results.extend(self._process_crypto(task))

            if should_run('hash'):
                results.extend(self._process_hash_detection(task))

            if should_run('text'):
                results.extend(self._process_text_extraction(task))

        except Exception as e:
            task.status = 'failed'
            task.error = str(e)
            self.failed_tasks += 1
            self.logger.error(f"Task {task.task_id} failed: {e}")
            return results

        task.status = 'completed'
        task.result_count = len(results)
        self.completed_tasks += 1

        for result in results:
            self._add_result(result)

        return results

    def _process_queue(self) -> int:
        processed = 0
        while self.task_queue:
            task = self.task_queue.popleft()

            if task.task_id in self.processed_tasks:
                continue

            self.processed_tasks.add(task.task_id)
            self.logger.info(
                f"{Colors.CYAN}[TASK]{Colors.RESET} Processing {task.task_id} "
                f"(depth={task.depth}, priority={task.priority}, methods={task.methods})"
            )

            task_results = self._process_task(task)
            processed += 1

            if self.verbose:
                print_analysis(task.data, title=f"Task {task.task_id}")

        return processed

    def run_full_analysis(
        self,
        data: bytes,
        source: str = 'manual',
        methods: Optional[List[str]] = None,
    ) -> List[AnalysisResult]:
        self.start_time = time.time()
        self.results = []
        self.task_queue = deque()
        self.processed_hashes = set()
        self.processed_tasks = set()
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0

        self.logger.info(f"{Colors.BOLD}{Colors.MAGENTA}Starting full analysis{Colors.RESET}")
        self.logger.info(f"Data size: {len(data)} bytes, source: {source}")

        initial_task_id = self._add_task(
            data=data,
            source=source,
            depth=0,
            priority=0,
            methods=methods,
        )

        if not initial_task_id:
            self.logger.warning("No task created - data may be empty or already processed")
            return []

        processed = self._process_queue()

        self.end_time = time.time()
        elapsed = self.end_time - self.start_time

        self.logger.info(
            f"{Colors.GREEN}{Colors.BOLD}Analysis complete{Colors.RESET} - "
            f"processed={processed}, results={len(self.results)}, "
            f"elapsed={elapsed:.2f}s"
        )

        return self.results

    def get_best_results(self, top_n: int = 10) -> List[AnalysisResult]:
        successful = [r for r in self.results if r.success]
        sorted_results = sorted(successful, key=lambda r: r.score, reverse=True)
        return sorted_results[:top_n]

    def export_results(self, filepath: Optional[str] = None) -> str:
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(self.output_dir, f'analysis_{timestamp}.json')

        export_data = {
            'version': VERSION,
            'timestamp': datetime.now().isoformat(),
            'summary': self.get_summary(),
            'results': [r.to_dict() for r in self.results],
            'best_results': [r.to_dict() for r in self.get_best_results()],
        }

        content = json.dumps(export_data, indent=2, default=str)
        safe_file_write(filepath, content.encode('utf-8'))
        self.logger.info(f"Results exported to {filepath}")
        return filepath

    def get_summary(self) -> Dict[str, Any]:
        elapsed = (self.end_time - self.start_time) if self.end_time > 0 else 0.0
        successful = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)

        engine_counts: Dict[str, int] = {}
        for r in self.results:
            engine_counts[r.engine] = engine_counts.get(r.engine, 0) + 1

        method_counts: Dict[str, int] = {}
        for r in self.results:
            method_counts[r.method] = method_counts.get(r.method, 0) + 1

        best = self.get_best_results(1)
        best_result = best[0] if best else None

        return {
            'version': VERSION,
            'total_tasks': self.total_tasks,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'total_results': len(self.results),
            'successful_results': successful,
            'failed_results': failed,
            'elapsed_seconds': round(elapsed, 2),
            'engine_counts': engine_counts,
            'method_counts': method_counts,
            'best_result': best_result.to_dict() if best_result else None,
        }


class PipelineManager:
    """Manages multiple engine pipelines for complex analysis workflows"""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.engines: Dict[str, ReverserEngine] = {}
        self.pipeline_order: List[str] = []
        self.pipeline_results: Dict[str, List[AnalysisResult]] = {}
        self.logger = setup_logger('PipelineManager')

    def add_engine(self, name: str, engine: ReverserEngine) -> None:
        self.engines[name] = engine
        if name not in self.pipeline_order:
            self.pipeline_order.append(name)
        self.logger.info(f"Added engine: {name}")

    def remove_engine(self, name: str) -> bool:
        if name in self.engines:
            del self.engines[name]
            if name in self.pipeline_order:
                self.pipeline_order.remove(name)
            self.logger.info(f"Removed engine: {name}")
            return True
        return False

    def set_pipeline_order(self, order: List[str]) -> None:
        valid = [name for name in order if name in self.engines]
        self.pipeline_order = valid
        self.logger.info(f"Pipeline order set: {valid}")

    def run_pipeline(self, data: bytes, source: str = 'pipeline') -> Dict[str, List[AnalysisResult]]:
        self.pipeline_results = {}
        current_data = data

        for engine_name in self.pipeline_order:
            engine = self.engines.get(engine_name)
            if not engine:
                self.logger.warning(f"Engine {engine_name} not found, skipping")
                continue

            self.logger.info(f"{Colors.YELLOW}[PIPELINE]{Colors.RESET} Running {engine_name}")
            results = engine.run_full_analysis(current_data, source=source)
            self.pipeline_results[engine_name] = results

            best = engine.get_best_results(1)
            if best:
                current_data = best[0].decoded_data
                self.logger.info(
                    f"{Colors.GREEN}[PIPELINE]{Colors.RESET} {engine_name} produced best result "
                    f"score={best[0].score:.2f}"
                )

        return self.pipeline_results

    def get_combined_results(self) -> List[AnalysisResult]:
        all_results = []
        for results in self.pipeline_results.values():
            all_results.extend(results)
        return sorted(all_results, key=lambda r: r.score, reverse=True)

    def get_pipeline_summary(self) -> Dict[str, Any]:
        summary = {
            'engines': list(self.engines.keys()),
            'pipeline_order': self.pipeline_order,
            'engine_results': {},
            'combined_count': len(self.get_combined_results()),
        }
        for name, results in self.pipeline_results.items():
            successful = sum(1 for r in results if r.success)
            summary['engine_results'][name] = {
                'total': len(results),
                'successful': successful,
                'best_score': max((r.score for r in results), default=0.0),
            }
        return summary

    def export_pipeline(self, filepath: Optional[str] = None) -> str:
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f'pipeline_{timestamp}.json'

        export_data = {
            'version': VERSION,
            'timestamp': datetime.now().isoformat(),
            'summary': self.get_pipeline_summary(),
            'results': {
                name: [r.to_dict() for r in results]
                for name, results in self.pipeline_results.items()
            },
            'combined': [r.to_dict() for r in self.get_combined_results()],
        }

        content = json.dumps(export_data, indent=2, default=str)
        safe_file_write(filepath, content.encode('utf-8'))
        self.logger.info(f"Pipeline results exported to {filepath}")
        return filepath


def test_engine() -> None:
    """Test function for ReverserEngine"""
    print(f"{Colors.BOLD}{Colors.CYAN}Reverser X Supreme v{VERSION} - Engine Test{Colors.RESET}")
    print()

    engine = ReverserEngine(verbose=True)

    test_data = b'SGVsbG8gV29ybGQh'
    print(f"{Colors.YELLOW}[*]{Colors.RESET} Testing with base64 data: {test_data}")
    results = engine.run_full_analysis(test_data, source='test')
    print(f"{Colors.GREEN}[+]{Colors.RESET} Found {len(results)} results")

    best = engine.get_best_results(3)
    print(f"{Colors.GREEN}[+]{Colors.RESET} Best results:")
    for i, r in enumerate(best):
        print(f"  {i+1}. {r.engine}/{r.method} score={r.score:.2f}")

    summary = engine.get_summary()
    print(f"{Colors.GREEN}[+]{Colors.RESET} Summary:")
    print(f"  Total tasks: {summary['total_tasks']}")
    print(f"  Completed: {summary['completed_tasks']}")
    print(f"  Results: {summary['total_results']}")

    export_path = engine.export_results()
    print(f"{Colors.GREEN}[+]{Colors.RESET} Exported to: {export_path}")

    print()
    print(f"{Colors.GREEN}{Colors.BOLD}[+] Engine test passed!{Colors.RESET}")


if __name__ == '__main__':
    test_engine()
