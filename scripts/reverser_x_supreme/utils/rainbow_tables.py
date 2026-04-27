#!/usr/bin/env python3
"""Gerenciador de tabelas arco-iris para reversao de hashes"""

import os
import json
import hashlib
import time
from typing import Dict, Any, Optional, List
from utils.constants import Colors
from utils.helpers import get_file_hash


class RainbowTableManager:
    """Gerencia geracao, armazenamento e consulta de tabelas arco-iris"""

    def __init__(self, table_dir: str = "rainbow_tables"):
        self.table_dir = table_dir
        self.tables: Dict[str, Dict[str, str]] = {}
        self.chain_lengths: Dict[str, int] = {}
        self.table_metadata: Dict[str, Dict[str, Any]] = {}
        os.makedirs(self.table_dir, exist_ok=True)

    def _hash_function(self, plaintext: str, algorithm: str = "md5") -> str:
        """Calcula o hash de um texto usando o algoritmo especificado"""
        try:
            h = hashlib.new(algorithm)
            h.update(plaintext.encode("utf-8"))
            return h.hexdigest()
        except ValueError:
            return ""

    def reduce_function(self, hash_str: str, length: int) -> str:
        """Funcao R para geracao de tabelas arco-iris"""
        try:
            charset = "0123456789abcdef"
            numeric_value = int(hash_str[:length], 16)
            result = []
            for i in range(length):
                index = (numeric_value + i) % len(charset)
                result.append(charset[index])
            return "".join(result)
        except (ValueError, IndexError):
            return ""

    def generate_table(
        self,
        algorithm: str = "md5",
        charset: str = "0123456789abcdef",
        max_length: int = 6,
    ) -> str:
        """Gera tabela arco-iris e salva em arquivo"""
        try:
            table_name = f"{algorithm}_len{max_length}"
            table_path = os.path.join(self.table_dir, f"{table_name}.json")
            rainbow_table: Dict[str, str] = {}
            chain_count = 0
            start_time = time.time()

            for length in range(1, max_length + 1):
                chains = self._generate_chains(algorithm, charset, length, 1000)
                for start_plain, end_hash in chains:
                    rainbow_table[end_hash] = start_plain
                    chain_count += 1

            elapsed = time.time() - start_time

            metadata = {
                "algorithm": algorithm,
                "charset": charset,
                "max_length": max_length,
                "chain_count": chain_count,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "generation_time": round(elapsed, 2),
            }

            table_data = {"metadata": metadata, "chains": rainbow_table}

            with open(table_path, "w") as f:
                json.dump(table_data, f, indent=2)

            self.tables[table_name] = rainbow_table
            self.chain_lengths[table_name] = chain_count
            self.table_metadata[table_name] = metadata

            print(
                f"{Colors.GREEN}[+] Tabela gerada: {table_path}{Colors.RESET}"
            )
            print(
                f"{Colors.CYAN}    Cadeias: {chain_count} | Tempo: {elapsed:.2f}s{Colors.RESET}"
            )
            return table_path
        except Exception as e:
            print(f"{Colors.RED}[-] Erro ao gerar tabela: {e}{Colors.RESET}")
            return ""

    def _generate_chains(
        self,
        algorithm: str,
        charset: str,
        length: int,
        num_chains: int,
    ) -> List[tuple]:
        """Gera cadeias para a tabela arco-iris"""
        chains = []
        try:
            for i in range(num_chains):
                start_plain = self._generate_start_string(charset, length, i)
                current_hash = self._hash_function(start_plain, algorithm)

                if not current_hash:
                    continue

                for step in range(100):
                    reduced = self.reduce_function(current_hash, length)
                    current_hash = self._hash_function(reduced, algorithm)
                    if not current_hash:
                        break

                chains.append((start_plain, current_hash))
        except Exception:
            pass
        return chains

    def _generate_start_string(
        self, charset: str, length: int, index: int
    ) -> str:
        """Gera string inicial para uma cadeia"""
        try:
            result = []
            charset_len = len(charset)
            for i in range(length):
                char_index = (index // (charset_len**i)) % charset_len
                result.append(charset[char_index])
            return "".join(result)
        except Exception:
            return charset[0] * length

    def load_table(self, table_path: str) -> Dict[str, str]:
        """Carrega tabela arco-iris de arquivo"""
        try:
            if not os.path.exists(table_path):
                print(
                    f"{Colors.RED}[-] Arquivo nao encontrado: {table_path}{Colors.RESET}"
                )
                return {}

            with open(table_path, "r") as f:
                data = json.load(f)

            if "chains" in data:
                chains = data["chains"]
            else:
                chains = data

            table_name = os.path.splitext(os.path.basename(table_path))[0]
            self.tables[table_name] = chains
            self.chain_lengths[table_name] = len(chains)

            if "metadata" in data:
                self.table_metadata[table_name] = data["metadata"]

            print(
                f"{Colors.GREEN}[+] Tabela carregada: {table_path}{Colors.RESET}"
            )
            print(
                f"{Colors.CYAN}    Cadeias: {len(chains)}{Colors.RESET}"
            )
            return chains
        except json.JSONDecodeError as e:
            print(f"{Colors.RED}[-] JSON invalido: {e}{Colors.RESET}")
            return {}
        except Exception as e:
            print(f"{Colors.RED}[-] Erro ao carregar tabela: {e}{Colors.RESET}")
            return {}

    def lookup_hash(self, hash_str: str, table_path: str = None) -> Optional[str]:
        """Consulta um hash na tabela"""
        try:
            if table_path:
                chains = self.load_table(table_path)
            else:
                chains = {}
                for name, table in self.tables.items():
                    chains.update(table)

            if hash_str in chains:
                plaintext = chains[hash_str]
                print(
                    f"{Colors.GREEN}[+] Hash encontrado: {hash_str} -> {plaintext}{Colors.RESET}"
                )
                return plaintext

            for name, table in self.tables.items():
                if hash_str in table:
                    plaintext = table[hash_str]
                    print(
                        f"{Colors.GREEN}[+] Hash encontrado: {hash_str} -> {plaintext}{Colors.RESET}"
                    )
                    return plaintext

            print(
                f"{Colors.YELLOW}[!] Hash nao encontrado: {hash_str}{Colors.RESET}"
            )
            return None
        except Exception as e:
            print(f"{Colors.RED}[-] Erro na consulta: {e}{Colors.RESET}")
            return None

    def chain_length(self) -> int:
        """Retorna o comprimento atual da cadeia"""
        if self.chain_lengths:
            return sum(self.chain_lengths.values())
        return 0

    def export_table(self, table_path: str, format: str = "json") -> bool:
        """Exporta tabela para arquivo"""
        try:
            table_name = os.path.splitext(os.path.basename(table_path))[0]

            if table_name not in self.tables:
                if os.path.exists(table_path):
                    self.load_table(table_path)
                else:
                    print(
                        f"{Colors.RED}[-] Tabela nao encontrada: {table_name}{Colors.RESET}"
                    )
                    return False

            chains = self.tables.get(table_name, {})
            metadata = self.table_metadata.get(table_name, {})

            if format == "json":
                export_data = {"metadata": metadata, "chains": chains}
                with open(table_path, "w") as f:
                    json.dump(export_data, f, indent=2)
            elif format == "csv":
                csv_path = table_path.replace(".json", ".csv")
                with open(csv_path, "w") as f:
                    f.write("end_hash,plaintext\n")
                    for end_hash, plaintext in chains.items():
                        f.write(f"{end_hash},{plaintext}\n")
            else:
                print(
                    f"{Colors.RED}[-] Formato nao suportado: {format}{Colors.RESET}"
                )
                return False

            print(
                f"{Colors.GREEN}[+] Tabela exportada: {table_path}{Colors.RESET}"
            )
            return True
        except Exception as e:
            print(f"{Colors.RED}[-] Erro ao exportar tabela: {e}{Colors.RESET}")
            return False

    def import_table(self, table_path: str) -> bool:
        """Importa tabela de arquivo"""
        try:
            if not os.path.exists(table_path):
                print(
                    f"{Colors.RED}[-] Arquivo nao encontrado: {table_path}{Colors.RESET}"
                )
                return False

            ext = os.path.splitext(table_path)[1].lower()

            if ext == ".json":
                with open(table_path, "r") as f:
                    data = json.load(f)

                if "chains" in data:
                    chains = data["chains"]
                else:
                    chains = data

                if "metadata" in data:
                    metadata = data["metadata"]
                else:
                    metadata = {}

            elif ext == ".csv":
                chains = {}
                metadata = {}
                with open(table_path, "r") as f:
                    header = f.readline()
                    for line in f:
                        line = line.strip()
                        if line:
                            parts = line.split(",", 1)
                            if len(parts) == 2:
                                end_hash, plaintext = parts
                                chains[end_hash] = plaintext
            else:
                print(
                    f"{Colors.RED}[-] Formato nao suportado: {ext}{Colors.RESET}"
                )
                return False

            table_name = os.path.splitext(os.path.basename(table_path))[0]
            self.tables[table_name] = chains
            self.chain_lengths[table_name] = len(chains)
            self.table_metadata[table_name] = metadata

            print(
                f"{Colors.GREEN}[+] Tabela importada: {table_path}{Colors.RESET}"
            )
            print(
                f"{Colors.CYAN}    Cadeias: {len(chains)}{Colors.RESET}"
            )
            return True
        except json.JSONDecodeError as e:
            print(f"{Colors.RED}[-] JSON invalido: {e}{Colors.RESET}")
            return False
        except Exception as e:
            print(f"{Colors.RED}[-] Erro ao importar tabela: {e}{Colors.RESET}")
            return False

    def get_table_info(self, table_path: str) -> Dict[str, Any]:
        """Retorna informacoes sobre uma tabela"""
        try:
            table_name = os.path.splitext(os.path.basename(table_path))[0]

            if table_name in self.table_metadata:
                metadata = self.table_metadata[table_name].copy()
            else:
                metadata = {}

            if os.path.exists(table_path):
                file_size = os.path.getsize(table_path)
                file_hash = get_file_hash(table_path)
                metadata["file_path"] = table_path
                metadata["file_size"] = file_size
                metadata["file_hash"] = file_hash
                metadata["last_modified"] = time.strftime(
                    "%Y-%m-%d %H:%M:%S",
                    time.localtime(os.path.getmtime(table_path)),
                )

            if table_name in self.tables:
                metadata["loaded_chains"] = len(self.tables[table_name])

            if table_name in self.chain_lengths:
                metadata["chain_length"] = self.chain_lengths[table_name]

            return metadata
        except Exception as e:
            print(
                f"{Colors.RED}[-] Erro ao obter informacoes: {e}{Colors.RESET}"
            )
            return {}


def rainbow_test():
    """Teste da tabela arco-iris"""
    print(f"\n{Colors.BOLD}=== Teste de Tabela Arco-Iris ==={Colors.RESET}\n")

    manager = RainbowTableManager()

    print(f"{Colors.CYAN}[*] Gerando tabela de teste...{Colors.RESET}")
    table_path = manager.generate_table(
        algorithm="md5",
        charset="0123456789abcdef",
        max_length=4,
    )

    if table_path:
        print(f"\n{Colors.CYAN}[*] Carregando tabela...{Colors.RESET}")
        chains = manager.load_table(table_path)

        print(f"\n{Colors.CYAN}[*] Comprimento total: {manager.chain_length()}{Colors.RESET}")

        print(f"\n{Colors.CYAN}[*] Consultando hash conhecido...{Colors.RESET}")
        test_hash = manager._hash_function("1234", "md5")
        result = manager.lookup_hash(test_hash, table_path)

        print(f"\n{Colors.CYAN}[*] Informacoes da tabela:{Colors.RESET}")
        info = manager.get_table_info(table_path)
        for key, value in info.items():
            print(f"    {key}: {value}")

        print(f"\n{Colors.CYAN}[*] Exportando tabela...{Colors.RESET}")
        manager.export_table(table_path, format="json")

    print(f"\n{Colors.GREEN}[+] Teste concluido!{Colors.RESET}\n")


if __name__ == "__main__":
    rainbow_test()
