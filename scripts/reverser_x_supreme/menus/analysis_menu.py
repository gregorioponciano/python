#!/usr/bin/env python3
"""Analysis Menu Module"""

from typing import Dict, Any, List, Optional
from utils.constants import Colors, MAGIC_NUMBERS
from utils.helpers import calculate_entropy, is_printable, find_repeating_patterns, hexdump, print_analysis
from core import AdvancedAnalyzer


class AnalysisMenu:
    """Interactive analysis menu for binary data inspection"""

    def __init__(self, config=None):
        """Initialize analysis menu with optional configuration"""
        self.config = config or {}
        self.analyzer = None
        self.results = {}

    def run(self, data: bytes) -> Dict[str, Any]:
        """Run analysis menu and return results"""
        while True:
            self._print_header("Analysis Menu")
            print(f"{Colors.CYAN}1. Full Analysis{Colors.RESET}")
            print(f"{Colors.CYAN}2. Statistical Analysis{Colors.RESET}")
            print(f"{Colors.CYAN}3. Pattern Detection{Colors.RESET}")
            print(f"{Colors.CYAN}4. Entropy Analysis{Colors.RESET}")
            print(f"{Colors.CYAN}5. String Search{Colors.RESET}")
            print(f"{Colors.CYAN}6. Magic Number Detection{Colors.RESET}")
            print(f"{Colors.CYAN}7. Structure Detection{Colors.RESET}")
            print(f"{Colors.CYAN}8. Hexdump View{Colors.RESET}")
            print(f"{Colors.CYAN}9. Compare Analysis{Colors.RESET}")
            print(f"{Colors.RED}0. Exit{Colors.RESET}")

            choice = input(f"\n{Colors.YELLOW}[>] Select option: {Colors.RESET}").strip()

            if choice == "0":
                break
            elif choice == "1":
                self.results = self.full_analysis(data)
            elif choice == "2":
                self.results = self.statistical_analysis(data)
            elif choice == "3":
                self.results = self.pattern_detection(data)
            elif choice == "4":
                self.results = self.entropy_analysis(data)
            elif choice == "5":
                self.results = {"strings_found": self.string_search(data)}
            elif choice == "6":
                self.results = {"magic_numbers": self.magic_number_detection(data)}
            elif choice == "7":
                self.results = {"structures": self.structure_detection(data)}
            elif choice == "8":
                try:
                    offset = int(input(f"{Colors.YELLOW}[>] Offset (default 0): {Colors.RESET}") or "0")
                    length = int(input(f"{Colors.YELLOW}[>] Length (default 256): {Colors.RESET}") or "256")
                except ValueError:
                    print(f"{Colors.RED}Invalid input{Colors.RESET}")
                    continue
                self.hexdump_view(data, offset, length)
            elif choice == "9":
                try:
                    file2 = input(f"{Colors.YELLOW}[>] Path to second file: {Colors.RESET}").strip()
                    with open(file2, "rb") as f:
                        data2 = f.read()
                    self.results = self.compare_analysis(data, data2)
                except FileNotFoundError:
                    print(f"{Colors.RED}File not found{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.RED}Error: {e}{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid option{Colors.RESET}")

            if self.results:
                input(f"\n{Colors.YELLOW}[Press Enter to continue]{Colors.RESET}")

        return self.results

    def _print_header(self, title: str) -> None:
        """Print formatted header"""
        width = 50
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'=' * width}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{title.center(width)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'=' * width}{Colors.RESET}\n")

    def full_analysis(self, data: bytes) -> Dict[str, Any]:
        """Perform comprehensive analysis on data"""
        self._print_header("Full Analysis")

        results = {
            "size": len(data),
            "statistics": self.statistical_analysis(data),
            "patterns": self.pattern_detection(data),
            "entropy": self.entropy_analysis(data),
            "strings": self.string_search(data),
            "magic": self.magic_number_detection(data),
            "structures": self.structure_detection(data),
        }

        print(f"{Colors.CYAN}Size: {Colors.WHITE}{len(data)} bytes{Colors.RESET} | Entropy: {Colors.WHITE}{results['entropy']['overall']:.4f}{Colors.RESET}")
        print(f"{Colors.CYAN}Printable: {Colors.WHITE}{results['statistics']['printable_ratio']:.2%}{Colors.RESET} | Strings: {Colors.WHITE}{len(results['strings'])}{Colors.RESET}")
        print(f"{Colors.CYAN}Magic: {Colors.WHITE}{len(results['magic'])}{Colors.RESET} | Structures: {Colors.WHITE}{len(results['structures'])}{Colors.RESET}")

        if results["patterns"]["repeating"]:
            print(f"\n{Colors.YELLOW}Repeating patterns:{Colors.RESET}")
            for p in results["patterns"]["repeating"][:5]:
                print(f"  {Colors.WHITE}{p['pattern'][:40]}{Colors.RESET} x{p['count']}")

        print_analysis(results)
        return results

    def statistical_analysis(self, data: bytes) -> Dict[str, Any]:
        """Perform statistical analysis on data"""
        self._print_header("Statistical Analysis")

        if not data:
            return {"error": "Empty data"}

        byte_counts = [0] * 256
        for b in data:
            byte_counts[b] += 1

        most_common = sorted(range(256), key=lambda x: byte_counts[x], reverse=True)[:10]
        least_common = sorted(range(256), key=lambda x: byte_counts[x])[:10]

        printable_count = sum(1 for b in data if 32 <= b <= 126 or b in (9, 10, 13))
        printable_ratio = printable_count / len(data)
        zero_count = byte_counts[0]
        null_ratio = zero_count / len(data)
        mean_val = sum(data) / len(data)
        std_dev = (sum((b - mean_val) ** 2 for b in data) / len(data)) ** 0.5

        results = {
            "size": len(data),
            "printable_count": printable_count,
            "printable_ratio": printable_ratio,
            "null_count": zero_count,
            "null_ratio": null_ratio,
            "unique_bytes": sum(1 for c in byte_counts if c > 0),
            "most_common": [(hex(b), byte_counts[b]) for b in most_common],
            "least_common": [(hex(b), byte_counts[b]) for b in least_common],
            "mean_value": mean_val,
            "std_dev": std_dev,
        }

        print(f"{Colors.CYAN}Total bytes: {Colors.WHITE}{len(data)}{Colors.RESET}")
        print(f"{Colors.CYAN}Unique byte values: {Colors.WHITE}{results['unique_bytes']}/256{Colors.RESET}")
        print(f"{Colors.CYAN}Printable: {Colors.WHITE}{printable_count} ({printable_ratio:.2%}){Colors.RESET}")
        print(f"{Colors.CYAN}Null bytes: {Colors.WHITE}{zero_count} ({null_ratio:.2%}){Colors.RESET}")
        print(f"{Colors.CYAN}Mean: {Colors.WHITE}{mean_val:.2f}{Colors.RESET} | Std dev: {Colors.WHITE}{std_dev:.2f}{Colors.RESET}")

        print(f"\n{Colors.YELLOW}Most common bytes:{Colors.RESET}")
        for b, c in results["most_common"]:
            bar = "#" * min(c // max(len(data) // 100, 1), 40)
            print(f"  {Colors.WHITE}{b}: {c} {bar}{Colors.RESET}")

        return results

    def pattern_detection(self, data: bytes) -> Dict[str, Any]:
        """Detect patterns in data"""
        self._print_header("Pattern Detection")

        repeating = find_repeating_patterns(data)

        runs = []
        if len(data) > 1:
            current_run = 1
            for i in range(1, len(data)):
                if data[i] == data[i - 1]:
                    current_run += 1
                else:
                    if current_run > 3:
                        runs.append({"byte": hex(data[i - 1]), "length": current_run, "offset": i - current_run})
                    current_run = 1
            if current_run > 3:
                runs.append({"byte": hex(data[-1]), "length": current_run, "offset": len(data) - current_run})

        results = {
            "repeating": repeating,
            "runs": runs,
            "has_xor_pattern": self._detect_xor_pattern(data),
            "has_padding": any(r["length"] > 16 for r in runs),
        }

        print(f"{Colors.CYAN}Repeating patterns: {Colors.WHITE}{len(repeating)}{Colors.RESET}")
        for p in repeating[:10]:
            print(f"  {Colors.WHITE}{p['pattern'][:50]}{Colors.RESET} (len={p['length']}, count={p['count']})")

        print(f"\n{Colors.CYAN}Byte runs (>3): {Colors.WHITE}{len(runs)}{Colors.RESET}")
        for r in runs[:10]:
            print(f"  {Colors.WHITE}{r['byte']} x{r['length']} at offset {r['offset']}{Colors.RESET}")

        print(f"\n{Colors.CYAN}XOR pattern: {Colors.WHITE}{results['has_xor_pattern']}{Colors.RESET}")
        print(f"{Colors.CYAN}Has padding: {Colors.WHITE}{results['has_padding']}{Colors.RESET}")

        return results

    def _detect_xor_pattern(self, data: bytes) -> bool:
        """Detect potential XOR encryption pattern"""
        if len(data) < 32:
            return False
        chunks = [data[i:i + 16] for i in range(0, min(len(data), 256), 16)]
        if len(chunks) < 2:
            return False
        similarities = [sum(1 for a, b in zip(chunks[i], chunks[i + 1]) if a == b) / 16 for i in range(len(chunks) - 1)]
        return sum(similarities) / len(similarities) > 0.5

    def entropy_analysis(self, data: bytes) -> Dict[str, Any]:
        """Analyze entropy of data"""
        self._print_header("Entropy Analysis")

        if not data:
            return {"overall": 0.0, "blocks": []}

        overall_entropy = calculate_entropy(data)
        block_size = 256
        blocks = []
        for i in range(0, len(data), block_size):
            block = data[i:i + block_size]
            blocks.append({"offset": i, "entropy": calculate_entropy(block), "size": len(block)})

        max_e = max((b["entropy"] for b in blocks), default=0)
        min_e = min((b["entropy"] for b in blocks), default=0)
        avg_e = sum(b["entropy"] for b in blocks) / len(blocks) if blocks else 0

        results = {
            "overall": overall_entropy,
            "blocks": blocks,
            "max": max_e,
            "min": min_e,
            "average": avg_e,
            "is_encrypted": overall_entropy > 7.5,
            "is_compressed": overall_entropy > 7.0,
        }

        print(f"{Colors.CYAN}Overall entropy: {Colors.WHITE}{overall_entropy:.4f}/8.0{Colors.RESET}")
        print(f"{Colors.CYAN}Range: {Colors.WHITE}{min_e:.4f} - {max_e:.4f}{Colors.RESET} | Avg: {Colors.WHITE}{avg_e:.4f}{Colors.RESET}")

        if results["is_encrypted"]:
            print(f"\n{Colors.RED}[!] Data appears encrypted (entropy > 7.5){Colors.RESET}")
        elif results["is_compressed"]:
            print(f"\n{Colors.YELLOW}[!] Data appears compressed (entropy > 7.0){Colors.RESET}")
        else:
            print(f"\n{Colors.GREEN}[+] Data appears plaintext or structured{Colors.RESET}")

        print(f"\n{Colors.YELLOW}Entropy by block:{Colors.RESET}")
        for b in blocks[:20]:
            bar = "#" * int(b["entropy"] * 5)
            color = Colors.RED if b["entropy"] > 7.5 else Colors.YELLOW if b["entropy"] > 7.0 else Colors.GREEN
            print(f"  {Colors.WHITE}0x{b['offset']:06x}: {b['entropy']:.4f} {color}{bar}{Colors.RESET}")

        return results

    def string_search(self, data: bytes) -> List[str]:
        """Search for printable strings in data"""
        self._print_header("String Search")

        strings = []
        current = bytearray()

        for b in data:
            if 32 <= b <= 126 or b in (9, 10, 13):
                current.append(b)
            else:
                if len(current) >= 4:
                    try:
                        strings.append(current.decode("ascii", errors="ignore"))
                    except Exception:
                        pass
                current = bytearray()

        if len(current) >= 4:
            try:
                strings.append(current.decode("ascii", errors="ignore"))
            except Exception:
                pass

        print(f"{Colors.CYAN}Strings found: {Colors.WHITE}{len(strings)}{Colors.RESET}")
        for s in strings[:30]:
            print(f"  {Colors.WHITE}{s}{Colors.RESET}")

        return strings

    def magic_number_detection(self, data: bytes) -> List[Dict[str, Any]]:
        """Detect magic numbers in data"""
        self._print_header("Magic Number Detection")

        detected = []
        for magic, file_type in MAGIC_NUMBERS.items():
            offset = data.find(magic)
            if offset != -1:
                detected.append({"type": file_type, "offset": offset, "magic": magic.hex()})

        print(f"{Colors.CYAN}Checked: {Colors.WHITE}{len(MAGIC_NUMBERS)}{Colors.RESET} | Found: {Colors.WHITE}{len(detected)}{Colors.RESET}")
        if detected:
            for d in detected:
                print(f"  {Colors.CYAN}{d['type']}{Colors.RESET} at {d['offset']} ({d['magic']})")
        else:
            print(f"\n{Colors.YELLOW}No known magic numbers detected{Colors.RESET}")

        return detected

    def structure_detection(self, data: bytes) -> List[Dict[str, Any]]:
        """Detect known structures in data"""
        self._print_header("Structure Detection")

        structures = []
        signatures = {
            b"PE\x00\x00": "PE Header",
            b"\x7fELF": "ELF Header",
            b"SQLite format 3": "SQLite Database",
            b"%PDF": "PDF Document",
            b"<?xml": "XML Data",
        }
        for sig, name in signatures.items():
            pos = data.find(sig)
            if pos != -1:
                structures.append({"type": name, "offset": pos})

        for sig in [b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf", b"\xca\xfe\xba\xbe"]:
            pos = data.find(sig)
            if pos != -1:
                structures.append({"type": "Mach-O Header", "offset": pos})
                break

        zip_entries = []
        start = 0
        while True:
            pos = data.find(b"PK\x03\x04", start)
            if pos == -1:
                break
            zip_entries.append(pos)
            start = pos + 4
        if zip_entries:
            structures.append({"type": "ZIP Entries", "offset": zip_entries[0], "count": len(zip_entries)})

        for pattern in [b"<html", b"<HTML", b"<!DOCTYPE", b"<head", b"<body"]:
            pos = data.find(pattern)
            if pos != -1:
                structures.append({"type": "HTML Content", "offset": pos})
                break

        for pattern in [b"{\"", b"[\n  {", b"[\r\n  {"]:
            pos = data.find(pattern)
            if pos != -1:
                structures.append({"type": "JSON Data", "offset": pos})
                break

        print(f"{Colors.CYAN}Structures found: {Colors.WHITE}{len(structures)}{Colors.RESET}")
        for s in structures:
            extra = f" ({s.get('count', 1)} entries)" if "count" in s else ""
            print(f"  {Colors.CYAN}{s['type']}{Colors.RESET} at offset {s['offset']}{extra}")

        return structures

    def hexdump_view(self, data: bytes, offset: int = 0, length: int = 256) -> None:
        """Display hexdump of data"""
        self._print_header("Hexdump View")

        end = min(offset + length, len(data))
        view_data = data[offset:end]

        print(f"{Colors.CYAN}Offset: {Colors.WHITE}0x{offset:08x}{Colors.RESET}")
        print(f"{Colors.CYAN}Length: {Colors.WHITE}{len(view_data)} bytes{Colors.RESET}\n")

        dump = hexdump(view_data, offset=offset)
        print(dump)

    def compare_analysis(self, data1: bytes, data2: bytes) -> Dict[str, Any]:
        """Compare two data samples"""
        self._print_header("Compare Analysis")

        size1, size2 = len(data1), len(data2)
        entropy1, entropy2 = calculate_entropy(data1), calculate_entropy(data2)

        common_prefix = 0
        for a, b in zip(data1, data2):
            if a == b:
                common_prefix += 1
            else:
                break

        min_len = min(size1, size2)
        matching_bytes = sum(1 for a, b in zip(data1, data2) if a == b)
        similarity = matching_bytes / min_len if min_len > 0 else 0

        results = {
            "size1": size1,
            "size2": size2,
            "size_diff": size2 - size1,
            "entropy1": entropy1,
            "entropy2": entropy2,
            "common_prefix": common_prefix,
            "matching_bytes": matching_bytes,
            "similarity": similarity,
            "identical": data1 == data2,
        }

        print(f"{Colors.CYAN}Size: {Colors.WHITE}{size1} vs {size2} (diff: {size2 - size1:+d}){Colors.RESET}")
        print(f"{Colors.CYAN}Entropy: {Colors.WHITE}{entropy1:.4f} vs {entropy2:.4f}{Colors.RESET}")
        print(f"{Colors.CYAN}Common prefix: {Colors.WHITE}{common_prefix}{Colors.RESET} | Similarity: {Colors.WHITE}{similarity:.2%}{Colors.RESET}")

        if results["identical"]:
            print(f"\n{Colors.GREEN}[+] Files are identical{Colors.RESET}")
        elif similarity > 0.9:
            print(f"\n{Colors.YELLOW}[!] Files are very similar{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}[-] Files differ significantly{Colors.RESET}")

        return results
